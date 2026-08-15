"""Corpus gate: trigger-span cross-check vs cpfair/quran-tajweed (A6 crit. 4).

Every category must reach recall 1.0 except the three verdicted misses:
17:7 (rasm variant, madd_2) and 2:245/7:69 (seen-substitution vs their
'silent saad'). Any new miss is a regression, not a tolerance.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))


def test_span_oracle_gate():
    import span_check
    tp, fn, fn_ex = span_check.main()
    allowed_fn = {"madd_2": 1, "silent": 2}
    for cat in span_check.CATEGORY:
        limit = allowed_fn.get(cat, 0)
        assert fn[cat] <= limit, (cat, fn[cat], fn_ex.get(cat))
