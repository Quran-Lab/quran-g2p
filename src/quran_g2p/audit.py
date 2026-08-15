"""Codepoint census and fail-closed corpus verification.

Codepoints are keyed as 4-or-more hex digits, uppercase, zero-padded ("0628"),
so the census file is diffable and unambiguous regardless of console encoding.
"""
from __future__ import annotations

from collections import Counter
from typing import Iterable, Mapping

from .textbank import TextBank


class CensusError(Exception):
    """Corpus census does not match the frozen expectation."""


def _key(ch: str) -> str:
    return f"{ord(ch):04X}"


def census(texts: Iterable[str]) -> dict[str, int]:
    counter: Counter[str] = Counter()
    for text in texts:
        for ch in text:
            counter[_key(ch)] += 1
    return dict(counter)


def verify_corpus_census(tb: TextBank, frozen: Mapping[str, int]) -> None:
    actual = census(tb.ayah(ref) for ref in tb.refs())
    if actual == dict(frozen):
        return
    missing = {k: v for k, v in frozen.items() if actual.get(k) != v}
    extra = {k: v for k, v in actual.items() if frozen.get(k) != v}
    raise CensusError(
        f"census drift for edition {tb.edition!r}: "
        f"expected-but-differing={missing} actual-but-differing={extra}"
    )
