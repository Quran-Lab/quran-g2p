"""codepoints.py is the single home of every Arabic codepoint in the project.

Contract: every codepoint occurring in ANY pinned edition's census has a named
constant; constants are unique single characters; NAME_BY_CP maps back. Rules
and tests reference these names — never typed Arabic, never bare escapes.
"""
import json
from pathlib import Path

from quran_g2p import codepoints as cp

REPO_DATA = Path(__file__).resolve().parents[1] / "data"


def _census_union():
    union = set()
    for f in ("census-tanzil.json", "census-kfgqpc.json"):
        union |= set(json.loads((REPO_DATA / f).read_text(encoding="utf-8")))
    return union


def test_every_census_codepoint_has_a_named_constant():
    missing = sorted(_census_union() - set(cp.NAME_BY_CP))
    assert not missing, f"codepoints in pinned texts without constants: {missing}"


def test_constants_are_unique_single_chars():
    seen = {}
    for name, value in cp.ALL.items():
        assert isinstance(value, str) and len(value) == 1, name
        assert value not in seen, f"{name} duplicates {seen.get(value)}"
        seen[value] = name


def test_name_by_cp_roundtrips():
    for name, value in cp.ALL.items():
        key = f"{ord(value):04X}"
        assert cp.NAME_BY_CP[key] == name
        assert getattr(cp, name) == value
