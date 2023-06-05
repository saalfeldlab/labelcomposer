import itertools
from typing import Dict, List, Optional, Sequence, Set, TypeVar, Union

from typeguard import CollectionCheckStrategy, check_type, typechecked

from labelcomposer.helpers import check_type_bool

T = TypeVar("T")
CollectionLike = Union[Sequence[T], Set[T]]
StringLike = Union[str, bytes, bytearray]

check_all = CollectionCheckStrategy.ALL_ITEMS


class AtomicLabel:
    @typechecked
    def __init__(self, name: StringLike, index: Union[None, int] = None):
        # if not isinstance(name, str):
        # raise TypeError(f"Expected 'str', but got '{type(name).__name__}'")
        # if not (isinstance(index, int) or index is None):
        # raise TypeError(f"Expected 'int', but got '{type(index).__name__}'")
        self.name = name
        self.index = index

    def __hash__(self) -> int:
        return hash((self.name, self.index))

    def __eq__(self, other: "AtomicLabel") -> bool:
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

    def __add__(self, other: "AnyCompoundLabelType") -> "AnyCompoundLabelType":
        if check_type_bool(other, AnyCompoundLabelType):
            return other + self
        else:
            msg = f"unsupported operand type(s) for +: 'AtomicLabel' and '{type(other).__name__}'"
            raise TypeError(msg)

    def __or__(self, other: "AnyCompoundLabelType") -> "AnyCompoundLabelType":
        if check_type_bool(other, AnyCompoundLabelType):
            return other | self
        else:
            msg = f"unsupported operand type(s) for |: 'AtomicLabel' and '{type(other).__name__}'"
            raise TypeError(msg)

    def __and__(self, other: "AnyCompoundLabelType") -> "AnyCompoundLabelType":
        if check_type_bool(other, AnyCompoundLabelType):
            return other & self
        else:
            msg = f"unsupported operand type(s) for &: 'AtomicLabel' and '{type(other).__name__}'"
            raise TypeError(msg)


class AtomicLabelSet:
    @typechecked
    def __init__(self, members: CollectionLike[AtomicLabel]):
        # if not isinstance(members, Iterable):
        #     raise TypeError(
        #         f"Expected an iterable of 'AtomicLabel' instances, but got '{type(members).__name__}'"
        #     )
        # if not all(isinstance(mem, AtomicLabel) for mem in members):
        #     raise TypeError(
        #         f"Expected an iterable of 'AtomicLabel' instances, but got {type(members).__name__} of {set(type(mem).__name__ for mem in members)}"
        #     )
        # print(check_type_bool(members, CollectionLike[AtomicLabel]))
        self.members = frozenset(members)

    def __eq__(self, other: "AtomicLabelSet") -> bool:
        if not isinstance(other, AtomicLabelSet):
            return False
        return self.members == other.members

    def __hash__(self) -> int:
        return hash(self.members)

    def __add__(self, other: "AnyLabelType") -> "AnyCompoundLabelType":
        if not check_type_bool(other, AnyLabelType):
            msg = f"unsupported operand type(s) for +: 'AtomicLabelSet' and '{type(other).__name__}'"
            raise TypeError(msg)
        if isinstance(other, Label):
            return other + self
        if isinstance(other, AtomicLabel):
            other = AtomicLabelSet({other})
        return AtomicLabelSet(self.members.union(other.members))

    def __sub__(self, other: "AnyLabelType") -> "AnyCompoundLabelType":
        if not check_type_bool(other, AnyLabelType):
            msg = f"unsupported operand type(s) for -: 'AtomicLabelSet' and '{type(other).__name__}'"
            raise TypeError(msg)
        if isinstance(other, Label):
            return Label(self - other.annotations)
        if isinstance(other, AtomicLabel):
            other = AtomicLabelSet({other})
        return AtomicLabelSet(self.members - other.members)

    def __or__(self, other: "AnyLabelType") -> "AnyCompoundLabelType":
        if not check_type_bool(other, AnyLabelType):
            msg = f"unsupported operand type(s) for |: 'AtomicLabelSet' and '{type(other).__name__}'"
            raise TypeError(msg)
        else:
            return self + other

    def __and__(self, other: "AnyLabelType") -> "AnyCompoundLabelType":
        if not check_type_bool(other, AnyLabelType):
            msg = f"unsupported operand type(s) for &: 'AtomicLabelSet' and '{type(other).__name__}'"
            raise TypeError(msg)
        if isinstance(other, Label):
            return other & self
        if isinstance(other, AtomicLabel):
            other = AtomicLabelSet({other})
        return AtomicLabelSet(self.members & other.members)

    @typechecked
    def get_computable_labels(self, other: "AnyLabelType") -> Set["AtomicLabelSet"]:
        if isinstance(other, AtomicLabel):
            other = AtomicLabelSet({other})
        if isinstance(other, Label):
            other = other.annotations
        if self == other:
            return {self}
        add = self + other
        sub1 = self - other
        sub2 = other - self
        inters = other & self
        disjoint = add - inters
        return {self, other, add, sub1, sub2, inters, disjoint}

    def __repr__(self) -> str:
        return "AtomicLabelSet{" + ", ".join(repr(ann) for ann in self.members) + "}"

    def __str__(self) -> str:
        return "AtomicLabelSet{" + ", ".join(str(ann) for ann in self.members) + "}"

    def __len__(self) -> int:
        return len(self.members)


class Label:
    @typechecked
    def __init__(
        self,
        annotations: Union[AtomicLabelSet, CollectionLike[AtomicLabel]],
        name: Optional[StringLike] = None,
    ):
        self._name = None
        if name is not None:
            self.name = name
        # if not (
        #     isinstance(annotations, AtomicLabelSet)
        #     or (
        #         isinstance(annotations, Iterable)
        #         and all(isinstance(lbl, AtomicLabel) for lbl in annotations)
        #     )
        # ):
        #     if isinstance(annotations, Iterable):
        #         got_type = f"{type(annotations).__name__} of {set(type(lbl).__name__ for lbl in annotations)}"
        #     else:
        #         got_type = f"'{type(annotations.__name__)}'"
        #     raise TypeError(
        #         f"Expected a AtomicLabelSet or an iterable of 'AtomicLabel' instances, but got {got_type}"
        #     )
        if isinstance(annotations, AtomicLabelSet):
            self.annotations = annotations
        else:
            self.annotations = AtomicLabelSet(annotations)

    def __eq__(self, other: "Label") -> bool:
        if not isinstance(other, Label):
            return False
        return self.name == other.name and self.annotations == other.annotations

    def __str__(self) -> str:
        return f"Label {self.name}: {self.annotations!s}"

    def __repr__(self) -> str:
        return f"Label: name {self.name}, label: {self.annotations!r}"

    @property
    def name(self) -> Optional[str]:
        return self._name

    @name.setter
    def name(self, name: StringLike) -> str:
        check_type(name, StringLike)
        if name is not None and not isinstance(name, str):
            name = name.decode()
        self._name = name

    def __add__(self, other: "AnyLabelType") -> "Label":
        if isinstance(other, (AtomicLabelSet, AtomicLabel)):
            return Label(self.annotations + other)
        elif isinstance(other, Label):
            return Label(self.annotations + other.annotations)
        else:
            msg = f"unsupported operand type(s) for +: 'Label' and '{type(other).__name__}'"
            raise TypeError(msg)

    def __or__(self, other: "AnyLabelType") -> "Label":
        if not check_type_bool(other, AnyLabelType):
            msg = f"unsupported operand type(s) for |: 'Label' and '{type(other).__name__}'"
            raise TypeError(msg)
        return self + other

    def __sub__(self, other: "AnyLabelType") -> "Label":
        if isinstance(other, (AtomicLabelSet, AtomicLabel)):
            return Label(self.annotations - other)
        elif isinstance(other, Label):
            return Label(self.annotations - other.annotations)
        else:
            msg = f"unsupported operand type(s) for -: 'Label' and '{type(other).__name__}'"
            raise TypeError(msg)

    def __and__(self, other: "AnyLabelType") -> "Label":
        if isinstance(other, (AtomicLabelSet, AtomicLabel)):
            return Label(self.annotations & other)
        elif isinstance(other, Label):
            return Label(self.annotations & other.annotations)
        else:
            msg = f"unsupported operand type(s) for &: 'Label' and '{type(other).__name__}"
            raise TypeError(msg)

    def __len__(self) -> int:
        return len(self.annotations)


class LabelCollection:
    @typechecked
    def __init__(self, labels: Sequence[Label]):
        # if not isinstance(labels, Sequence) or not all(
        #     isinstance(lbl, Label) for lbl in labels
        # ):
        #     if isinstance(labels, Sequence):
        #         got_type = f"{type(labels).__name__} of {set(type(lbl).__name__ for lbl in labels)}"
        #     else:
        #         got_type = f"'{type(labels.__name__)}'"
        #     raise TypeError(f"Expected sequence of 'Label', but got {got_type}")
        self._labels: Set[AtomicLabelSet] = set()
        self._names: Set[str] = set()
        self._members: List[Label] = []
        self._computable_labels: Set[AtomicLabelSet] = set()
        base_annotations: Set[AtomicLabel] = set()
        for lbl in labels:
            base_annotations.update(lbl.annotations.members)
        self._base_annotations: Dict[AtomicLabel, bool] = {ann: False for ann in base_annotations}
        for lbl in labels:
            if len(lbl) == 1:
                self.mark_computable(next(iter(lbl.annotations.members)))
        for lbl in labels:
            self.add_new_label(lbl)

    @typechecked
    def mark_computable(self, annotation: AtomicLabel):
        self._base_annotations[annotation] = True
        after_new_base: Set[AtomicLabelSet] = set()
        for ann in self._computable_labels:
            after_new_base.update({AtomicLabelSet(ann.members - {annotation})})
        self._computable_labels = after_new_base

    def extract_computable_base(self) -> List[AtomicLabel]:
        return [ba for ba, comp in self._base_annotations.items() if comp is True]

    def _update_computable(self, new_label: Label):
        new_members = new_label.annotations.members
        lbl_minus_base = list(new_members - set(self.extract_computable_base()))

        if len(lbl_minus_base) == 1:
            self.mark_computable(lbl_minus_base[0])
        elif len(lbl_minus_base) > 1:
            lbl_minus_base = AtomicLabelSet(lbl_minus_base)
            self._computable_labels.update({lbl_minus_base})
            new_computable = set()
            for lbl in self._computable_labels:
                new_computable.update(lbl.get_computable_labels(lbl_minus_base))
            new_computable2 = set()
            for lbl1, lbl2 in itertools.combinations(new_computable - self._computable_labels, r=2):
                new_computable2.update(lbl1.get_computable_labels(lbl2))
            self._computable_labels.update(new_computable, new_computable2)
            for lbl in new_computable | new_computable2:
                if len(lbl) == 1:
                    self.mark_computable(next(iter(lbl.members)))

    @typechecked
    def add_new_label(self, new_label: Label):
        if new_label.name is None:
            msg = "Name of new label needs to be set."
            raise ValueError(msg)

        if new_label.annotations not in self._labels:
            if new_label.name in self._names:
                msg = f"Label with name {new_label.name} already contained in LabelCollection {self}"
                raise ValueError(msg)
            self._labels.update({new_label.annotations})
            self._names.update({new_label.name})
            self._members.append(new_label)
            self._update_computable(new_label)

    def __iter__(self) -> Label:
        yield from self._members

    def get_members(self) -> List[Label]:
        return self._members

    def get_labels(self) -> Set[AtomicLabelSet]:
        return self._labels

    def get_names(self) -> Set[str]:
        return self._names

    @typechecked
    def can_compute(self, test_label: Union["AnyCompoundLabelType", "LabelCollection"]):
        if isinstance(test_label, LabelCollection):
            return all(self.can_compute(lbl) for lbl in test_label)
        elif isinstance(test_label, Label):
            test_label = test_label.annotations
        test_annotations = test_label.members - set(self.extract_computable_base())
        if len(test_annotations) == 0:
            return True
        else:
            return test_annotations.issubset(self._computable_labels)


AnyLabelType = Union[AtomicLabel, AtomicLabelSet, Label]
AnyCompoundLabelType = Union[AtomicLabelSet, Label]
AnyLabelType = Union[AtomicLabel, AtomicLabelSet, Label]
AnyCompoundLabelType = Union[AtomicLabelSet, Label]
AnyCompoundLabelType = Union[AtomicLabelSet, Label]
AnyCompoundLabelType = Union[AtomicLabelSet, Label]
