from itertools import combinations

import pytest
from typeguard import TypeCheckError

from labelcomposer.label import AtomicLabel, Label, LabelCollection


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
        with pytest.raises(TypeCheckError):
            AtomicLabel("A", "A")

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


class TestLabel:
    def test_basic_usage(self):
        a = AtomicLabel("A")
        b = AtomicLabel("B")
        myab1 = Label([a, b])
        assert myab1.included == {a, b}
        assert myab1.name is None
        myab2 = Label((a, b), "AB")
        assert myab2.included == {a, b}
        assert myab2.name == "AB"
        myab3 = Label(frozenset([a, b]), "ab")
        assert myab3.included == {a, b}
        assert myab3.name == "ab"

    def test_type_error(self):
        a = AtomicLabel("A")
        with pytest.raises(TypeCheckError):
            Label(a, "my_label")
        with pytest.raises(TypeCheckError):
            Label([a], a)

    def test_equality(self):
        a = AtomicLabel("A")
        b = AtomicLabel("B")
        ab1 = Label([a, b], "AB")
        ab2 = Label((a, b), "AB")
        assert ab1 == ab2
        assert ab2 == ab1
        assert hash(ab1) == hash(ab2)

    def test_inequality(self):
        a = AtomicLabel("A")
        b = AtomicLabel("B")
        assert Label([a, b], "AB") != Label([a, b], "ab")
        assert hash(Label([a, b], "AB")) != hash(Label([a, b], "ab"))
        assert Label([a], "A") != Label([a, b], "A")
        assert hash(Label([a], "A")) != hash(Label([a, b], "A"))
        assert Label([a], "A") != Label([a, b], "AB")
        assert hash(Label([a], "A")) != hash(Label([a, b], "AB"))

    def test_name_setter(self):
        a = AtomicLabel("A")
        albl1 = Label([a])
        albl2 = Label([a], "A")
        assert albl1 != albl2
        assert hash(albl1) != hash(albl2)
        albl1.name = "A"
        assert albl1 == albl2
        assert hash(albl1) == hash(albl2)
        albl2.name = "differentA"
        assert albl1 != albl2
        assert hash(albl1) != hash(albl2)

    def test_add(self):
        a = AtomicLabel("A")
        b = AtomicLabel("B")
        c = AtomicLabel("C")
        d = AtomicLabel("D")
        ab = Label([a, b], "AB")
        abc1 = ab + c
        assert abc1 == frozenset([a, b, c])
        assert Label(abc1) == Label([a, b, c])

        abcd1 = ab + {c, d, d}
        assert abcd1 == frozenset([a, b, c, d])
        assert Label(abcd1) == Label([a, b, c, d])

        cd = Label([c, d], "CD")
        assert ab + cd == frozenset([a, b, c, d])
        assert Label(abcd1, "ABCD") == Label(ab + cd, "ABCD")

    def test_or(self):
        a = AtomicLabel("A")
        b = AtomicLabel("B")
        c = AtomicLabel("C")
        d = AtomicLabel("D")
        ab = Label([a, b], "AB")
        abc1 = ab | c
        assert abc1 == frozenset([a, b, c])
        assert Label(abc1) == Label([a, b, c])

        abcd1 = ab | [c, d, d]
        assert abcd1 == frozenset([a, b, c, d])
        assert Label(abcd1) == Label([a, b, c, d])

        cd = Label([c, d], "CD")
        assert ab | cd == frozenset([a, b, c, d])
        assert Label(abcd1, "ABCD") == Label(ab | cd, "ABCD")

    def test_sub(self):
        a = AtomicLabel("A")
        b = AtomicLabel("B")
        c = AtomicLabel("C")
        d = AtomicLabel("D")
        abcd = Label([a, b, c, d], "ABCD")
        abc1 = abcd - d
        abc2 = Label([a, b, c]) - d
        assert abc1 == frozenset([a, b, c])
        assert abc1 == abc2

        ab1 = abcd - (c, d, d)
        assert ab1 == frozenset([a, b])
        ab2 = abcd - Label([c, d])
        assert ab1 == ab2


class TestLabelCollection:
    def test_basic_usage(self):
        a = AtomicLabel("A")
        b = AtomicLabel("B")
        c = AtomicLabel("C")
        d = AtomicLabel("D")
        hierarchy = LabelCollection([a, b, c, d])
        a_lbl = Label([a], "newA")
        b_lbl = Label([b], "B")
        ac_lbl = Label([a, c], "AC")
        hierarchy.add_label(a_lbl)
        hierarchy.add_label(b_lbl)
        hierarchy.add_label(ac_lbl)
        assert hierarchy.get_atoms() == {a, b, c, d}
        assert hierarchy.get_computable_atoms() == {a, b, c, d}
        assert hierarchy.get_computable_sets() == set()
        assert hierarchy.get_derived_labels() == {a_lbl, b_lbl, ac_lbl}
        assert hierarchy.get_names() == ["AC", "B", "newA"]

    def test_empty_like(self):
        a = AtomicLabel("A")
        b = AtomicLabel("B")
        c = AtomicLabel("C")
        d = AtomicLabel("D")
        hierarchy = LabelCollection([a, b, c])
        hierarchy.add_label(Label([a, b]))
        hierarchy2 = LabelCollection.empty_like(hierarchy)
        assert hierarchy2.get_atoms() == {a, b, c}
        hierarchy.add_atom(d)
        assert hierarchy2.get_atoms() == {a, b, c}
        assert len(hierarchy2.get_derived_labels()) == 0

    def test_computable_labels_2classes(self):
        a = AtomicLabel("A", 1)
        b = AtomicLabel("B", 2)
        c = AtomicLabel("C", 3)
        d = AtomicLabel("D", 4)
        class1 = Label([a, b], "AB")
        class2 = Label([b, c], "BC")
        my_list = [a, b, c, d]
        mylblset = LabelCollection(my_list, labels=[class1, class2])

        all_combos = []
        for i in range(len(my_list) + 1):
            all_combos += list(combinations(my_list, i))
        for entry in all_combos:
            assert mylblset.can_compute(set(entry))

    def test_computable_labels_3classes(self):
        a = AtomicLabel("A", 1)
        b = AtomicLabel("B", 2)
        c = AtomicLabel("C", 3)
        d = AtomicLabel("D", 4)
        e = AtomicLabel("E", 5)
        f = AtomicLabel("F", 6)
        g = AtomicLabel("G", 7)
        h = AtomicLabel("H", 8)
        class1 = Label([a, b, d, e], "ABDE")
        class2 = Label([b, c, e, f], "BCEF")
        class3 = Label([d, e, f, g], "DEFG")
        my_list = [a, b, c, d, e, f, g, h]
        mylblset = LabelCollection(my_list, labels=[class1, class2, class3])

        all_combos = []
        for i in range(len(my_list) + 1):
            all_combos += list(combinations(my_list, i))
        for entry in all_combos:
            assert mylblset.can_compute(set(entry))

    def test_computable_labels_4classes(self):
        a_atom = AtomicLabel("A", 1)
        b_atom = AtomicLabel("B", 2)
        c_atom = AtomicLabel("C", 3)
        d_atom = AtomicLabel("D", 4)
        e_atom = AtomicLabel("E", 5)
        f_atom = AtomicLabel("F", 6)
        g_atom = AtomicLabel("G", 7)
        h_atom = AtomicLabel("H", 8)
        i_atom = AtomicLabel("I", 9)
        j_atom = AtomicLabel("J", 10)
        k_atom = AtomicLabel("K", 11)
        l_atom = AtomicLabel("L", 12)
        m_atom = AtomicLabel("M", 13)
        n_atom = AtomicLabel("N", 14)
        class1 = Label([a_atom, c_atom, d_atom, e_atom, g_atom, h_atom, i_atom], "CLASS1")
        class2 = Label([b_atom, c_atom, d_atom, g_atom, h_atom, j_atom, k_atom], "CLASS2")
        class3 = Label([d_atom, e_atom, f_atom, h_atom, i_atom, k_atom, l_atom], "CLASS3")
        class4 = Label([g_atom, h_atom, i_atom, j_atom, k_atom, l_atom, m_atom], "CLASS4")
        my_list = [
            a_atom,
            b_atom,
            c_atom,
            d_atom,
            e_atom,
            f_atom,
            g_atom,
            h_atom,
            i_atom,
            j_atom,
            k_atom,
            l_atom,
            m_atom,
            n_atom,
        ]
        with pytest.warns(UserWarning):
            mylblset = LabelCollection(my_list, labels=[class1, class2, class3, class4])

        all_combos = []
        for indx in range(len(my_list) + 1):
            all_combos += list(combinations(my_list, indx))
        for entry in all_combos:
            assert mylblset.can_compute(set(entry))

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
        cyto = AtomicLabel("Cytosol", 35)
        mtin = AtomicLabel("MT in", 36)
        atoms = [
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
            cyto,
            mtin,
        ]
        lblset = LabelCollection(
            atoms,
            labels=[
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
            ],
        )
        assert lblset.can_compute_atoms()
