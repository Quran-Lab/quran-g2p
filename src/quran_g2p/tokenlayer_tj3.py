"""tj3: the phone vocabulary (one token per sound, lengths and tajweed qualities off the token axis).

    <blk> |  28 consonants  ں (ikhfa nasal)  a i u  aa ii uu  <foreign>          38 classes, blank 0

What a token carries, and what it does not:
  - consonant identity (iqlab / ikhfa shafawi meem -> م; tasheel hamza -> ء); the ikhfa nasal ں is its own sound
    (a nasal at the next consonant's place, not the alveolar ن), so it keeps its own token;
  - vowel quality and the phonemic short/long contrast: a short vowel + its madd letter is ONE long vowel token
    (fatha + alef -> aa, damma + small waw -> uu, kasra + small yeh -> ii; the 11:41 imala vowel -> aa);
  - '|' between words (the H-time chain puts its optional pause states there; a CTC target may drop it).

Measured by the timing head, never tokens: madd / leen counts, gemination (shadda = the consonant held: one token),
ghunna length, rawm (a reduced vowel: the vowel token, the face head says rawm), sakt (a pause).  Attribute heads, never
tokens: tafkheem (reh, lam, vowels), qalqalah, ghunna class (incl. naqis idgham on waw / yeh), imala, tasheel.
Ishmam is not heard (its audio is the sukun form's): no token.  Ikhtilas (12:11) is a short damma: u.

  phones_to_tj3(phones)       Phone IR (objects or layer dicts) -> tj3 tokens, '|' between words
  phones_to_tj3_units(units)  the same over labeller units, plus each unit's first tj3 index
  tj2_to_tj3(tokens, vid)     a built record's tj2 units + its V_id ids -> (tj3 tokens, unit -> tj3 index of its first
                              token); every V_id phone is checked against the unit it belongs to
"""
from __future__ import annotations

from . import codepoints as cp

VOCAB_ID = "tj3"
BLANK, WORD = "<blk>", "|"
FOREIGN = "<foreign>"
CONSONANTS = [cp.HAMZA, cp.BEH, cp.TEH, cp.THEH, cp.JEEM, cp.HAH, cp.KHAH, cp.DAL, cp.THAL, cp.REH, cp.ZAIN, cp.SEEN,
              cp.SHEEN, cp.SAD, cp.DAD, cp.TAH, cp.ZAH, cp.AIN, cp.GHAIN, cp.FEH, cp.QAF, cp.KAF, cp.LAM, cp.MEEM,
              cp.NOON, cp.HEH, cp.WAW, cp.YEH]
IKHFA = cp.NOON_GHUNNA
SHORT = {"fatha": "a", "kasra": "i", "damma": "u"}
LONG = {"a": "aa", "i": "ii", "u": "uu"}
MADD_LONG = {"alef_madd": "aa", "waw_madd": "uu", "yeh_madd": "ii", "alef_imala": "aa"}
TOKENS = [BLANK, WORD] + CONSONANTS + [IKHFA] + ["a", "i", "u", "aa", "ii", "uu"] + [FOREIGN]
INDEX = {t: i for i, t in enumerate(TOKENS)}

_CONS = {"hamza": cp.HAMZA, "beh": cp.BEH, "teh": cp.TEH, "theh": cp.THEH, "jeem": cp.JEEM, "hah": cp.HAH,
         "khah": cp.KHAH, "dal": cp.DAL, "thal": cp.THAL, "reh": cp.REH, "zain": cp.ZAIN, "seen": cp.SEEN,
         "sheen": cp.SHEEN, "sad": cp.SAD, "dad": cp.DAD, "tah": cp.TAH, "zah": cp.ZAH, "ain": cp.AIN,
         "ghain": cp.GHAIN, "feh": cp.FEH, "qaf": cp.QAF, "kaf": cp.KAF, "lam": cp.LAM, "meem": cp.MEEM,
         "noon": cp.NOON, "heh": cp.HEH, "waw": cp.WAW, "yeh": cp.YEH,
         "noon_mukhfah": IKHFA, "meem_mukhfah": cp.MEEM, "hamza_musahhala": cp.HAMZA}
_VOWEL = {"fatha": "a", "kasra": "i", "damma": "u", "fatha_imala": "a", "damma_mukhtalasa": "u"}


class Tj3Error(ValueError):
    pass


def _get(p, k):
    v = p.get(k) if isinstance(p, dict) else getattr(p, k)
    return getattr(v, "value", v)          # Base enum -> its string


def _emit(out: list, base: str):
    """Append one phone (by IR base name) to a tj3 stream."""
    if base in MADD_LONG:
        long = MADD_LONG[base]
        if out and out[-1] in LONG:                         # the short vowel before its madd letter
            out[-1] = long
        else:
            out.append(long)
    elif base in _VOWEL:
        out.append(_VOWEL[base])
    elif base in _CONS:
        out.append(_CONS[base])
    elif base == FOREIGN:
        if not out or out[-1] != FOREIGN:
            out.append(FOREIGN)
    else:
        raise Tj3Error(f"no tj3 sound for phone base {base!r}")


def phones_to_tj3(phones, boundaries: bool = True) -> list:
    return phones_to_tj3_units([[p] for p in phones], boundaries)[0]


def phones_to_tj3_units(units, boundaries: bool = True) -> tuple:
    """units: phone lists (a labeller unit each, e.g. consonant + its vowel) -> (tj3 tokens, first): first[k] is the
    tj3 index of the token unit k's first phone became (a madd unit: the long vowel it merged into)."""
    out, first, prev = [], [], None
    for unit in units:
        for n, p in enumerate(unit):
            w = _get(p, "word_index")
            if boundaries and prev is not None and w != prev and out and out[-1] != WORD:
                out.append(WORD)
            _emit(out, _get(p, "base"))
            if n == 0:
                first.append(len(out) - 1)
            prev = w
    return out, first


# tj2 unit -> the IR bases of its phones, in order (the V_id stream records them with BASE_MERGES applied)
_TJ2_CONS = {v: k for k, v in _CONS.items() if k not in ("meem_mukhfah", "hamza_musahhala")}
_TJ2_CONS.update({cp.SIGN_SINDHI_POSTPOSITION_MEN: "meem_mukhfah", cp.ALEF_WITH_WAVY_HAMZA_ABOVE: "hamza_musahhala",
                  cp.SMALL_DAMMA: "damma_mukhtalasa"})
_TJ2_MADD = {cp.ALEF: "alef_madd", cp.SMALL_WAW: "waw_madd", cp.SMALL_YEH: "yeh_madd", cp.TATWEEL: "alef_imala"}
_TJ2_VOWEL = {cp.FATHA: "fatha", cp.DAMMA: "damma", cp.KASRA: "kasra", cp.EMPTY_CENTRE_LOW_STOP: "fatha_imala"}
_MARKS = {cp.SHADDA, "^", "~", "=", cp.TCHEHEH, cp.SMALL_HIGH_SEEN}
# V_id merges (tajweedformer/vocab.py BASE_MERGES): what the record's id stream holds for each base
_VID_MERGE = {"noon_mukhfah": "noon", "meem_mukhfah": "meem", "hamza_musahhala": "hamza", "alef_imala": "alef_madd",
              "fatha_imala": "fatha", "damma_mukhtalasa": "damma"}


def tj2_unit_bases(tok: str) -> list:
    """The IR bases of one tj2 token's phones (consonant [+ vowel], or one madd), length / markers dropped."""
    body = tok.split(":", 1)[0]
    if not body:
        raise Tj3Error(f"empty tj2 token {tok!r}")
    if body[0] in _TJ2_MADD:
        if len(body) != 1:
            raise Tj3Error(f"madd token with marks {tok!r}")
        return [_TJ2_MADD[body[0]]]
    if body[0] not in _TJ2_CONS:
        raise Tj3Error(f"unknown tj2 base in {tok!r}")
    out = [_TJ2_CONS[body[0]]]
    for ch in body[1:]:
        if ch in _TJ2_VOWEL:
            out.append(_TJ2_VOWEL[ch])
        elif ch not in _MARKS:
            raise Tj3Error(f"unknown mark {ch!r} in {tok!r}")
    return out


def tj2_to_tj3(tokens, vid, id_classes) -> tuple:
    """A built record's tj2 units + V_id ids (with '|') -> (tj3 tokens with '|', unit_first): unit_first[k] is the tj3
    index of unit k's first token (a madd unit points at the long vowel it merged into).  id_classes is V_id's class
    list (tajweedformer.vocab.ID_CLASSES); every V_id phone must equal the unit phone it is walked against."""
    ids = [id_classes[i] for i in vid]
    j, out, first = 0, [], []
    for k, tok in enumerate(tokens):
        bases = tj2_unit_bases(tok)
        unit_first = None
        for b in bases:
            if j < len(ids) and ids[j] == WORD:
                if out and out[-1] != WORD:
                    out.append(WORD)
                j += 1
            want = _VID_MERGE.get(b, b)
            if j >= len(ids) or ids[j] != want:
                got = ids[j] if j < len(ids) else "<end>"
                raise Tj3Error(f"unit {k} {tok!r}: V_id has {got!r} where {want!r} is expected")
            j += 1
            n0 = len(out)
            _emit(out, b)
            if unit_first is None:
                unit_first = len(out) - 1 if len(out) == n0 else n0
        first.append(unit_first)
    if any(x != WORD for x in ids[j:]):
        raise Tj3Error(f"V_id has {len(ids) - j} phones after the last unit")
    return out, first
