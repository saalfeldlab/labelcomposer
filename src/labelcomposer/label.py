import itertools
import warnings
from typing import FrozenSet, Iterator, Optional, Sequence, Set, TypeVar, Union

from typeguard import CollectionCheckStrategy, check_type, typechecked

from labelcomposer.helpers import StringLike, check_type_bool, convert_to_str

T = TypeVar("T")
AnySet = Union[FrozenSet[T], Set[T]]
CollectionLike = Union[Sequence[T], AnySet[T]]
check_all = CollectionCheckStrategy.ALL_ITEMS


class AtomicLabel:
    @typechecked
    def __init__(self, name: StringLike, index: Union[None, int] = None):
        self.name: str = convert_to_str(name)
        self.index = index

    def __hash__(self) -> int:
        return hash((self.name, self.index))

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, AtomicLabel):
            return False
        return self.name == other.name and self.index == other.index

    def __str__(self) -> str:
        if self.index is None:
            index_add = " (id not set)"
        else:
            index_add = f" ({self.index})"
        return self.name + index_add

    def __repr__(self) -> str:
        return f"AtomicLabel {self!s}"


class Label:
    @typechecked
    def __init__(
        self,
        included: CollectionLike[AtomicLabel],
        name: Optional[StringLike] = None,
    ):
        self.name: Optional[str] = name
        self.included = frozenset(included)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Label):
            return False
        return self.name == other.name and self.included == other.included

    def match(self, other: "Label") -> bool:
        if not isinstance(other, Label):
            return False
        return self.included == other.included

    def __str__(self) -> str:
        return f"Label {self.name}: {self.included}"

    def __repr__(self) -> str:
        return f"Label: name {self.name}, label: {self.included}"

    def __hash__(self) -> int:
        return hash((self.included, self.name))

    def __iter__(self) -> Iterator[AtomicLabel]:
        yield from self.included

    @property
    def name(self) -> Optional[str]:
        return self._name

    @name.setter
    def name(self, name: Optional[StringLike]) -> None:
        check_type(name, Optional[StringLike])
        if name is not None:
            name = convert_to_str(name)
        self._name = name

    def __or__(self, other: "AnyLabelType") -> FrozenSet[AtomicLabel]:
        if isinstance(other, (AtomicLabel)):
            return self.included | {other}
        elif check_type_bool(other, CollectionLike[AtomicLabel]):
            return self.included | set(other)
        elif isinstance(other, Label):
            return self.included | other.included
        else:
            msg = f"unsupported operand type(s) for |: 'Label' and '{type(other).__name__}'"
            raise TypeError(msg)

    def __add__(self, other: "AnyLabelType") -> FrozenSet[AtomicLabel]:
        if not check_type_bool(other, AnyLabelType):
            msg = f"unsupported operand type(s) for +: 'Label' and '{type(other).__name__}'"
            raise TypeError(msg)
        return self | other

    def __sub__(self, other: "AnyLabelType") -> FrozenSet[AtomicLabel]:
        if isinstance(other, AtomicLabel):
            return self.included - {other}
        elif check_type_bool(other, CollectionLike[AtomicLabel]):
            return self.included - set(other)
        elif isinstance(other, Label):
            return self.included - other.included
        else:
            msg = f"unsupported operand type(s) for -: 'Label' and '{type(other).__name__}'"
            raise TypeError(msg)

    def __and__(self, other: "AnyLabelType") -> FrozenSet[AtomicLabel]:
        if isinstance(other, AtomicLabel):
            return self.included - {other}
        elif check_type_bool(other, CollectionLike[AtomicLabel]):
            return self.included & set(other)
        elif isinstance(other, Label):
            return self.included & other.included
        else:
            msg = f"unsupported operand type(s) for &: 'Label' and '{type(other).__name__}"
            raise TypeError(msg)

    def __len__(self) -> int:
        return len(self.included)


def computable(set1: AnySet, set2: AnySet) -> Set[FrozenSet]:
    add = frozenset(set1 | set2)
    sub1 = frozenset(set1 - set2)
    sub2 = frozenset(set2 - set1)
    inters = frozenset(set1 & set2)
    disjoint = frozenset(add - inters)
    return {frozenset(set1), frozenset(set2), add, sub1, sub2, inters, disjoint}


class LabelCollection:
    @typechecked
    def __init__(self, atoms: CollectionLike[AtomicLabel], labels: Optional[CollectionLike[Label]] = None):
        self._atoms: Set[AtomicLabel] = set()
        self._derived_labels: Set[Label] = set()
        self._computable_atoms: Set[AtomicLabel] = set()
        self._computable_sets: Set[FrozenSet[AtomicLabel]] = set()
        self._warn_size = 100
        for atom in atoms:
            self.add_atom(atom)
        if labels is not None:
            for lbl in labels:
                self.add_label(lbl)

    @classmethod
    def empty_like(cls, prototype):
        return cls(prototype.get_atoms())

    def get_computable_atoms(self):
        return self._computable_atoms

    def get_computable_sets(self):
        return self._computable_sets

    def get_derived_labels(self):
        return self._derived_labels

    @typechecked
    def get_label_by_name(self, name: str):
        for lbl in self.get_derived_labels():
            if lbl.name == name:
                return lbl
        msg = f"No Label with name {name} in this LabelCollection."
        raise ValueError(msg)

    def __iter__(self) -> Iterator[Label]:
        names = self.get_names()
        for name in names:
            yield self.get_label_by_name(name)

    def get_names(self):
        return sorted([lbl.name for lbl in self._derived_labels])

    def get_atoms(self):
        return self._atoms

    @typechecked
    def add_atom(self, atom: AtomicLabel):
        self._atoms.add(atom)
        if len(self._derived_labels) > 0:
            self._reinit()

    @typechecked
    def add_label(self, label: Label):
        self._add_to_derived_labels(label)

    def _reinit(self):
        previous_derived_labels = self._derived_labels
        self._derived_labels = set()
        self._computable_atoms = set()
        self._computable_sets = set()
        self._warn_size = 10
        for label in previous_derived_labels:
            self.add_label(label)

    @typechecked()
    def _add_to_derived_labels(self, label: Label):
        if any(inc not in self._atoms for inc in label.included):
            msg = f"{set(label.included) - self._atoms} not part of collection"
            raise ValueError(msg)
        self._derived_labels.add(label)
        self._update_computable(label.included)
        self._update_computable(frozenset(self._atoms - label.included))

    def _check_size(self):
        size = len(self.get_computable_sets())
        if size >= self._warn_size:
            self._increase_warn_size()
            msg = (
                f"Your collection of computable sets is getting big. "
                f"Proceed with caution. "
                f"Current size: {size} "
                f"Next warning at {self._warn_size}"
            )
            warnings.warn(msg, stacklevel=1)

    @typechecked
    def _add_to_computable_atoms(self, new_atom: AtomicLabel):
        new_computable_sets: Set[FrozenSet[AtomicLabel]] = set()
        new_atoms: Set[AtomicLabel] = set()
        for atomset in self._computable_sets:
            new_set = atomset - {
                new_atom,
            }
            if len(new_set) > 1:
                new_computable_sets.add(new_set)
            elif len(new_set) == 1:
                [atom] = new_set
                new_atoms.add(atom)
        self._computable_sets = new_computable_sets
        self._check_size()
        self._computable_atoms.add(new_atom)
        for atom in new_atoms:
            self._add_to_computable_atoms(atom)

    @typechecked
    def _add_a_computable_set(self, added_set: FrozenSet[AtomicLabel]):
        new_set = added_set - self._computable_atoms
        if len(new_set) == 1:
            [new_atom] = new_set
            self._add_to_computable_atoms(new_atom)
        elif len(new_set) > 1:
            self._computable_sets.add(new_set)
            self._check_size()

    def _increase_warn_size(self):
        self._warn_size = self._warn_size * 10

    @typechecked
    def _update_computable(self, added_set: FrozenSet[AtomicLabel]):
        # compute the part of the `added_set` that is non-trivial by ignoring
        # all the atomic labels that are already computable
        new_set = added_set - self._computable_atoms
        if len(new_set) == 1:  # this is a single atom
            [new_atom] = new_set
            self._add_to_computable_atoms(new_atom)
        elif len(new_set) > 1:
            newly_computable_it1 = {
                new_set,
            }
            for old_set in self._computable_sets:
                newly_computable_it1.update(computable(new_set, old_set))
            newly_computable_it2 = set()
            for set1, set2 in itertools.combinations(newly_computable_it1 - self._computable_sets, r=2):
                newly_computable_it2.update(computable(set1, set2))
            for computable_set in newly_computable_it1 | newly_computable_it2:
                self._add_a_computable_set(computable_set)
        # don't do anything if set is empty

    def can_compute_atoms(self) -> bool:
        return self._atoms == self.get_computable_atoms()

    @typechecked
    def can_compute(self, test_label: Union["AnyLabelType", "LabelCollection"]):
        if isinstance(test_label, LabelCollection):
            if test_label._atoms != self._atoms:
                return False
            else:
                for lbl in test_label:
                    if not self.can_compute(lbl):
                        return False
                return True
        elif isinstance(test_label, AtomicLabel):
            included_set = frozenset(
                [
                    test_label,
                ]
            )
        elif isinstance(test_label, Label):
            included_set = test_label.included
        elif check_type_bool(test_label, CollectionLike[AtomicLabel]):
            included_set = frozenset(test_label)
        else:
            msg = f"Unknown type of `test_label`: {type(test_label)}"
            raise TypeError(msg)
        included_set = included_set - self.get_computable_atoms()

        if len(included_set) == 0:
            return True
        else:
            return included_set in self.get_computable_sets()

    def contains_match(self, test_label: Label):
        for lbl in self.get_derived_labels():
            if lbl.match(test_label):
                return True
        return False


AnyLabelType = Union[AtomicLabel, Label, Set[AtomicLabel]]
