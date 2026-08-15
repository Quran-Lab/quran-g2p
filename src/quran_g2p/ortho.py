"""P1 orthographic segment types: the decoder's output (SPEC-002/SPEC-1xx).

An OrthoSeg stream is the edition-INDEPENDENT reading of the rasm+dabt:
consonants with their vowel state, madd letters resolved to quality, silent
letters deleted with reasons, tanween carrying its dabt mode. Later phases
(waqf, junction, noon/meem, madd...) operate on this stream only.

Dabt states recorded here are WITNESSES, not decisions: e.g. tanween mode
"open" (KFGQPC) or the iqlab meem mark witness that the phonological phases
must independently derive and then assert against (SPEC-002 R021).
"""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Literal

from .ir import Base


class VQ(Enum):
    """Vowel quality."""
    A = "a"
    U = "u"
    I = "i"


class SukunKind(Enum):
    MARKED = "marked"   # explicit sukun sign (Tanzil 0652 / KFGQPC 06E1)
    BARE = "bare"       # no vowel-slot mark: assimilated/hidden per dabt


class TanweenMode(Enum):
    PLAIN = "plain"          # Tanzil unified forms — mode carried by separate markers
    IZHAR = "izhar"          # KFGQPC closed forms (izhar or pre-pause)
    OPEN = "open"            # KFGQPC open forms (idgham/ikhfa follows)
    IQLAB = "iqlab"          # iqlab-marked (meem mark on/after the tanween)


class MaddSource(Enum):
    PLAIN_ALEF = "plain_alef"
    ALEF_MAKSURA = "alef_maksura"
    BARE_WAW = "bare_waw"
    BARE_YEH = "bare_yeh"
    DAGGER_ALEF = "dagger_alef"
    SMALL_WAW = "small_waw"
    SMALL_YEH = "small_yeh"
    SMALL_HIGH_YEH = "small_high_yeh"
    LETTER_NAME = "letter_name"    # R011 muqatta'at spell-out internal madd


@dataclass(frozen=True)
class Tanween:
    quality: VQ
    mode: TanweenMode


@dataclass(frozen=True)
class ConsSeg:
    letter: Base
    vowel: VQ | None
    tanween: Tanween | None
    sukun: SukunKind | None
    shadda: bool
    hamza_carrier: str | None   # codepoint name of the carrier, for provenance
    madda: bool                 # U+0653 madd-class witness on this seg's cluster
    iqlab_mark: bool            # U+06E2/06ED witness
    span: tuple[int, int]
    word_index: int


@dataclass(frozen=True)
class MaddSeg:
    quality: VQ
    source: MaddSource
    madda: bool                 # U+0653 on the madd letter (muttasil/lazim witness)
    span: tuple[int, int]
    word_index: int
    waqf_only: bool = False     # U+06E0 sukun mustateel: pronounced only at waqf


OrthoSeg = ConsSeg | MaddSeg


@dataclass
class DecodeResult:
    segs: list[OrthoSeg]
    n_words: int


class DecodeError(Exception):
    """Cluster the decoder cannot yet read — fail closed with site info."""
