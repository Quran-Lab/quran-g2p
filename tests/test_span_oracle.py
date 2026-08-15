"""Corpus gate: trigger-span cross-check vs the quran-tajweed spans (A6 c4).

Every category must reach recall 1.0. The single allowed residual is ONE
annotation corpus-wide: 17:7 madd_2, a verdicted DATASET error (their
2017 annotation reads the un-restored rasm as tabee'i; the recitation
restores the waw and the madd is muttasil: al-Hujja 5:85, al-Muhkam
1:168, see the rulings register). The former 'silent' misses at
2:245/7:69 are cross-representation equivalences the checker now maps
(their silent-sad annotation = our R012 seen-substitution provenance).
Any new miss is a regression, not a tolerance.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))


def test_span_oracle_gate():
    import span_check
    tp, fn, fn_ex = span_check.main()
    allowed_fn = {"madd_2": 1}
    for cat in span_check.CATEGORY:
        limit = allowed_fn.get(cat, 0)
        assert fn[cat] <= limit, (cat, fn[cat], fn_ex.get(cat))
