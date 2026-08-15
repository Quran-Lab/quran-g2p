"""P1 orthographic rules that transform the decoded seg stream.

R011 — الحروف المقطعة (muqatta'at spell-out), SPEC-011.

The 29 surah openings are written as bare letters but recited as letter
NAMES. This rule replaces word 0 of the opening ayah with the spelled-out
segs, carrying each written letter's madda witness onto the name's madd seg
(or onto the name-initial consonant for عين, whose stretchable element is the
leen yeh). Name-final consonants get MARKED sukun: Shatibiyyah default is
izhar at the يس/ن junctions (khilaf knob lives with R012).
"""
from __future__ import annotations

from ..ir import Base, RuleApp
from ..ortho import ConsSeg, DecodeError, MaddSeg, MaddSource, SukunKind, VQ
from .registry import register

# (surah, ayah) -> written letter sequence (identity check, fail-closed)
OPENINGS: dict[tuple[int, int], str] = {
    (2, 1): "ALM", (3, 1): "ALM", (7, 1): "ALMS", (10, 1): "ALR", (11, 1): "ALR",
    (12, 1): "ALR", (13, 1): "ALMR", (14, 1): "ALR", (15, 1): "ALR",
    (19, 1): "KHYES", (20, 1): "TH", (26, 1): "TSM", (27, 1): "TS", (28, 1): "TSM",
    (29, 1): "ALM", (30, 1): "ALM", (31, 1): "ALM", (32, 1): "ALM", (36, 1): "YS",
    (38, 1): "S", (40, 1): "HM", (41, 1): "HM", (42, 1): "HM", (42, 2): "ESQ",
    (43, 1): "HM", (44, 1): "HM", (45, 1): "HM", (46, 1): "HM", (50, 1): "Q",
    (68, 1): "N",
}

# letter key -> written Base expected in the raw decode ('S'/'H' resolved in _expected)
_WRITTEN: dict[str, Base] = {
    "A": Base.ALEF_MADD,  # raw decode emits MaddSeg for the bare alef
    "L": Base.LAM, "M": Base.MEEM, "R": Base.REH, "K": Base.KAF,
    "Y": Base.YEH, "E": Base.AIN, "T": Base.TAH, "Q": Base.QAF, "N": Base.NOON,
}


def _expected(key: str, seq: str, pos: int) -> Base:
    # 'S' is SAD in ALMS/KHYES/S (ص) but SEEN in TSM/TS/YS/ESQ (س);
    # disambiguate by the letters around it.
    if key == "S":
        return Base.SAD if seq in ("ALMS", "KHYES", "S") else Base.SEEN
    if key == "H":
        # H is HEH in TH/KHYES (ه) but HAH in HM (ح)
        return Base.HEH if seq in ("TH", "KHYES") else Base.HAH
    return _WRITTEN[key]


def _name_segs(key: str, seq: str, span, word, madda: bool,
               noon_marked: bool = False) -> list:
    C, M = ConsSeg, MaddSeg

    def cons(base, vowel=None, sukun=None, first_madda=False):
        return C(base, vowel, None, sukun, False, None, first_madda, False, span, word)

    def madd(q, witness):
        return M(q, MaddSource.LETTER_NAME, witness, span, word)

    s = SukunKind.MARKED
    # Name-final noons are BARE (assimilation runs between letter names:
    # 'ayn's noon ikhfas into saad, seen's noon idghams into meem) EXCEPT the
    # witnessed izhar junctions يس/ن before waw (noon_marked=True there).
    sn = SukunKind.MARKED if noon_marked else SukunKind.BARE
    base = _expected(key, seq, 0)
    if key == "A":
        return [cons(Base.HAMZA, VQ.A), cons(Base.LAM, VQ.I), cons(Base.FEH, sukun=s)]
    if key == "L":
        return [cons(Base.LAM, VQ.A), madd(VQ.A, madda), cons(Base.MEEM, sukun=s)]
    if key == "M":
        return [cons(Base.MEEM, VQ.I), madd(VQ.I, madda), cons(Base.MEEM, sukun=s)]
    if key == "S" and base is Base.SAD:
        return [cons(Base.SAD, VQ.A), madd(VQ.A, madda), cons(Base.DAL, sukun=s)]
    if key == "S":
        return [cons(Base.SEEN, VQ.I), madd(VQ.I, madda), cons(Base.NOON, sukun=sn)]
    if key == "R":
        return [cons(Base.REH, VQ.A), madd(VQ.A, madda)]
    if key == "K":
        return [cons(Base.KAF, VQ.A), madd(VQ.A, madda), cons(Base.FEH, sukun=s)]
    if key == "H" and base is Base.HEH:
        return [cons(Base.HEH, VQ.A), madd(VQ.A, madda)]
    if key == "H":
        return [cons(Base.HAH, VQ.A), madd(VQ.A, madda)]
    if key == "Y":
        return [cons(Base.YEH, VQ.A), madd(VQ.A, madda)]
    if key == "E":
        # عَيْنْ: stretchable element is the leen yeh; madda witness rides the
        # name-initial 'ayn ConsSeg ({4,6} khilaf resolved in P10).
        return [cons(Base.AIN, VQ.A, first_madda=madda),
                cons(Base.YEH, sukun=s), cons(Base.NOON, sukun=sn)]
    if key == "T":
        return [cons(Base.TAH, VQ.A), madd(VQ.A, madda)]
    if key == "Q":
        return [cons(Base.QAF, VQ.A), madd(VQ.A, madda), cons(Base.FEH, sukun=s)]
    if key == "N":
        return [cons(Base.NOON, VQ.U), madd(VQ.U, madda), cons(Base.NOON, sukun=sn)]
    raise DecodeError(f"unknown muqatta'at letter key {key!r}")


class R012SeenSadKhilaf:
    """R012 — seen/sad khilaf words (SPEC-012).

    Written saad recited seen at 2:245 (يَبْصُۜطُ) and 7:69 (بَصْۜطَةً) per the
    Hafs/Shatibiyyah mashhur; 52:37 keeps saad (muqaddam); 88:22 plain saad.
    The small seen mark (Tanzil 06DC/06E3; KFGQPC 06DC) is the in-text witness
    at the three marked sites. Config knobs flip each site.
    """

    rule_id = "R012_SEEN_SAD"
    spec = "SPEC-012"
    phase = 1

    SITES = {
        (2, 245): "bast_2_245_seen",
        (7, 69): "basta_7_69_seen",
        (52, 37): "musaytirun_52_37_seen",
        (88, 22): "musaytir_88_22_seen",
    }

    def apply(self, ctx) -> None:
        if ctx.ref is None:
            return
        knob = self.SITES.get((ctx.ref.surah, ctx.ref.ayah))
        if knob is None or not getattr(ctx.config, knob):
            return
        sad_indices = [i for i, s in enumerate(ctx.segs)
                       if isinstance(s, ConsSeg) and s.letter is Base.SAD]
        if len(sad_indices) != 1:
            raise DecodeError(
                f"R012 at {ctx.ref}: expected exactly one saad seg, found {len(sad_indices)}"
            )
        i = sad_indices[0]
        old = ctx.segs[i]
        ctx.segs[i] = ConsSeg(Base.SEEN, old.vowel, old.tanween, old.sukun, old.shadda,
                              old.hamza_carrier, old.madda, old.iqlab_mark,
                              old.span, old.word_index)
        ctx.trace.append(RuleApp(self.rule_id, self.spec, old.span, note=knob))


@register
class R011Muqattaat:
    rule_id = "R011_MUQATTAAT"
    spec = "SPEC-011"
    phase = 1

    def apply(self, ctx) -> None:
        if ctx.ref is None:
            return
        key = (ctx.ref.surah, ctx.ref.ayah)
        seq = OPENINGS.get(key)
        if seq is None:
            return
        word0 = [s for s in ctx.segs if s.word_index == 0]
        rest = [s for s in ctx.segs if s.word_index != 0]
        if len(word0) != len(seq):
            raise DecodeError(
                f"muqatta'at {key}: expected {len(seq)} letters, decoded {len(word0)}"
            )
        out = []
        for name_idx, (k, seg) in enumerate(zip(seq, word0)):
            expected = _expected(k, seq, 0)
            if isinstance(seg, MaddSeg):
                if k != "A":
                    raise DecodeError(f"muqatta'at {key}: madd seg where {k} expected")
            elif seg.letter is not expected:
                raise DecodeError(
                    f"muqatta'at {key}: letter {seg.letter} where {expected} expected"
                )
            madda = seg.madda
            # each letter NAME is its own recitation word (alif, laam, meem…)
            noon_marked = (key in ((36, 1), (68, 1))
                           and name_idx == len(seq) - 1)
            out.extend(_name_segs(k, seq, seg.span, name_idx, madda,
                                  noon_marked=noon_marked))
        shift = len(seq) - 1
        if shift:
            rest = [_shift_word(s, shift) for s in rest]
        ctx.segs = out + rest
        ctx.trace.append(RuleApp(self.rule_id, self.spec, (0, 0), note=f"{key} {seq}"))


def _shift_word(seg, shift: int):
    from dataclasses import replace
    return replace(seg, word_index=seg.word_index + shift)


class R013ElidedWawLiyasuu:
    """R013 — the rasm-elided waw of لِيَسُوءُوا (17:7), SPEC-012.

    The 'Uthmani rasm writes ONE waw («اجتمعت المصاحف على حذف إحدى الواوين»
    — al-Dani, al-Muhkam 1:168-169), and the muhaqqiqun restore the elided
    first waw in the dabt («فتلحق قبلها واوًا أخرى بالحمراء وهي الأصلية» —
    al-Naqt 1:141-142; Dalil al-Hayran 1:405-406 adds the madd sign on it
    «لوجود سببه»). The recitation is li-yasūʾū — «همزة بين واوين» (al-Hujja
    5:85). Tanzil's encoding carries the restored small waw; KFGQPC prints
    the bare rasm — this rule inserts the waw-madd where an edition lacks
    it, so both converge on the recited form (muttasil on the first waw,
    Hidayat al-Qari 1:280-281).
    """

    rule_id = "R013_ELIDED_WAW_LIYASUU"
    spec = "SPEC-012"
    phase = 1

    def apply(self, ctx) -> None:
        if ctx.ref is None or (ctx.ref.surah, ctx.ref.ayah) != (17, 7):
            return
        from ..ortho import VQ
        for i, seg in enumerate(ctx.segs):
            if not (isinstance(seg, ConsSeg) and seg.letter is Base.SEEN
                    and seg.vowel is VQ.U):
                continue
            nxt = ctx.segs[i + 1] if i + 1 < len(ctx.segs) else None
            if isinstance(nxt, MaddSeg):
                return  # the restored waw is already encoded (Tanzil)
            if isinstance(nxt, ConsSeg) and nxt.letter is Base.HAMZA:
                madd = MaddSeg(VQ.U, MaddSource.SMALL_WAW, True,
                               seg.span, seg.word_index)
                ctx.segs = ctx.segs[: i + 1] + [madd] + ctx.segs[i + 1:]
                ctx.trace.append(RuleApp(self.rule_id, self.spec, seg.span))
                return


register(R012SeenSadKhilaf)
register(R013ElidedWawLiyasuu)
