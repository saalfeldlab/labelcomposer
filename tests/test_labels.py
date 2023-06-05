from itertools import combinations
from typing import Tuple, Union

import pytest
from typeguard import TypeCheckError

from labelcomposer.label import AtomicLabel, AtomicLabelSet, Label, LabelCollection


class TestAtomicLabel:
    def test_basic_usage(self):
        a = AtomicLabel("A", 1)
        assert a.name == "A"
        assert a.index == 1
        b = AtomicLabel("B")
        assert b.name == "B"
        assert b.index is None

    def test_type_errors(self):
        with pytest.raises(TypeCheckError):
            AtomicLabel(1, 1)

    def test_equality(self):
        a1 = AtomicLabel("A", 1)
        a2 = AtomicLabel("A", 1)
        assert a1 == a2
        assert a2 == a1
        assert hash(a1) == hash(a2)
        b1 = AtomicLabel("B", None)
        b2 = AtomicLabel("B")
        assert b1 == b2
        assert b2 == b1
        assert hash(b1) == hash(b2)

    def test_type_errors2(self):
        with pytest.raises(TypeCheckError):
            AtomicLabel("A", "A")

    def test_inequality(self):
        a = AtomicLabel("A", 1)
        b = AtomicLabel("A", 2)
        assert a != b
        assert b != a
        assert hash(a) != hash(b)
        a = AtomicLabel("A", 1)
        b = AtomicLabel("B", 1)
        assert a != b
        assert b != a
        assert hash(a) != hash(b)
        a = AtomicLabel("A", 1)
        b = AtomicLabel("B", 2)
        assert a != b
        assert b != a
        assert hash(a) != hash(b)
        a = AtomicLabel("A")
        b = AtomicLabel("A", 1)
        assert a != b
        assert b != a
        assert hash(a) != hash(b)
        a = AtomicLabel("A")
        b = AtomicLabel("B")
        assert a != b
        assert b != a
        assert hash(a) != hash(b)
        assert a != 1
        assert 1 != a
        assert hash(a) != hash(1)

    def test_string(self):
        a = AtomicLabel("A")
        b = AtomicLabel("BLA", 1)
        assert str(a) == "A (id not set)"
        assert str(b) == "BLA (1)"

    def test_repr(self):
        a = AtomicLabel("A")
        b = AtomicLabel("BLA", 1)
        assert repr(a) == "AtomicLabel A (id not set)"
        assert repr(b) == "AtomicLabel BLA (1)"

    def test_add(self):
        a = AtomicLabel("A")
        b = AtomicLabel("B")
        c = AtomicLabel("C")
        ab = AtomicLabelSet([a, b])
        abc1 = ab + c
        abc2 = c + ab
        assert abc1 == AtomicLabelSet([a, b, c])
        assert abc2 == abc1
        ab2 = b + ab
        assert ab2 == ab
        ab_lbl = Label(ab, "AB")
        abc1_lbl = ab_lbl + c
        abc2_lbl = c + ab_lbl
        assert abc1_lbl == Label(AtomicLabelSet([a, b, c]))
        assert abc2_lbl == abc1_lbl
        ab2_lbl = b + ab_lbl
        ab2_lbl.name = "AB"
        assert ab2_lbl == ab_lbl

    def test_add_error(self):
        a = AtomicLabel("A")
        b = AtomicLabel("B")
        with pytest.raises(TypeError) as e:
            a + b
        assert "unsupported operand type(s) for +: 'AtomicLabel' and 'AtomicLabel'" in str(e.value)
        with pytest.raises(TypeError) as e:
            a + 1
        assert "unsupported operand type(s) for +: 'AtomicLabel' and 'int'" in str(e.value)

    def test_or_error(self):
        a = AtomicLabel("A")
        b = AtomicLabel("B")
        with pytest.raises(TypeError):
            a | b
        assert "unsupported operand type(s) for |: 'AtomicLabel' and 'AtomicLabel'"
        with pytest.raises(TypeError):
            a | 1
        assert "unsupported operand type(s) for |: 'AtomicLabel' and 'int'"

    def test_or(self):
        a = AtomicLabel("A")
        b = AtomicLabel("B")
        c = AtomicLabel("C")
        ab = AtomicLabelSet([a, b])
        abc1 = ab | c
        abc2 = c | ab
        assert abc1 == AtomicLabelSet([a, b, c])
        assert abc2 == abc1
        ab2 = b | ab
        assert ab2 == ab
        ab_lbl = Label(ab, "AB")
        abc1_lbl = ab_lbl | c
        abc2_lbl = c | ab_lbl
        assert abc1_lbl == Label(AtomicLabelSet([a, b, c]))
        assert abc2_lbl == abc1_lbl
        ab2_lbl = b | ab_lbl
        ab2_lbl.name = "AB"
        assert ab2_lbl == ab_lbl

    def test_and(self):
        a = AtomicLabel("A")
        b = AtomicLabel("B")
        c = AtomicLabel("C")
        ab = AtomicLabelSet([a, b])
        empty = c & ab
        assert empty == AtomicLabelSet([])
        b2 = b & ab
        assert b2 == AtomicLabelSet([b])
        ab_lbl = Label(ab, "AB")
        empty1_lbl = ab_lbl & c
        empty2_lbl = c & ab_lbl
        assert empty1_lbl == Label(AtomicLabelSet([]))
        assert empty2_lbl == empty1_lbl
        b2_lbl = b & ab_lbl
        assert b2_lbl == Label(b2)


class TestAtomicLabelSet:
    def test_basic_usage(self):
        a = AtomicLabel("A", 1)
        b = AtomicLabel("B", 2)
        c = AtomicLabel("C")
        d = AtomicLabel("D")
        a1 = AtomicLabelSet([a])
        assert a1.members == {a}
        a2 = AtomicLabelSet((a,))
        assert a2.members == {a}
        a3 = AtomicLabelSet(
            {
                a,
            }
        )
        assert a3.members == {a}
        aa = AtomicLabelSet([a, a])
        assert aa.members == {a}
        ab = AtomicLabelSet([a, b])
        assert ab.members == {a, b}
        abc = AtomicLabelSet([a, b, c])
        assert abc.members == {a, b, c}
        abcd = AtomicLabelSet([a, b, c, d])
        assert abcd.members == {a, b, c, d}

    def test_empty_set(self):
        empty = AtomicLabelSet([])
        assert empty.members == set()

    def test_type_errors(self):
        a = AtomicLabel("A", 1)
        with pytest.raises(TypeCheckError):
            AtomicLabelSet(a)
        # assert (
        #    "Expected an iterable of 'AtomicLabel' instances, but got 'AtomicLabel'"
        #    in str(e.value)
        # )
        a2 = AtomicLabelSet(
            [
                a,
            ]
        )
        with pytest.raises(TypeCheckError):
            AtomicLabelSet([4, 5])
        with pytest.raises(TypeCheckError):
            AtomicLabelSet([a2])
        # assert (
        #     "Expected an iterable of 'AtomicLabel' instances, but got list of {'AtomicLabelSet'}"
        #     in str(e.value)
        # )
        with pytest.raises(TypeCheckError):
            AtomicLabelSet([a2, a])
        # assert "Expected an iterable of 'AtomicLabel' instances, but got list of {'AtomicLabel', 'AtomicLabelSet'}" in str(
        #     e.value
        # ) or "Expected an iterable of 'AtomicLabel' instances, but got list of {'AtomicLabelSet', 'AtomicLabel'}" in str(
        #     e.value
        # )

    def test_equality(self):
        a = AtomicLabel("A", 1)
        b = AtomicLabel("B", 2)
        c = AtomicLabel("C")
        abc1 = AtomicLabelSet([a, b, c])
        abc2 = AtomicLabelSet((c, b, a))
        abc3 = AtomicLabelSet([a, a, b, c, c])
        abc4 = AtomicLabelSet({a, b, b, c})
        assert abc1 == abc2
        assert abc2 == abc1
        assert abc1 == abc3
        assert abc3 == abc1
        assert abc1 == abc4
        assert abc4 == abc1
        assert hash(abc1) == hash(abc2) == hash(abc3) == hash(abc4)

    def test_inequality(self):
        a = AtomicLabel("A", 1)
        b = AtomicLabel("B", 2)
        c = AtomicLabel("C")
        abc = AtomicLabelSet([b, c, a])
        ab = AtomicLabelSet([a, b])
        assert abc != ab
        assert ab != abc
        assert hash(ab) != hash(abc)
        assert abc != {a, b, c}

    def test_add(self):
        a = AtomicLabel("A", 1)
        b = AtomicLabel("B")
        a1 = AtomicLabelSet([a])
        b1 = AtomicLabelSet([b])
        ab = AtomicLabelSet([a, b])
        assert ab == a1 + b1
        assert ab == a1 + b
        assert ab == a + b1
        assert ab == ab + a

    def test_or(self):
        a = AtomicLabel("A", 1)
        b = AtomicLabel("B")
        a1 = AtomicLabelSet([a])
        b1 = AtomicLabelSet([b])
        ab = AtomicLabelSet([a, b])
        assert ab == a1 | b1
        assert ab == a1 | b
        assert ab == ab | a

    def test_add_error(self):
        a = AtomicLabel("A")
        b = AtomicLabel("B")
        ab = AtomicLabelSet([a, b])
        with pytest.raises(TypeError) as e:
            ab + {a}
        assert "unsupported operand type(s) for +: 'AtomicLabelSet' and 'set'" in str(e.value)
        with pytest.raises(TypeError) as e:
            a + b
        with pytest.raises(TypeError) as e:
            {a} + ab
        assert "unsupported operand type(s) for +: 'set' and 'AtomicLabelSet'" in str(e.value)

    def test_or_error(self):
        a = AtomicLabel("A")
        b = AtomicLabel("B")
        ab = AtomicLabelSet([a, b])
        with pytest.raises(TypeError) as e:
            ab | {a}
        assert "unsupported operand type(s) for |: 'AtomicLabelSet' and 'set'" in str(e.value)
        with pytest.raises(TypeError) as e:
            a | b

    def test_sub(self):
        a = AtomicLabel("A", 1)
        b = AtomicLabel("B")
        c = AtomicLabel("C")
        abc = AtomicLabelSet([a, b, c])
        ab1 = AtomicLabelSet([a, b])
        c1 = AtomicLabelSet([c])
        assert ab1 == abc - c
        assert ab1 == abc - c1
        assert c1 == abc - ab1

    def test_sub_error(self):
        a = AtomicLabel("A")
        a1 = AtomicLabelSet([a])
        with pytest.raises(TypeError) as e:
            a1 - {a}
        assert "unsupported operand type(s) for -: 'AtomicLabelSet' and 'set'" in str(e.value)

    def test_and(self):
        a = AtomicLabel("A", 1)
        b = AtomicLabel("B")
        c = AtomicLabel("C")
        d = AtomicLabel("D", 2)
        abcd = AtomicLabelSet([a, b, c, d])
        ab = AtomicLabelSet([a, b])
        c1 = AtomicLabelSet([c])
        assert abcd & ab == ab
        assert abcd & c == c1
        assert abcd == abcd + ab + c1

    def test_and_error(self):
        a = AtomicLabel("A")
        b = AtomicLabel("B")
        ab = AtomicLabelSet(
            [
                a,
            ]
        )
        with pytest.raises(TypeError):
            ab & {b}
        assert "unsupported operand type(s) for &: 'AtomicLabelSet' and 'set'"

    def test_computable_labels(self):
        aa = AtomicLabel("A", 1)
        bb = AtomicLabel("B")
        cc = AtomicLabel("C")
        dd = AtomicLabel("D")
        ee = AtomicLabel("E")
        a = AtomicLabelSet([aa])
        b = AtomicLabelSet([bb])
        a_b_computable = a.get_computable_labels(b)
        assert a_b_computable == {
            AtomicLabelSet([aa, bb]),
            AtomicLabelSet([]),
            AtomicLabelSet([aa]),
            AtomicLabelSet([bb]),
        }
        abcd = AtomicLabelSet([aa, bb, cc, dd])
        cde = AtomicLabelSet([cc, dd, ee])
        abcd_cde_computable = abcd.get_computable_labels(cde)
        assert abcd_cde_computable == {
            abcd,
            cde,
            AtomicLabelSet([aa, bb, cc, dd, ee]),
            AtomicLabelSet([aa, bb, ee]),
            AtomicLabelSet([ee]),
            AtomicLabelSet([aa, bb]),
            AtomicLabelSet([cc, dd]),
        }
        assert AtomicLabelSet([aa, bb, cc, dd]).get_computable_labels(abcd) == {abcd}

    def test_repr(self):
        a = AtomicLabel("A")
        b = AtomicLabel("BBB", 1)
        lbl = AtomicLabelSet([a, b])
        lbl_repr = repr(lbl)
        assert (
            lbl_repr == "AtomicLabelSet{" + repr(a) + ", " + repr(b) + "}"
            or lbl_repr == "AtomicLabelSet{" + repr(b) + ", " + repr(a) + "}"
        )


class TestLabel:
    def test_basic_usage(self):
        a = AtomicLabel("A")
        b = AtomicLabel("B")
        ab = AtomicLabelSet([a, b])
        myab1 = Label(ab)
        assert myab1.annotations == ab
        assert myab1.name is None
        myab2 = Label([a, b], "AB")
        assert myab2.annotations == ab
        assert myab2.name == "AB"

    def test_not_hashable(self):
        a = AtomicLabel("A")
        albl = Label([a])
        with pytest.raises(TypeError) as e:
            {albl}
        assert "unhashable type" in str(e.value)

    def test_type_error(self):
        a = AtomicLabel("A")
        with pytest.raises(TypeCheckError):
            Label(a, "my_label")
        with pytest.raises(TypeCheckError):
            Label([a], a)
        with pytest.raises(TypeCheckError):
            Label(
                [
                    AtomicLabelSet([a]),
                ]
            )
        with pytest.raises(TypeCheckError):
            Label(AtomicLabelSet([a]), 5)

    def test_equality(self):
        a = AtomicLabel("A")
        b = AtomicLabel("B")
        ab = AtomicLabelSet([a, b])
        ab1 = Label([a, b], "AB")
        ab2 = Label(ab, "AB")
        assert ab1 == ab2
        assert ab2 == ab1

    def test_inequality(self):
        a = AtomicLabel("A")
        b = AtomicLabel("B")
        ab = AtomicLabelSet([a, b])
        assert Label(ab, "AB") != Label(ab, "ab")
        assert Label([a], "A") != Label(ab, "A")
        assert Label([a], "A") != Label(ab, "AB")

    def test_name_setter(self):
        a = AtomicLabel("A")
        albl1 = Label([a])
        albl2 = Label([a], "A")
        assert albl1 != albl2
        albl1.name = "A"
        assert albl1 == albl2
        albl2.name = "differentA"
        assert albl1 != albl2

    def test_add(self):
        a = AtomicLabel("A")
        b = AtomicLabel("B")
        c = AtomicLabel("C")
        ab = Label([a, b], "AB")
        abc1 = Label([a, b, c], "ABC")
        abc2 = ab + c
        abc2.name = "ABC"
        assert abc1 == abc2
        abc2_r = c + ab
        abc2_r.name = "ABC"
        assert abc2 == abc2_r
        abc3 = ab + AtomicLabelSet([c])
        abc3.name = "ABC"
        assert abc1 == abc3
        abc3_r = AtomicLabelSet([c]) + ab
        abc3_r.name = "ABC"
        assert abc3 == abc3_r
        abc4 = ab + Label([c], "C")
        abc4.name = "ABC"
        assert abc1 == abc4
        abc4_r = Label([c], "C") + ab
        abc4_r.name = "ABC"
        assert abc4 == abc4_r
        assert abc4 == abc4_r


class TestLabelSet:
    def test_basic_usage(self):
        a = AtomicLabel("A")
        b = AtomicLabel("B")
        c = AtomicLabel("C")
        a_as = AtomicLabelSet(
            [
                a,
            ]
        )
        b_as = AtomicLabelSet(
            [
                b,
            ]
        )
        ac_as = AtomicLabelSet(
            [
                a,
                c,
            ]
        )
        a_lbl = Label(a_as, "newA")
        b_lbl = Label(b_as, "B")
        ac_lbl = Label(ac_as, "AC")
        lblset1 = LabelCollection(
            [
                a_lbl,
            ]
        )
        lblset2 = LabelCollection((a_lbl,))
        LabelCollection([a_lbl, b_lbl, ac_lbl])
        assert (
            lblset1.get_labels()
            == lblset2.get_labels()
            == {
                a_as,
            }
        )
        assert lblset1.get_names() == lblset2.get_names() == {"newA"}
        assert (
            lblset1.get_members()
            == lblset2.get_members()
            == [
                a_lbl,
            ]
        )

    def test_computable_labels_2classes(self):
        a = AtomicLabel("A", 1)
        b = AtomicLabel("B", 2)
        c = AtomicLabel("C", 3)
        class1 = Label([a, b], "AB")
        class2 = Label([b, c], "BC")
        mylblset = LabelCollection([class1, class2])
        my_list = [a, b, c]
        all = []
        for i in range(len(my_list) + 1):
            all += list(combinations(my_list, i))

        for entry in all:
            assert mylblset.can_compute(AtomicLabelSet(entry))

    def test_computable_labels_3classes(self):
        a = AtomicLabel("A", 1)
        b = AtomicLabel("B", 2)
        c = AtomicLabel("C", 3)
        d = AtomicLabel("D", 4)
        e = AtomicLabel("E", 5)
        f = AtomicLabel("F", 6)
        g = AtomicLabel("C", 7)
        class1 = Label([a, b, d, e], "ABDE")
        class2 = Label([b, c, e, f], "BCEF")
        class3 = Label([d, e, f, g], "DEFG")
        mylblset = LabelCollection([class1, class2, class3])
        my_list = [a, b, c, d, e, f, g]
        all = []
        for i in range(len(my_list) + 1):
            all += list(combinations(my_list, i))
        for entry in all:
            assert mylblset.can_compute(AtomicLabelSet(entry))

    def test_computable_labels_4classes(self):
        a = AtomicLabel("A", 1)
        b = AtomicLabel("B", 2)
        c = AtomicLabel("C", 3)
        d = AtomicLabel("D", 4)
        e = AtomicLabel("E", 5)
        f = AtomicLabel("F", 6)
        g = AtomicLabel("G", 7)
        h = AtomicLabel("H", 8)
        i = AtomicLabel("I", 9)
        j = AtomicLabel("J", 10)
        k = AtomicLabel("K", 11)
        l = AtomicLabel("L", 12)
        m = AtomicLabel("M", 13)

        class1 = Label([a, c, d, e, g, h, i], "CLASS1")
        class2 = Label([b, c, d, g, h, j, k], "CLASS2")
        class3 = Label([d, e, f, h, i, k, l], "CLASS3")
        class4 = Label([g, h, i, j, k, l, m], "CLASS4")
        mylblset = LabelCollection([class1, class2, class3, class4])
        my_list = [a, b, c, d, e, f, g, h, i, j, k, l, m]
        all = []
        for indx in range(len(my_list) + 1):
            all += list(combinations(my_list, indx))
        for entry in all:
            assert mylblset.can_compute(AtomicLabelSet(entry))

    def test_realistic(self):
        ecs = AtomicLabel("ECS", 1)
        pm = AtomicLabel("PM", 2)
        mitomem = AtomicLabel("Mito mem", 3)
        mitolum = AtomicLabel("Mito lum", 4)
        mitodna = AtomicLabel("Mito Ribo", 5)
        golgimem = AtomicLabel("Golgi mem", 6)
        golgilum = AtomicLabel("Golgi lum", 7)
        vesmem = AtomicLabel("Vesicle mem", 8)
        veslum = AtomicLabel("Vesicle lum", 9)
        endomem = AtomicLabel("Endo mem", 10)
        endolum = AtomicLabel("Endo lum", 11)
        lysomem = AtomicLabel("Lyso mem", 12)
        lysolum = AtomicLabel("Lyso lum", 13)
        ldmem = AtomicLabel("LD mem", 14)
        ldlum = AtomicLabel("LD lum", 15)
        ermem = AtomicLabel("ER mem", 16)
        erlum = AtomicLabel("ER lum", 17)
        eresmem = AtomicLabel("ERES mem", 18)
        ereslum = AtomicLabel("ERES lum", 19)
        nemem = AtomicLabel("NE mem", 20)
        nelum = AtomicLabel("NE lum", 21)
        npout = AtomicLabel("NP out", 22)
        npin = AtomicLabel("NP in", 23)
        hchrom = AtomicLabel("H Chrom", 24)
        nhchrom = AtomicLabel("N-H Chrom", 25)
        echrom = AtomicLabel("E Chrom", 26)
        nechrom = AtomicLabel("N-E Chrom", 27)
        nplasm = AtomicLabel("Nucleoplasm", 28)
        nucle = AtomicLabel("Nucleolus", 29)
        mtout = AtomicLabel("MT out", 30)
        centr = AtomicLabel("Centrosome", 31)
        dapp = AtomicLabel("Centrosome D App", 32)
        sdapp = AtomicLabel("Centrosome SD App", 33)
        ribo = AtomicLabel("Ribo", 34)
        AtomicLabel("Cytosol", 35)
        mtin = AtomicLabel("MT in", 36)
        acs = [
            ecs,
            pm,
            mitomem,
            mitolum,
            mitodna,
            golgimem,
            golgilum,
            vesmem,
            veslum,
            endomem,
            endolum,
            lysomem,
            lysolum,
            ldmem,
            ldlum,
            ermem,
            erlum,
            eresmem,
            ereslum,
            nemem,
            nelum,
            npout,
            npin,
            hchrom,
            nhchrom,
            echrom,
            nechrom,
            nplasm,
            nucle,
            mtout,
            centr,
            dapp,
            sdapp,
            ribo,
            # cyto,
            mtin,
        ]
        lblset = LabelCollection(
            [
                Label(
                    [
                        ecs,
                    ],
                    "ECS",
                ),
                Label(
                    [
                        pm,
                    ],
                    "PM",
                ),
                Label(
                    [
                        mitomem,
                    ],
                    "Mito mem",
                ),
                Label([mitomem, mitolum, mitodna], "Mito"),
                Label(
                    [
                        mitodna,
                    ],
                    "Mito Ribo",
                ),
                Label(
                    [
                        golgimem,
                    ],
                    "Golgi mem",
                ),
                Label([golgimem, golgilum], "Golgi"),
                Label(
                    [
                        vesmem,
                    ],
                    "Vesicle mem",
                ),
                Label([vesmem, veslum], "Vesicle"),
                Label(
                    [
                        endomem,
                    ],
                    "Endo mem",
                ),
                Label([endomem, endolum], "Endo"),
                Label(
                    [
                        lysomem,
                    ],
                    "Lyso mem",
                ),
                Label([lysomem, lysolum], "Lyso"),
                Label([ldmem], "LD mem"),
                Label([ldmem, ldlum], "LD"),
                Label([ermem, eresmem, nemem], "ER mem"),
                Label([ermem, erlum, eresmem, ereslum, nemem, nelum, npin, npout], "ER"),
                Label([eresmem, ereslum], "ERES"),
                Label([nemem, nelum, npout, npin], "NE"),
                Label([npout], "NP out"),
                Label([npout, npin], "NP"),
                Label([hchrom, nhchrom, echrom, nechrom], "chromatin"),
                Label([nhchrom], "N-H-Chrom"),
                Label([echrom], "E-Chrom"),
                Label([nechrom], "N=E Crhom"),
                Label(
                    [
                        nemem,
                        nelum,
                        npout,
                        npin,
                        hchrom,
                        nhchrom,
                        echrom,
                        nechrom,
                        nplasm,
                        nucle,
                    ],
                    "Nucleus",
                ),
                Label([nucle], "Nucleolus"),
                Label([mtout, mtin, centr], "MT"),
                Label([mtout], "MT out"),
                Label([centr, dapp, sdapp], "Centrosome"),
                Label(
                    [
                        dapp,
                    ],
                    "Centrosome D App",
                ),
                Label([sdapp], "Centrosome SD App"),
                Label([ribo], "Ribo"),
            ]
        )
        for ac in acs:
            assert lblset.can_compute(AtomicLabelSet([ac])), f"Label set should be able to compute {ac}"
