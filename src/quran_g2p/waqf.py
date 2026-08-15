"""WaqfSpec: where the reciter stops (SPEC-004) + waqf-variant eligibility.

v1 scope: ayah-end waqf only (the default). Stops at arbitrary word indices
are the input surface the rest of the engine is built against; segmentation
by stop list lands with P2's full implementation.
"""
from __future__ import annotations

from dataclasses import dataclass

from .ir import Base, Phone

SUKUN = "sukun"
RAWM = "rawm"
ISHMAM = "ishmam"

_SUKUN_ONLY = frozenset({SUKUN})
_NO_ISHMAM = frozenset({SUKUN, RAWM})
_ALL = frozenset({SUKUN, RAWM, ISHMAM})

#: contexts that forbid isharah on the pronoun haa under the tafsil madhhab
#: (damm, sakin waw, kasr, sakin yaa before the haa)
_PRONOUN_BLOCKERS = frozenset(
    {Base.DAMMA, Base.KASRA, Base.WAW, Base.YEH, Base.WAW_MADD, Base.YEH_MADD}
)


@dataclass(frozen=True)
class WaqfSpec:
    #: word indices after which the reciter stops; the ayah end is always a stop.
    stops: tuple[int, ...] = ()

    @classmethod
    def ayah_end(cls) -> "WaqfSpec":
        return cls(())


def isharah_modes(
    final_haraka: Base | None,
    prev: Phone | None,
    *,
    pronoun_haa: bool = False,
    haa_sakt: bool = False,
    ta_marbuta: bool = False,
    arid_haraka: bool = False,
) -> frozenset[str]:
    """Waqf variants legal on a final letter whose wasl haraka is dropped.

    `final_haraka` is the wasl-form haraka the pausal iskan removes (None if
    the final letter is already sakin in wasl); `prev` is the phone
    immediately before that final letter.

    General legality (SPEC-123): rawm indicates damm and kasr only; ishmam
    is the lip-rounding of damm only; neither ever runs on fath. A final
    already sakin in wasl offers nothing to indicate, and haa as-sakt is by
    definition a sakin haa with no underlying haraka, so both take pure
    sukun. On the pronoun haa the tafsil madhhab governs (SPEC-183): no
    rawm/ishmam when the haa follows damm, sakin waw, kasr, or sakin yaa;
    the modes stay open after fath, alif, or a sakin sahih. A prev phone of
    consonant waw/yeh is positionally sakin here (a haraka would otherwise
    sit between it and the final letter), which folds the leen yaa of
    عَلَيْهُ into the blocked set without a separate flag.
    """
    if haa_sakt or final_haraka is None:
        return _SUKUN_ONLY
    # al-Nashr 2:122-124: of the five sukun-only asnaf, two need flags the
    # haraka alone cannot betray — the waqf-haa replacing ta marbuta (it
    # carries no i'rab; stopping on a WRITTEN open taa instead keeps the
    # isharah, 2:126) and any 'arid haraka (naql / iltiqa al-sakinayn).
    # Wasl-sakin finals and un-tanweened fath are covered below; meem
    # al-jam' is wasl-sakin for Hafs and lands in the None branch.
    if ta_marbuta or arid_haraka:
        return _SUKUN_ONLY
    if final_haraka is Base.FATHA:
        return _SUKUN_ONLY
    if pronoun_haa and prev is not None:
        prev_base = prev.base if isinstance(prev, Phone) else prev
        if prev_base in _PRONOUN_BLOCKERS:
            return _SUKUN_ONLY
    if final_haraka is Base.DAMMA:
        return _ALL
    if final_haraka is Base.KASRA:
        return _NO_ISHMAM
    return _SUKUN_ONLY
