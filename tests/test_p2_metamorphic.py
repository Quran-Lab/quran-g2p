"""P2 metamorphic invariants (plan A5b), sampled corpus-wide.

For every sampled ayah and every valid stop position k:
  (a) segments tile the ayah's words, disjoint and in order;
  (b) words before k are phone-identical to the unstopped ayah;
  (c) words after k+1 are phone-identical to the unstopped ayah
      (only the stopped word's tail and the resumed word's head may
      change);
  (d) every segment ends legally for pause (never on a bare short
      vowel).
"""
import pytest

from quran_g2p.phonemize import phonemize
from quran_g2p.textbank import AyahRef, TextBank
from quran_g2p.waqf import WaqfSpec

TB = TextBank.load("tanzil")

SAMPLE = [
    (1, 7), (2, 3), (2, 26), (2, 61), (2, 180), (2, 255), (2, 282),
    (3, 155), (4, 176), (7, 176), (11, 42), (11, 81), (12, 11), (12, 99),
    (18, 38), (19, 1), (24, 52), (25, 69), (27, 36), (30, 54), (33, 10),
    (36, 52), (41, 44), (43, 49), (54, 16), (75, 27), (76, 4), (76, 15),
    (77, 20), (89, 4), (96, 15), (112, 1),
]


def sig(p):
    return (p.base, p.kind, p.geminated, p.ghunna, p.qalqalah, p.tafkheem,
            p.length.canonical if p.length else None)


def by_word(phones):
    d = {}
    for p in phones:
        d.setdefault(p.word_index, []).append(sig(p))
    return d


@pytest.mark.parametrize("s,a", SAMPLE, ids=[f"{s}:{a}" for s, a in SAMPLE])
def test_every_stop_position(s, a):
    ref = AyahRef(s, a)
    text = TB.ayah(ref)
    n_words = len(text.split(" "))
    base = by_word(phonemize(text, edition="tanzil", ref=ref)
                   .segments[0].phones)
    for k in range(n_words - 1):
        res = phonemize(text, edition="tanzil", ref=ref,
                        waqf=WaqfSpec(stops=(k,)))
        assert len(res.segments) == 2, (s, a, k)
        seg1, seg2 = res.segments

        # (a) tiling
        w1 = sorted({p.word_index for p in seg1.phones})
        w2 = sorted({p.word_index for p in seg2.phones})
        assert w1 and w2 and w1[-1] < w2[0], (s, a, k)
        assert w1[0] == 0 and w2[-1] == n_words - 1, (s, a, k)

        stopped = by_word(seg1.phones) | by_word(seg2.phones)
        # (b) prefix stability
        for w in range(0, k):
            assert stopped.get(w) == base.get(w), (s, a, k, "prefix", w)
        # (c) suffix stability
        for w in range(k + 2, n_words):
            assert stopped.get(w) == base.get(w), (s, a, k, "suffix", w)
        # (d) legal pausal ending
        for seg in (seg1, seg2):
            assert seg.phones, (s, a, k)
            assert seg.phones[-1].kind != "vowel", (s, a, k, "vowel-final")


def test_cross_edition_segments_agree():
    # the split is edition-agnostic: same stop, same phones, both editions
    from quran_g2p.ir import Base
    tbk = TextBank.load("kfgqpc")
    for s, a, k in ((2, 26, 6), (112, 1, 0), (76, 4, 3), (2, 255, 11)):
        ref = AyahRef(s, a)
        outs = []
        for ed, tb in (("tanzil", TB), ("kfgqpc", tbk)):
            res = phonemize(tb.ayah(ref), edition=ed, ref=ref,
                            waqf=WaqfSpec(stops=(k,)))
            outs.append([[sig(p) for p in seg.phones]
                         for seg in res.segments])
        assert outs[0] == outs[1], (s, a, k)
