"""Token layer (Part B1, SPEC-003 exports): letter-group tokens.

TOKEN := BASE (shadda?) ('^'?) ('~'?) (haraka?) (residual?) (':' LEN)?

One token = one acoustic dwell: a consonant with its gemination/tafkheem
marker and haraka, or a madd letter with its length tag. The '^' tafkheem
axis exists ONLY for reh/lam (the letters whose tafkheem is not implied by
identity); everything else keeps tafkheem in metadata. Ghunna length is
metadata in v1 (single-convention value), revisited at the A/B.

Lengths in tokens are the CANONICAL values until alignment fills realized
lengths (S3); the formatter reads realized_len when present.
"""
from __future__ import annotations

from dataclasses import dataclass

from . import codepoints as cp
from .ir import Base, Phone

_CONS_CHAR = {
    Base.HAMZA: cp.HAMZA, Base.BEH: cp.BEH, Base.TEH: cp.TEH,
    Base.THEH: cp.THEH, Base.JEEM: cp.JEEM, Base.HAH: cp.HAH,
    Base.KHAH: cp.KHAH, Base.DAL: cp.DAL, Base.THAL: cp.THAL,
    Base.REH: cp.REH, Base.ZAIN: cp.ZAIN, Base.SEEN: cp.SEEN,
    Base.SHEEN: cp.SHEEN, Base.SAD: cp.SAD, Base.DAD: cp.DAD,
    Base.TAH: cp.TAH, Base.ZAH: cp.ZAH, Base.AIN: cp.AIN,
    Base.GHAIN: cp.GHAIN, Base.FEH: cp.FEH, Base.QAF: cp.QAF,
    Base.KAF: cp.KAF, Base.LAM: cp.LAM, Base.MEEM: cp.MEEM,
    Base.NOON: cp.NOON, Base.HEH: cp.HEH, Base.WAW: cp.WAW,
    Base.YEH: cp.YEH,
    Base.NOON_MUKHFAH: cp.NOON_GHUNNA,             # ں
    Base.MEEM_MUKHFAH: cp.SIGN_SINDHI_POSTPOSITION_MEN,  # ۾
    Base.HAMZA_MUSAHHALA: cp.ALEF_WITH_WAVY_HAMZA_ABOVE,  # ٲ
    Base.DAMMA_MUKHTALASA: cp.SMALL_DAMMA,         # ؙ
}
_VOWEL_CHAR = {
    Base.FATHA: cp.FATHA, Base.DAMMA: cp.DAMMA, Base.KASRA: cp.KASRA,
    Base.FATHA_IMALA: cp.EMPTY_CENTRE_LOW_STOP,    # ۪
}
_MADD_CHAR = {
    Base.ALEF_MADD: cp.ALEF, Base.WAW_MADD: cp.SMALL_WAW,
    Base.YEH_MADD: cp.SMALL_YEH, Base.ALEF_IMALA: cp.TATWEEL,
}
_QLQ = cp.TCHEHEH            # ڇ (qalqalah residual, oracle-compatible)
_SAKT = cp.SMALL_HIGH_SEEN   # ۜ

_TAFKHEEM_AXIS = {Base.REH, Base.LAM}


@dataclass(frozen=True)
class Token:
    text: str


class TokenError(Exception):
    pass


def phones_to_tokens(phones: list[Phone]) -> list[Token]:
    out: list[Token] = []
    i = 0
    n = len(phones)
    while i < n:
        p = phones[i]
        if p.kind == "madd":
            length = int(p.realized_len or (p.length.canonical if p.length else 2))
            out.append(Token(f"{_MADD_CHAR[p.base]}:{length}"))
            i += 1
            continue
        if p.kind == "vowel":
            # A vowel with no preceding consonant in the token stream would be
            # a structural bug — vowels are consumed with their consonant.
            raise TokenError(f"orphan vowel {p.base} at phone {i}")
        # consonant (+ optional following vowel)
        text = _CONS_CHAR[p.base]
        if p.geminated:
            text += cp.SHADDA
        if p.base in _TAFKHEEM_AXIS and p.tafkheem == "mofakham":
            text += "^"
        # '~' ghunna axis: a NAQIS idgham target (waw/yeh nasalized without
        # gemination) has no shadda and no mukhfah base to betray its ghunna;
        # every other carrier is already token-visible. ASCII like '^'.
        if (p.base in (Base.WAW, Base.YEH) and p.kind == "consonant"
                and p.ghunna == "idgham" and not p.geminated):
            text += "~"
        if i + 1 < n and phones[i + 1].kind == "vowel":
            text += _VOWEL_CHAR[phones[i + 1].base]
            i += 1
        if p.qalqalah is not None:
            text += _QLQ
        if p.sakt_after:
            text += _SAKT
        # a consonant carrying a LEEN madd length gets the length tag; the
        # discriminator is kind=="free" (leen specs are free {2,4,6}/{4,6};
        # ghunna-duration prescriptions are fixed {2} and stay OFF the token
        # axis in v1 — metadata in rule_index, revisited at the A/B).
        if (p.length is not None and p.length.kind == "free"
                and p.base in (Base.WAW, Base.YEH)):
            length = int(p.realized_len or p.length.canonical)
            text += f":{length}"
        out.append(Token(text))
        i += 1
    return out


def parse_token(text: str) -> Token:
    """Validate a token's surface form; returns the Token (identity check).

    Grammar: base char, then optional shadda, optional '^', optional '~',
    optional haraka,
    optional residuals (qalqalah/sakt), optional ':LEN'.
    """
    if not text:
        raise TokenError("empty token")
    body, sep, length = text.partition(":")
    if sep and (not length.isdigit() or not (1 <= int(length) <= 8)):
        raise TokenError(f"bad length in {text!r}")
    chars = list(body)
    idx = 0
    known_bases = set(_CONS_CHAR.values()) | set(_MADD_CHAR.values())
    if chars[idx] not in known_bases:
        raise TokenError(f"unknown base in {text!r}")
    idx += 1
    if idx < len(chars) and chars[idx] == cp.SHADDA:
        idx += 1
    if idx < len(chars) and chars[idx] == "^":
        idx += 1
    if idx < len(chars) and chars[idx] == "~":
        idx += 1
    if idx < len(chars) and chars[idx] in set(_VOWEL_CHAR.values()):
        idx += 1
    while idx < len(chars) and chars[idx] in (_QLQ, _SAKT):
        idx += 1
    if idx != len(chars):
        raise TokenError(f"trailing garbage in {text!r}")
    return Token(text)
