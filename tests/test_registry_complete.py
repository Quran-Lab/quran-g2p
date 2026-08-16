"""The register completeness gate: every rule the engine can cite is
covered by at least one existing golden row, with no stale entries and
no dangling row references. See src/quran_g2p/registry.py."""
import re
from pathlib import Path

import yaml

from quran_g2p.registry import COVERAGE

SRC = Path(__file__).parents[1] / "src" / "quran_g2p"
GOLDEN_DIR = Path(__file__).parent / "goldens"

_ID_RE = re.compile(r'"(R\d{3}[A-Z0-9_]*)"')


def source_ids():
    ids = set()
    for f in SRC.rglob("*.py"):
        if f.name == "registry.py":
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
        "— add the ruling to the reviewable golden set and map it")


def test_no_stale_register_entries():
    stale = sorted(set(COVERAGE) - source_ids())
    assert not stale, f"registered ids no longer used in src/: {stale}"


def test_every_ruling_has_existing_coverage_rows():
    rows = golden_row_ids()
    for rid, cov in COVERAGE.items():
        assert cov, f"{rid}: empty coverage"
        dangling = [c for c in cov if c not in rows]
        assert not dangling, f"{rid}: coverage rows do not exist: {dangling}"
