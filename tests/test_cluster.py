"""Grapheme clustering: text -> typed Cluster stream (base + marks + span).

The cluster layer is purely orthographic: it groups each base character with
its trailing marks, validates impossible stacks, and round-trips exactly.
It knows nothing about tajweed.
"""
import pytest

from quran_g2p import codepoints as cp
from quran_g2p.cluster import Cluster, IllegalStackError, cluster, uncluster
from quran_g2p.textbank import AyahRef, TextBank


def test_bismi_tanzil_clusters():
    # بِسْمِ = BEH+KASRA, SEEN+SUKUN, MEEM+KASRA
    text = cp.BEH + cp.KASRA + cp.SEEN + cp.SUKUN + cp.MEEM + cp.KASRA
    got = cluster(text)
    assert [(c.base, c.marks) for c in got] == [
        (cp.BEH, (cp.KASRA,)),
        (cp.SEEN, (cp.SUKUN,)),
        (cp.MEEM, (cp.KASRA,)),
    ]
    assert [c.span for c in got] == [(0, 2), (2, 4), (4, 6)]


def test_space_is_its_own_cluster():
    text = cp.BEH + cp.KASRA + " " + cp.MEEM
    got = cluster(text)
    assert [(c.base, c.marks) for c in got] == [
        (cp.BEH, (cp.KASRA,)),
        (" ", ()),
        (cp.MEEM, ()),
    ]


def test_multiple_marks_stack_in_order():
    # لّٰ = LAM + SHADDA + SUPERSCRIPT ALEF (as in الله in Tanzil)
    text = cp.LAM + cp.SHADDA + cp.SUPERSCRIPT_ALEF
    (c,) = cluster(text)
    assert c.base == cp.LAM
    assert c.marks == (cp.SHADDA, cp.SUPERSCRIPT_ALEF)


def test_small_waw_attaches_to_preceding_cluster():
    # هُۥ (silah): HEH + DAMMA + SMALL WAW — small waw is a mark by project decision
    text = cp.HEH + cp.DAMMA + cp.SMALL_WAW
    (c,) = cluster(text)
    assert c.marks == (cp.DAMMA, cp.SMALL_WAW)


def test_mark_before_any_base_is_illegal():
    with pytest.raises(IllegalStackError):
        cluster(cp.KASRA + cp.BEH)


def test_duplicate_identical_mark_is_illegal():
    with pytest.raises(IllegalStackError):
        cluster(cp.BEH + cp.FATHA + cp.FATHA)


def test_two_vowel_slot_marks_are_illegal():
    with pytest.raises(IllegalStackError):
        cluster(cp.BEH + cp.FATHA + cp.DAMMA)
    with pytest.raises(IllegalStackError):
        cluster(cp.BEH + cp.SUKUN + cp.FATHA)


def test_fatha_plus_superscript_alef_is_legal():
    # مَٰلِكِ 1:4 — fatha and dagger alif co-occur on one base
    got = cluster(cp.MEEM + cp.FATHA + cp.SUPERSCRIPT_ALEF)
    assert got[0].marks == (cp.FATHA, cp.SUPERSCRIPT_ALEF)


def test_segment_carrier_small_yeh_opens_new_vowel_slot():
    # 27:36 (both editions): NOON+KASRA + SMALL YEH + FATHA — the silah yaa
    # carries its own fatha; legal because SMALL YEH is a segment carrier.
    got = cluster(cp.NOON + cp.KASRA + cp.SMALL_YEH + cp.FATHA)
    assert got[0].marks == (cp.KASRA, cp.SMALL_YEH, cp.FATHA)


def test_segment_carrier_floating_hamza_opens_new_vowel_slot():
    # Tanzil 2:72: REH+FATHA+SUPERSCRIPT ALEF + HAMZA ABOVE + SUKUN — a floating
    # hamza segment with its own sukun.
    got = cluster(cp.REH + cp.FATHA + cp.SUPERSCRIPT_ALEF + cp.HAMZA_ABOVE + cp.SUKUN)
    assert got[0].marks == (cp.FATHA, cp.SUPERSCRIPT_ALEF, cp.HAMZA_ABOVE, cp.SUKUN)


def test_two_vowels_in_same_segment_still_illegal_after_carrier():
    with pytest.raises(IllegalStackError):
        cluster(cp.BEH + cp.FATHA + cp.SMALL_YEH + cp.FATHA + cp.DAMMA)


def test_tatweel_is_transparent_its_marks_belong_to_preceding_letter():
    # KFGQPC كـَلَّا: KAF + TATWEEL + FATHA — the fatha rides the kasheeda but
    # belongs to the kaf (SPEC-002 finding; 33 kalla-class sites).
    got = cluster(cp.KAF + cp.TATWEEL + cp.FATHA)
    assert [(c.base, c.marks) for c in got] == [(cp.KAF, (cp.TATWEEL, cp.FATHA))]


def test_roundtrip_whole_corpus_both_editions():
    for edition in ("tanzil", "kfgqpc"):
        tb = TextBank.load(edition)
        for ref in tb.refs():
            text = tb.ayah(ref)
            cs = cluster(text)
            assert uncluster(cs) == text, f"round-trip failed at {edition} {ref}"
            # spans tile the string exactly
            pos = 0
            for c in cs:
                assert c.span[0] == pos
                pos = c.span[1]
            assert pos == len(text)
