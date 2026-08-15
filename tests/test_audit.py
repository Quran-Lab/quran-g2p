"""Codepoint census: the fail-closed input contract.

census() counts codepoints; the frozen corpus census (data/census.json) is the
drift detector — any change to the pinned text or the loader shows up as a
census mismatch before it can corrupt a single rule trigger.
"""
import json
from pathlib import Path

import pytest

from quran_g2p.audit import CensusError, census, verify_corpus_census
from quran_g2p.textbank import TextBank

REPO_DATA = Path(__file__).resolve().parents[1] / "data"


def test_census_counts_codepoints_exactly():
    # synthetic: 2x U+0628, 1x U+0650, 1x space
    text = chr(0x628) + chr(0x650) + chr(0x628) + " "
    got = census([text])
    assert got == {"0628": 2, "0650": 1, "0020": 1}


def test_census_of_empty_is_empty():
    assert census([]) == {}
    assert census([""]) == {}


def test_frozen_tanzil_census_matches_recomputation():
    tb = TextBank.load("tanzil")
    frozen = json.loads((REPO_DATA / "census-tanzil.json").read_text(encoding="utf-8"))
    verify_corpus_census(tb, frozen)  # raises CensusError on any drift


def test_frozen_kfgqpc_census_matches_recomputation():
    tb = TextBank.load("kfgqpc")
    frozen = json.loads((REPO_DATA / "census-kfgqpc.json").read_text(encoding="utf-8"))
    verify_corpus_census(tb, frozen)


def test_verify_corpus_census_fails_closed_on_drift():
    tb = TextBank.load("tanzil")
    frozen = json.loads((REPO_DATA / "census-tanzil.json").read_text(encoding="utf-8"))
    frozen["0628"] = frozen.get("0628", 0) + 1
    with pytest.raises(CensusError):
        verify_corpus_census(tb, frozen)
