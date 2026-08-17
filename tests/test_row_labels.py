"""Gate for the adjudication-#1/#2 defect class: a review row's Arabic
label contradicting its own example, ayah, or expect block.

The golden harness proves expect-vs-engine; this gate proves
label-vs-row, so a garbled or mispaired label can never again ride to
the reviewer on the back of a correct expect block. The detector
self-checks against synthetic broken rows, so it cannot pass vacuously.
"""
import sys
from pathlib import Path

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from audit_row_labels import TRANSFORMED_OK, check_rows  # noqa: E402
from quran_g2p.textbank import TextBank  # noqa: E402

GOLDENS = Path(__file__).resolve().parents[1] / "tests" / "goldens"


def _rows():
    rows = []
    for f in sorted(GOLDENS.glob("*.yaml")):
        rows += yaml.safe_load(f.read_text(encoding="utf-8"))
    return rows


def test_detector_is_not_vacuous():
    tb = TextBank.load("tanzil")
    broken = [
        # P1: quoted fragment absent from the anchored ayah
        {"id": "syn-p1", "surah": 1, "ayah": 1,
         "rule_ar": "إدغام مزيف (سَمِيعٌ بَصِيرٌ)",
         "expect": [{"base": "meem", "geminated": True}]},
        # L1: idgham label naming a letter the expect block lacks
        {"id": "syn-l1", "surah": 2, "ayah": 8,
         "rule_ar": "إدغام كامل بغنة في الميم (مَن يَقُولُ)",
         "expect": [{"base": "yeh", "geminated": True}]},
        # L2: kamil label without geminated:true
        {"id": "syn-l2", "surah": 2, "ayah": 61,
         "rule_ar": "إدغام كامل بغنة في النون (لَن نَّصْبِرَ)",
         "expect": [{"base": "noon"}]},
    ]
    fails = check_rows(broken, tb)
    codes = {(rid, code) for rid, code, _ in fails}
    assert ("syn-p1", "P1") in codes, fails
    assert ("syn-l1", "L1") in codes, fails
    assert ("syn-l2", "L2") in codes, fails
    # and the resurrected adjudication-#1 row must be caught
    resurrected = [{"id": "syn-adj1", "surah": 2, "ayah": 8,
                    "rule_ar": "إدغام كامل بغنة في الميم (مَن يَقُولُ)",
                    "expect": [{"base": "yeh", "ghunna": "idgham"}]}]
    assert check_rows(resurrected, tb), "adjudication-#1 mutant survived"


def test_all_row_labels_coherent():
    tb = TextBank.load("tanzil")
    fails = check_rows(_rows(), tb)
    assert fails == [], (
        "label/content mismatches (see docs/ADJUDICATIONS.md):\n  "
        + "\n  ".join(f"{c} [{r}] {m}" for r, c, m in fails))


def test_allowlist_points_at_live_rows():
    ids = {r["id"] for r in _rows()}
    stale = set(TRANSFORMED_OK) - ids
    assert not stale, f"TRANSFORMED_OK entries for deleted rows: {stale}"
