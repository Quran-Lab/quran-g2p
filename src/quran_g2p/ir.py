"""Phone IR: the engine's output types (SPEC-003).

The load-bearing idea is the PRESCRIPTION / OBSERVATION split:

- `LengthSpec` carries prescriptions as SETS: `allowed` (Shatibiyyah-legal),
  `scoring` (attested superset used for labeling/grading tolerance), and a
  deterministic `canonical` default. Free-choice madds have len(allowed) > 1;
  there is no single correct value and the type refuses to pretend otherwise.
- `Phone.realized_len` is the observation slot. The engine NEVER fills it —
  it is not even a constructor parameter; forced alignment fills it downstream
  via `with_realized_len`, keeping prescription and observation from ever
  collapsing into one number again.

Every phone carries its full rule provenance chain and source-char span;
`CoverageMap` guarantees the source is tiled exactly (every input char either
consumed by phones or deleted with a reason code).
"""
from __future__ import annotations

from dataclasses import dataclass, field, replace
from enum import Enum
from typing import Literal


class Base(Enum):
    HAMZA = "hamza"
    BEH = "beh"
    TEH = "teh"
    THEH = "theh"
    JEEM = "jeem"
    HAH = "hah"
    KHAH = "khah"
    DAL = "dal"
    THAL = "thal"
    REH = "reh"
    ZAIN = "zain"
    SEEN = "seen"
    SHEEN = "sheen"
    SAD = "sad"
    DAD = "dad"
    TAH = "tah"
    ZAH = "zah"
    AIN = "ain"
    GHAIN = "ghain"
    FEH = "feh"
    QAF = "qaf"
    KAF = "kaf"
    LAM = "lam"
    MEEM = "meem"
    NOON = "noon"
    HEH = "heh"
    WAW = "waw"
    YEH = "yeh"
    # madd (long-vowel) segments
    ALEF_MADD = "alef_madd"
    WAW_MADD = "waw_madd"
    YEH_MADD = "yeh_madd"
    # short vowels
    FATHA = "fatha"
    DAMMA = "damma"
    KASRA = "kasra"
    # Hafs one-off segments
    FATHA_IMALA = "fatha_imala"
    ALEF_IMALA = "alef_imala"
    HAMZA_MUSAHHALA = "hamza_musahhala"
    DAMMA_MUKHTALASA = "damma_mukhtalasa"
    # nasal ikhfa/iqlab carriers
    NOON_MUKHFAH = "noon_mukhfah"
    MEEM_MUKHFAH = "meem_mukhfah"
    # orthographic-stage letters, resolved before phone emission
    HAMZAT_WASL = "hamzat_wasl"    # resolves to HAMZA+vowel at ibtida' or elides
    TEH_MARBUTA = "teh_marbuta"    # resolves to TEH in wasl, HEH at waqf


Kind = Literal["consonant", "vowel", "madd"]
Ghunna = Literal["mushaddadah", "idgham", "ikhfa", "asl", None]
Qalqalah = Literal["sughra", "kubra", "akbar", None]
Tafkheem = Literal["mofakham", "low_mofakham", "moraqaq"]
PausalRole = Literal["wasl", "pausal", "ibtida", None]


@dataclass(frozen=True)
class LengthSpec:
    kind: Literal["fixed", "free"]
    allowed: frozenset[int]
    canonical: int
    scoring: frozenset[int]

    def __post_init__(self) -> None:
        if not self.allowed:
            raise ValueError("allowed must be non-empty")
        if self.kind == "fixed" and len(self.allowed) != 1:
            raise ValueError(f"fixed LengthSpec must have exactly one allowed value, got {sorted(self.allowed)}")
        if self.canonical not in self.allowed:
            raise ValueError(f"canonical {self.canonical} not in allowed {sorted(self.allowed)}")
        if not self.allowed <= self.scoring:
            raise ValueError(
                f"allowed {sorted(self.allowed)} must be a subset of scoring {sorted(self.scoring)}"
            )


@dataclass(frozen=True)
class RuleApp:
    rule_id: str
    spec: str
    trigger_span: tuple[int, int]
    note: str = ""


@dataclass(frozen=True)
class Phone:
    base: Base
    kind: Kind
    geminated: bool
    length: LengthSpec | None
    ghunna: Ghunna
    qalqalah: Qalqalah
    tafkheem: Tafkheem
    sakt_after: bool
    pausal_role: PausalRole
    provenance: tuple[RuleApp, ...]
    src_span: tuple[int, int]
    word_index: int
    #: Classical maraatib al-tafkheem (Ibn al-Jazari): 1 fath+alif, 2 fath,
    #: 3 damm, 4 sukun, 5 kasr. None for muraqqaq phones. The 3-level
    #: `tafkheem` field is the projection (1-4 -> mofakham, 5 -> low_mofakham).
    tafkheem_rank: int | None = None
    # Observation slot: NOT a constructor parameter (field(init=False)); the
    # engine cannot fill it even by accident. Alignment uses with_realized_len.
    realized_len: float | None = field(init=False, default=None)

    def __post_init__(self) -> None:
        if self.kind == "madd" and self.length is None:
            raise ValueError(f"madd phone {self.base} requires a LengthSpec")

    def with_realized_len(self, value: float) -> "Phone":
        if value <= 0:
            raise ValueError("realized_len must be positive")
        clone = replace(self)
        object.__setattr__(clone, "realized_len", float(value))
        return clone


class DeleteReason(Enum):
    KASHEEDA = "kasheeda"
    SILENT_CIRCLE = "silent_circle"
    WASL_ELIDED = "wasl_elided"
    IDGHAM_FIRST_LETTER = "idgham_first_letter"
    MADD_SIGN = "madd_sign"
    DABT_SIGN = "dabt_sign"
    TANWEEN_RESOLVED = "tanween_resolved"
    PAUSE_MARK = "pause_mark"
    ORNAMENT = "ornament"
    WAQF_DROPPED = "waqf_dropped"
    WORD_SEPARATOR = "word_separator"


class CoverageError(Exception):
    """Source text not tiled exactly by consumed/deleted claims."""


@dataclass(frozen=True)
class Deleted:
    reason: DeleteReason
    rule_id: str


@dataclass(frozen=True)
class Consumed:
    phone_indices: tuple[int, ...]


class CoverageMap:
    def __init__(self, text_len: int):
        self.text_len = text_len
        self._claims: dict[int, Consumed | Deleted] = {}

    def consume(self, char_index: int, phone_index: int) -> None:
        claim = self._claims.get(char_index)
        if isinstance(claim, Deleted):
            raise CoverageError(f"char {char_index} already deleted ({claim.reason})")
        if isinstance(claim, Consumed):
            self._claims[char_index] = Consumed(claim.phone_indices + (phone_index,))
        else:
            self._claims[char_index] = Consumed((phone_index,))

    def delete(self, char_index: int, reason: DeleteReason, rule_id: str) -> None:
        if char_index in self._claims:
            raise CoverageError(f"char {char_index} already claimed: {self._claims[char_index]}")
        self._claims[char_index] = Deleted(reason, rule_id)

    def claim(self, char_index: int) -> Consumed | Deleted | None:
        return self._claims.get(char_index)

    def verify_complete(self) -> None:
        untouched = [i for i in range(self.text_len) if i not in self._claims]
        if untouched:
            raise CoverageError(f"unclaimed source chars at {untouched[:20]}"
                                + ("…" if len(untouched) > 20 else ""))
