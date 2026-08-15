"""P2-full: mid-ayah waqf/resume segmentation (SPEC-004, plan A3 P2).

The reciter's stops come in as WaqfSpec word indices; phonemization splits
FIRST and runs every contextual phase per breath group, so pausal forms,
ibtida' resolution, and junction rules all happen inside the right segment
(post-hoc un-application is the bug factory the plan refuses to build).
"""
import pytest

from quran_g2p.ir import Base
from quran_g2p.phonemize import phonemize
from quran_g2p.textbank import AyahRef, TextBank
from quran_g2p.waqf import WaqfSpec

TB = TextBank.load("tanzil")


def segs_of(s, a, stops):
    ref = AyahRef(s, a)
    return phonemize(TB.ayah(ref), edition="tanzil", ref=ref,
                     waqf=WaqfSpec(stops=tuple(stops))).segments


def test_basic_split_112_1():
    # qul | huwa llahu ahad
    segments = segs_of(112, 1, [0])
    assert len(segments) == 2
    s1, s2 = segments
    assert [p.base for p in s1.phones] == [Base.QAF, Base.DAMMA, Base.LAM]
    # resumed segment: jalala after huwa's damma is mofakham
    gem_lams = [p for p in s2.phones if p.base is Base.LAM and p.geminated]
    assert gem_lams and gem_lams[0].tafkheem == "mofakham"
    # and the segment still takes its own pausal ending (dal + qalqalah)
    assert s2.phones[-1].base is Base.DAL and s2.phones[-1].qalqalah is not None


def test_iwad_at_midayah_stop_2_26():
    # stop after mathalan (word 6): tanween fath -> 'iwad alif {2}
    segments = segs_of(2, 26, [6])
    s1 = segments[0]
    assert s1.phones[-1].base is Base.ALEF_MADD
    assert s1.phones[-1].length.canonical == 2


def test_resume_strips_junction_shadda_2_26():
    # word 7 is written مَّا (shadda = idgham with the previous word's
    # tanween); at isti'naf it degeminates to maa (R112 generalized)
    segments = segs_of(2, 26, [6])
    s2 = segments[1]
    assert s2.phones[0].base is Base.MEEM
    assert not s2.phones[0].geminated


def test_resume_at_wasl_hamza():
    # 1:7 stop after word 1 (صِرَٰطَ ٱلَّذِينَ | أَنْعَمْتَ...): resume
    # works; then stop after word 0 gives ibtida' on ٱلَّذِينَ with fath
    segments = segs_of(1, 7, [0])
    s2 = segments[1]
    assert s2.phones[0].base is Base.HAMZA and s2.phones[1].base is Base.FATHA


def test_segments_tile_the_ayah():
    ref = AyahRef(2, 255)
    n_words = len(TB.ayah(ref).split(" "))
    segments = segs_of(2, 255, [4, 11, 20])
    assert len(segments) == 4
    covered = []
    for seg in segments:
        ws = sorted({p.word_index for p in seg.phones})
        covered.extend(ws)
    assert covered == sorted(set(covered))  # disjoint, ordered
    assert covered[0] == 0 and covered[-1] == n_words - 1


def test_prefix_words_stable_under_stop():
    # stopping after word k leaves words 0..k-1 phone-identical to the
    # unstopped phonemization (junction between k and k+1 is the only
    # removed context)
    ref = AyahRef(2, 3)
    text = TB.ayah(ref)
    base = phonemize(text, edition="tanzil", ref=ref).segments[0].phones
    k = 2
    stopped = phonemize(text, edition="tanzil", ref=ref,
                        waqf=WaqfSpec(stops=(k,))).segments

    def sig(ph):
        return [(p.base, p.kind, p.geminated, p.ghunna, p.qalqalah,
                 p.tafkheem,
                 p.length.canonical if p.length else None)
                for p in ph]

    base_prefix = [p for p in base if p.word_index < k]
    stop_prefix = [p for p in stopped[0].phones if p.word_index < k]
    assert sig(base_prefix) == sig(stop_prefix)


def test_invalid_stop_raises():
    with pytest.raises(Exception):
        segs_of(112, 1, [40])
