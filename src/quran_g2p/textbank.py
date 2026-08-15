"""Pinned, fail-closed loading of the vendored Quran text editions.

The engine's input contract starts here: an edition loads only if its file's
SHA-256 matches the pin recorded below. A mismatch is a hard error, never a
warning — a silently drifted text edition would invalidate every downstream
census count, rule trigger, and golden test.

Editions:
  tanzil  — Tanzil Uthmani (official tanzil.net distribution), authoritative input.
  kfgqpc  — KFGQPC Hafs v18 (github thetruetruth/quran-data-kfgqpc), cross-check.
The reference-engine-packaged text is deliberately NOT an edition here; it is consulted
only inside the oracle/ quarantine.
"""
from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Iterator

_REPO_DATA = Path(__file__).resolve().parents[2] / "data"

# (filename, sha256) — the pin IS the contract; update only with a spec change.
_PINS: dict[str, tuple[str, str]] = {
    "tanzil": (
        "tanzil-uthmani.txt",
        "bf4f57b968d03f4131c070b1e285da9be0e0a108a21c910e872801ca273312c8",
    ),
    "kfgqpc": (
        "kfgqpc-hafsData_v18.json",
        "5d8bb91726e482839d0057633cb1973031e4d706fa9604eea5e08892f20ba140",
    ),
}

# Trailing ayah-number decoration in KFGQPC aya_text: NBSP + Arabic-Indic digits.
_KFGQPC_STRIP = "\xa0 " + "".join(chr(c) for c in range(0x0660, 0x066A))


class PinnedTextError(Exception):
    """Vendored text file does not match its recorded SHA-256 pin."""


@dataclass(frozen=True, order=True)
class AyahRef:
    surah: int
    ayah: int


class TextBank:
    def __init__(self, edition: str, ayat: dict[AyahRef, str]):
        self.edition = edition
        self._ayat = ayat

    @property
    def n_ayat(self) -> int:
        return len(self._ayat)

    def ayah(self, ref: AyahRef) -> str:
        return self._ayat[ref]

    def refs(self) -> Iterator[AyahRef]:
        return iter(self._ayat)

    @classmethod
    def load(cls, edition: str, data_dir: Path | None = None) -> "TextBank":
        if edition not in _PINS:
            raise ValueError(f"unknown edition {edition!r}; known: {sorted(_PINS)}")
        filename, expected_sha = _PINS[edition]
        path = (data_dir or _REPO_DATA) / filename
        blob = path.read_bytes()
        actual_sha = hashlib.sha256(blob).hexdigest()
        if actual_sha != expected_sha:
            raise PinnedTextError(
                f"{path} sha256={actual_sha} does not match pin {expected_sha}"
            )
        if edition == "tanzil":
            ayat = _parse_tanzil(blob)
        else:
            ayat = _parse_kfgqpc(blob)
        return cls(edition, ayat)


def _parse_tanzil(blob: bytes) -> dict[AyahRef, str]:
    ayat: dict[AyahRef, str] = {}
    for line in blob.decode("utf-8-sig").splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        surah, ayah, text = line.split("|", 2)
        ayat[AyahRef(int(surah), int(ayah))] = text
    # Tanzil embeds the basmala at the start of every surah's first ayah
    # except surahs 1 (where it IS 1:1) and 9 (none). Canonical ayah numbering
    # excludes it, so strip. The embedded copy can carry cross-unit wasl dabt
    # on its first letter (95:1 beh+shadda from فَٱرْغَب idgham; iqlab class
    # likewise), so the match is exact on all but the first word, and
    # rasm-skeleton-exact on the first word. Fail-closed otherwise.
    basmala = ayat[AyahRef(1, 1)]
    b_first, b_rest = basmala.split(" ", 1)

    def _skeleton(s: str) -> str:
        return "".join(ch for ch in s if not (0x064B <= ord(ch) <= 0x0652))

    for surah in range(2, 115):
        if surah == 9:
            continue
        ref = AyahRef(surah, 1)
        text = ayat[ref]
        first, rest = text.split(" ", 1)
        if _skeleton(first) != _skeleton(b_first) or not rest.startswith(b_rest + " "):
            raise PinnedTextError(f"{ref} does not start with the basmala prefix")
        ayat[ref] = rest[len(b_rest) + 1:]
    return ayat


def _parse_kfgqpc(blob: bytes) -> dict[AyahRef, str]:
    rows = json.loads(blob.decode("utf-8-sig"))
    ayat: dict[AyahRef, str] = {}
    for row in rows:
        text = row["aya_text"].rstrip(_KFGQPC_STRIP)
        ayat[AyahRef(int(row["sora"]), int(row["aya_no"]))] = text
    return ayat
