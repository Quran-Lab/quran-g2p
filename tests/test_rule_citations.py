"""The citation pages in artifacts/citations/ cover the register exactly.

Every part of every ruling's citation has one row, in the register's order and
in its words, so a change to a citation fails here until the pages are found
again. A verified row names its print and its page; the rest say why not.
Where the Shamela corpus is on the machine, the file must regenerate byte for
byte from it.
"""
import importlib.util
import json
import os
from pathlib import Path

import pytest

from quran_g2p.rules.registry import RULINGS

ROOT = Path(__file__).resolve().parents[1]
ART = ROOT / "artifacts" / "citations"
SHAMELA4 = Path(os.environ.get("SHAMELA4", "F:/shamela4"))


def _rows(name):
    return [json.loads(line) for line in (ART / name).read_text(encoding="utf-8").splitlines() if line.strip()]


def _parts(cite):
    return [x.strip() for x in cite.split("؛") if x.strip()]


def test_one_row_per_citation_part_in_register_order():
    got = [(r["rule_id"], r["n"], r["cited"]) for r in _rows("rule_citations.jsonl")]
    want = [(r.id, k, part) for r in RULINGS for k, part in enumerate(_parts(r.cite), 1)]
    assert got == want


PLACED = {"quoted", "bayt", "on_cited_page", "located", "candidate"}
SHOWN = {"quoted", "bayt", "on_cited_page", "located"}


def test_a_placed_row_names_its_print_page_and_passage():
    editions = {e["shamela_book"]: e for e in _rows("editions.jsonl")}
    for r in _rows("rule_citations.jsonl"):
        assert r["status"] in PLACED | {"not_found", "note"}, r
        if r["status"] in PLACED:
            e = editions[r["shamela_book"]]
            assert e["pages_match_print"] and "موافق للمطبوع" in e["card_ar"]
            assert r["work"] == e["work"] and r["edition"] == e["edition"]
            assert isinstance(r["page"], int) and r["excerpt"].strip()
            assert r["url"].startswith(f"https://shamela.ws/book/{r['shamela_book']}/")
        else:
            assert r.get("reason") and not r.get("url"), r
        if r["status"] in {"bayt", "on_cited_page"}:
            assert r.get("page_cited") and r.get("page_agrees") is True, r
        if r["status"] == "located":
            assert r.get("page_agrees") is None and r.get("pages_matching"), r
        if "«" in r["cited"] and r["status"] != "quoted" and r["status"] != "note":
            assert r.get("quote_found") is False, r


def test_every_ruling_with_a_work_has_a_page_an_app_may_show():
    """Each ruling has at least one row an app may show beside a flag, except
    the one whose citation names no work its passage was found in."""
    by_rule = {}
    for r in _rows("rule_citations.jsonl"):
        by_rule.setdefault(r["rule_id"], set()).add(r["status"])
    without = sorted(k for k, v in by_rule.items() if not v & SHOWN)
    assert without == ["R112_STRIP_INITIAL_SHADDA"]


@pytest.mark.skipif(not (SHAMELA4 / "_meta").exists(), reason="the Shamela corpus is not on this machine")
def test_regenerates_from_the_corpus():
    spec = importlib.util.spec_from_file_location("locate_citations", ROOT / "tools" / "locate_citations.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    got = [{k: v for k, v in {k: r.get(k) for k in mod.FIELDS}.items() if v is not None} for r in mod.run()]
    assert got == _rows("rule_citations.jsonl")
