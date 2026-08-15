"""Expand our Phone streams into the reference engine's 42-symbol repeat-encoded convention.

QUARANTINE: this module encodes THEIR representation for differential testing
only. Documented conventions (SPEC-000 differential notes):
  - duration by repetition: madd length L -> L copies of the madd letter;
    plain waw/yaa madds use the consonant chars, silah smalls use ۥ/ۦ
  - gemination: 2 copies; ghunna-bearing geminates: `ghunna_repeat` copies
  - ikhfa carriers: ں/۾ x `ikhfa_repeat`
  - qalqalah -> trailing ڇ ; sakt -> trailing ۜ
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from quran_g2p.ir import Base, Phone  # noqa: E402

_CONS = {
    Base.HAMZA: "ء", Base.BEH: "ب", Base.TEH: "ت",
    Base.THEH: "ث", Base.JEEM: "ج", Base.HAH: "ح",
    Base.KHAH: "خ", Base.DAL: "د", Base.THAL: "ذ",
    Base.REH: "ر", Base.ZAIN: "ز", Base.SEEN: "س",
    Base.SHEEN: "ش", Base.SAD: "ص", Base.DAD: "ض",
    Base.TAH: "ط", Base.ZAH: "ظ", Base.AIN: "ع",
    Base.GHAIN: "غ", Base.FEH: "ف", Base.QAF: "ق",
    Base.KAF: "ك", Base.LAM: "ل", Base.MEEM: "م",
    Base.NOON: "ن", Base.HEH: "ه", Base.WAW: "و",
    Base.YEH: "ي", Base.HAMZA_MUSAHHALA: "ٲ",
    Base.NOON_MUKHFAH: "ں", Base.MEEM_MUKHFAH: "۾",
    Base.DAMMA_MUKHTALASA: "ؙ",
}
_VOWEL = {Base.FATHA: "َ", Base.DAMMA: "ُ", Base.KASRA: "ِ",
          Base.FATHA_IMALA: "۪"}
# the reference engine uses the small letters for ALL long u/i madds (verified 1:1: ررَحِۦۦۦۦم)
_MADD_CHAR = {Base.ALEF_MADD: "ا", Base.WAW_MADD: "ۥ",
              Base.YEH_MADD: "ۦ", Base.ALEF_IMALA: "ـ"}
_QLQ = "ڇ"
_SAKT = "ۜ"


def _note(p: Phone) -> str:
    return p.provenance[0].note if p.provenance else ""


def expand(phones: list[Phone], ghunna_repeat: int = 4,
           ikhfa_repeat: int = 3) -> str:
    out: list[str] = []
    last_word = None
    prev_phone: Phone | None = None
    for p in phones:
        if last_word is not None and p.word_index != last_word:
            # the reference engine merges words ONLY across cross-word assimilation: after an
            # ikhfa carrier, or where an idgham consumed the previous word's
            # last letter (R141/R142 provenance on the target). Wasl-elision
            # junctions keep their space.
            rules = {a.rule_id for a in p.provenance}
            merged = (
                (prev_phone is not None and prev_phone.base in
                 (Base.NOON_MUKHFAH, Base.MEEM_MUKHFAH))
                or bool(rules & {"R141_IDGHAM_GHUNNA", "R142_IDGHAM_BILA_GHUNNA",
                                 "R133_R160_IDGHAM_KAMIL", "R160_MUTAMATHILAYN"})
            )
            if not merged:
                out.append(" ")
        last_word = p.word_index
        prev_phone = p
        if p.kind == "vowel":
            out.append(_VOWEL[p.base])
            continue
        if p.kind == "madd":
            length = p.length.canonical if p.length else 2
            out.append(_MADD_CHAR[p.base] * length)
            continue
        # consonant
        ch = _CONS[p.base]
        if p.base in (Base.NOON_MUKHFAH, Base.MEEM_MUKHFAH):
            out.append(ch * ikhfa_repeat)
        elif p.geminated and p.ghunna in ("mushaddadah", "idgham"):
            out.append(ch * ghunna_repeat)
        elif p.ghunna == "idgham":
            # naqis idgham target (waw/yeh) and non-geminated letter-name
            # targets: repeated to carry the ghunna in their convention
            out.append(ch * 3)
        elif p.geminated:
            out.append(ch * 2)
        elif p.length is not None:
            # consonant carrying a madd length (leen): their convention writes
            # the consonant PLUS len stretch copies (khawf len2 -> ووو)
            out.append(ch * (1 + p.length.canonical))
        else:
            out.append(ch)
        if p.qalqalah is not None:
            out.append(_QLQ)
        if p.sakt_after:
            out.append(_SAKT)
    return "".join(out)
