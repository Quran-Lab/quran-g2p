"""The QAC morphology oracle (plan A3/P3), frozen as a corpus invariant.

Every hamzat-al-wasl-initial word in the corpus: the engine's ibtida'
haraka must agree with the Quranic Arabic Corpus POS class (article/REL
-> fath; bare noun -> kasra; verb -> kasra/damma). This oracle caught a
real bug on first contact: the iltaqa verb family (form VIII of a
lam-initial root) was read as the article.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))

from qac_crosscheck import main as run_crosscheck  # noqa: E402

RESULT = run_crosscheck()


def test_word_tokenization_aligned():
    assert RESULT["misaligned_ayat"] == []


def test_coverage_is_corpus_wide():
    assert RESULT["unique_pairs"] >= 2000
    assert RESULT["class_counts"]["verb"] >= 300
    assert RESULT["class_counts"]["noun"] >= 40


def test_zero_class_disagreements():
    assert RESULT["mismatches"] == []
