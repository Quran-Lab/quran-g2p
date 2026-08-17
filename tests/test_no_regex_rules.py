"""Structural ban: the engine never matches rules with regular expressions.

Rules operate on the typed IR (Cluster/Phone streams), never on `str`.
Regex-over-strings is the reference engine's central fragility: a pattern
written for one spelling silently misses a variant of the same word, and
nothing in the system knows a rule failed to fire. The IR makes the same
question a typed lookup that either matches a Base or does not.

The detector self-checks against a synthetic module below, so a broken
scanner cannot pass this file vacuously.
"""
import ast
from pathlib import Path

SRC = Path(__file__).resolve().parents[1] / "src" / "quran_g2p"

BANNED_MODULES = {"re", "regex"}


def _regex_uses(source: str, label: str):
    """Return every regex import or `re.<fn>()` call site in `source`."""
    tree = ast.parse(source)
    hits = []
    aliases = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for a in node.names:
                if a.name.split(".")[0] in BANNED_MODULES:
                    aliases.add(a.asname or a.name)
                    hits.append(f"{label}:{node.lineno} import {a.name}")
        elif isinstance(node, ast.ImportFrom):
            if (node.module or "").split(".")[0] in BANNED_MODULES:
                hits.append(f"{label}:{node.lineno} from {node.module} import ...")
        elif isinstance(node, ast.Attribute):
            base = node.value
            if isinstance(base, ast.Name) and base.id in (aliases | BANNED_MODULES):
                hits.append(f"{label}:{node.lineno} {base.id}.{node.attr}")
    return hits


_SYNTHETIC_VIOLATIONS = [
    "import re\n",
    "import re as _r\n_r.sub('a', 'b', 'c')\n",
    "from re import sub\n",
    "import regex\n",
]


def test_detector_is_not_vacuous():
    """A scanner that never fires would pass the real check silently."""
    for src in _SYNTHETIC_VIOLATIONS:
        assert _regex_uses(src, "<synthetic>"), src
    assert _regex_uses("from quran_g2p import ir\nx = ir.Base\n", "<clean>") == []


def test_engine_source_is_regex_free():
    files = sorted(SRC.rglob("*.py"))
    assert files, f"no source files found under {SRC}"
    hits = []
    for f in files:
        hits += _regex_uses(f.read_text(encoding="utf-8"),
                            str(f.relative_to(SRC)))
    assert hits == [], (
        "regex matching is banned in the engine; rules read the typed IR:\n  "
        + "\n  ".join(hits))
