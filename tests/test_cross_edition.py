"""Corpus invariant: cross-edition seg-equality (SPEC-001).

Tanzil and KFGQPC encode the same phonology under different conventions; after
per-edition decode they must produce identical seg streams — except:

- tanween MODE: KFGQPC distinguishes izhar/open forms (a dabt witness Tanzil
  lacks); compared as tanween-vs-iqlab only. P6 must derive the mode and
  assert it against the KFGQPC witness.
- word JOINING: 15:7 (لوما), 27:20 & 36:22 (ما لي) are written joined in
  KFGQPC, split in Tanzil — seg content identical, word_index shifts.
- 17:7: hamza-seat rasm variant inside لِيَسُوٓءُوا — seg streams genuinely
  differ; resolution deferred (madd classification + differential + expert).

Any OTHER divergence is a build error: a new finding must be investigated and
either fixed or added here WITH its verdict, never silently tolerated.
"""
import pytest

from quran_g2p.decode import decode_text
from quran_g2p.ortho import MaddSeg, TanweenMode
from quran_g2p.textbank import AyahRef, TextBank

WORD_JOIN_VARIANTS = {AyahRef(15, 7), AyahRef(27, 20), AyahRef(36, 22)}
# 17:7's rasm GENUINELY differs between editions (Tanzil carries the
# muhaqqiqun's restored small waw of لِيَسُوءُوا; KFGQPC prints the bare
# 'Uthmani rasm — al-Muhkam 1:168; al-Naqt 1:141), so the raw-DECODE
# comparison keeps it whitelisted. The ENGINE output does not differ:
# R013 restores the waw, and the phone-level test whitelist is EMPTY and
# must stay empty («همزة بين واوين» — al-Hujja 5:85).
DECODE_RASM_VARIANTS = {AyahRef(17, 7)}
RASM_VARIANTS: set = set()


def _brief(seg, with_word):
    if isinstance(seg, MaddSeg):
        return ("madd", seg.quality.value, seg.word_index if with_word else None)
    tan = None
    if seg.tanween:
        mode = "iqlab" if seg.tanween.mode is TanweenMode.IQLAB else "tanween"
        tan = (seg.tanween.quality.value, mode)
    return (
        seg.letter.value,
        seg.vowel.value if seg.vowel else None,
        tan,
        seg.sukun.value if seg.sukun else None,
        seg.shadda,
        seg.word_index if with_word else None,
    )


def test_cross_edition_seg_equality_whole_corpus():
    tanz, kf = TextBank.load("tanzil"), TextBank.load("kfgqpc")
    unexpected = []
    for ref in tanz.refs():
        if ref in DECODE_RASM_VARIANTS:
            continue
        with_word = ref not in WORD_JOIN_VARIANTS
        a = [_brief(s, with_word) for s in decode_text(tanz.ayah(ref), edition="tanzil").segs]
        b = [_brief(s, with_word) for s in decode_text(kf.ayah(ref), edition="kfgqpc").segs]
        if a != b:
            unexpected.append(f"{ref.surah}:{ref.ayah}")
            if len(unexpected) > 5:
                break
    assert not unexpected, f"new cross-edition divergences (investigate!): {unexpected}"


def test_cross_edition_phone_equality_whole_corpus():
    """The strongest oracle: after the full v1 pipeline, both editions emit
    identical phone streams for every ayah except the verdicted 17:7 rasm
    variant (word-join variants agree — word_index is not a phone axis)."""
    from quran_g2p.phonemize import phonemize

    tanz, kf = TextBank.load("tanzil"), TextBank.load("kfgqpc")
    unexpected = []
    for ref in tanz.refs():
        if ref in RASM_VARIANTS:
            continue
        a = [(p.base.value, p.geminated, p.ghunna)
             for s in phonemize(tanz.ayah(ref), edition="tanzil", ref=ref).segments
             for p in s.phones]
        b = [(p.base.value, p.geminated, p.ghunna)
             for s in phonemize(kf.ayah(ref), edition="kfgqpc", ref=ref).segments
             for p in s.phones]
        if a != b:
            unexpected.append(f"{ref.surah}:{ref.ayah}")
            if len(unexpected) > 5:
                break
    assert not unexpected, f"new phone-level divergences: {unexpected}"


def test_whitelisted_word_join_variants_differ_only_in_word_index():
    tanz, kf = TextBank.load("tanzil"), TextBank.load("kfgqpc")
    for ref in WORD_JOIN_VARIANTS:
        a = [_brief(s, False) for s in decode_text(tanz.ayah(ref), edition="tanzil").segs]
        b = [_brief(s, False) for s in decode_text(kf.ayah(ref), edition="kfgqpc").segs]
        assert a == b, f"{ref} differs beyond word_index"
