"""The register completeness gate.

Enforces the full contract of `quran_g2p.rules.registry`:

  1. every rule id used in src/ is registered, and every registered id
     is still used in src/ (the register equals the engine, both ways);
  2. every entry maps to golden rows that exist (the ruling is actually
     in front of the expert reviewer);
  3. every entry carries a classical citation;
  4. ids are append-only against the committed manifest
     (`tests/registry_frozen_ids.txt`): removing or renaming an id
     fails until the manifest is edited deliberately, and a new id
     fails until it is appended, so every change to the rule inventory
     is a reviewed event.
"""
import re
from pathlib import Path

import yaml

from quran_g2p.rules.registry import BY_ID, COVERAGE, RULINGS

ROOT = Path(__file__).parents[1]
SRC = ROOT / "src" / "quran_g2p"
GOLDEN_DIR = Path(__file__).parent / "goldens"
FROZEN = Path(__file__).parent / "registry_frozen_ids.txt"

_ID_RE = re.compile(r'"(R\d{3}[A-Z0-9_]*)"')


def source_ids():
    ids = set()
    for f in SRC.rglob("*.py"):
        if f.name == "registry.py" and f.parent.name == "rules":
            continue
        ids |= set(_ID_RE.findall(f.read_text(encoding="utf-8")))
    return ids


def golden_row_ids():
    ids = set()
    for f in sorted(GOLDEN_DIR.glob("*.yaml")):
        for row in yaml.safe_load(f.read_text(encoding="utf-8")):
            ids.add(row["id"])
    return ids


def test_every_source_rule_is_registered():
    missing = sorted(source_ids() - set(COVERAGE))
    assert not missing, (
        f"rule ids used in src/ but absent from the register: {missing} "
        "— add the ruling to the reviewable golden set, register it, "
        "and append the id to tests/registry_frozen_ids.txt")


def test_no_stale_register_entries():
    stale = sorted(set(COVERAGE) - source_ids())
    assert not stale, f"registered ids no longer used in src/: {stale}"


def test_every_ruling_has_existing_coverage_rows():
    rows = golden_row_ids()
    for rule in RULINGS:
        assert rule.covered_by, f"{rule.id}: empty coverage"
        dangling = [c for c in rule.covered_by if c not in rows]
        assert not dangling, (
            f"{rule.id}: coverage rows do not exist: {dangling}")


def test_every_ruling_carries_a_citation():
    for rule in RULINGS:
        assert rule.cite.strip(), f"{rule.id}: no classical citation"


def test_ids_are_append_only_against_manifest():
    frozen = set(FROZEN.read_text(encoding="utf-8").split())
    current = set(BY_ID)
    removed = sorted(frozen - current)
    assert not removed, (
        f"registered ids removed or renamed: {removed} — ids are "
        "append-only; edit tests/registry_frozen_ids.txt only as a "
        "deliberate, reviewed event")
    unfrozen = sorted(current - frozen)
    assert not unfrozen, (
        f"new ids not yet in the manifest: {unfrozen} — append them to "
        "tests/registry_frozen_ids.txt")


def test_register_document_is_fresh():
    import sys
    sys.path.insert(0, str(ROOT / "tools"))
    from export_register import render
    doc = ROOT / "docs" / "RULINGS-REGISTER.md"
    assert doc.exists(), "docs/RULINGS-REGISTER.md missing — run tools/export_register.py"
    assert doc.read_text(encoding="utf-8") == render(), (
        "docs/RULINGS-REGISTER.md is stale — rerun tools/export_register.py")
