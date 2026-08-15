"""P10 — madd classification goldens (SPEC-180..191).

Length prescriptions are SETS (allowed = Shatibiyyah-legal, canonical from
config, scoring = attested labeling superset). Sakin-asli vs sakin-'arid
(P4 iskan provenance) separates lazim from aared.
"""
import pytest

from quran_g2p.ir import Base
from quran_g2p.phonemize import phonemize
from quran_g2p.textbank import AyahRef, TextBank


def phones_of(ref, edition="tanzil"):
    tb = TextBank.load(edition)
    (seg,) = phonemize(tb.ayah(ref), edition=edition, ref=ref).segments
    return seg.phones


def madds(ref, edition="tanzil"):
    return [p for p in phones_of(ref, edition)
            if p.kind == "madd" or (p.length is not None and p.kind == "consonant")]


def rule_ids(p):
    return [a.rule_id for a in p.provenance]


def test_1_1_final_madd_is_aared():
    last_madd = [p for p in phones_of(AyahRef(1, 1)) if p.kind == "madd"][-1]
    assert last_madd.length.allowed == frozenset({2, 4, 6})
    assert any("R189" in r for r in rule_ids(last_madd))


def test_1_7_dallin_is_lazim_6():
    ph = [p for p in phones_of(AyahRef(1, 7)) if p.kind == "madd"]
    lazim = [p for p in ph if p.length.allowed == frozenset({6})]
    assert lazim, "expected the daalleen lazim madd"
    assert any("R187" in r for p in lazim for r in rule_ids(p))


def test_2_19_samaa_is_muttasil():
    ph = [p for p in phones_of(AyahRef(2, 19)) if p.kind == "madd"]
    mut = [p for p in ph if any("R185" in r for r in rule_ids(p))]
    assert mut and all(p.length.allowed == frozenset({4, 5}) for p in mut)


def test_2_4_bimaa_unzila_is_munfasil():
    ph = [p for p in phones_of(AyahRef(2, 4)) if p.kind == "madd"]
    mun = [p for p in ph if any("R186" in r for r in rule_ids(p))]
    assert mun
    for p in mun:
        assert p.length.allowed == frozenset({4, 5})
        assert p.length.scoring == frozenset({2, 3, 4, 5, 6})


def test_2_1_letter_names_meem_is_lazim_not_aared():
    ph = [p for p in phones_of(AyahRef(2, 1)) if p.kind == "madd"]
    # the meem name's I-madd (last madd) sits before an ASLI sakin -> lazim {6}
    assert ph[-1].length.allowed == frozenset({6})


def test_106_4_khawf_leen_at_waqf():
    ph = phones_of(AyahRef(106, 4))
    leen = [p for p in ph if p.kind == "consonant" and p.base is Base.WAW
            and p.length is not None]
    assert leen, "expected leen length on the khawf waw"
    assert leen[-1].length.allowed == frozenset({2, 4, 6})
    assert any("R190" in r for r in rule_ids(leen[-1]))


def test_all_emitted_madds_carry_length_everywhere():
    tb = TextBank.load("tanzil")
    for ref in (AyahRef(1, 1), AyahRef(2, 255), AyahRef(36, 1), AyahRef(112, 1)):
        for p in phones_of(ref):
            if p.kind == "madd":
                assert p.length is not None, (ref, p)
