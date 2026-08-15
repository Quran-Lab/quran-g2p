"""YAML golden harness (A5a): one parametrized test per golden row.

Golden rows live in tests/goldens/*.yaml, structured for non-programmer
review (ayah, Arabic rule name, citation, expected local phone pattern) and
carry expert_reviewed flags for the release-gate packet. `expect` is a
CONTIGUOUS phone-constraint sequence that must appear in the ayah's phones;
`forbid` is one that must not. Constraint keys: base, kind, geminated,
ghunna, qalqalah, tafkheem, sakt_after, len_allowed, len_canonical,
len_kind. Word-start goldens set `word: <text-prefix>` to phonemize a
single word (ibtida').
"""
from pathlib import Path

import pytest
import yaml

from quran_g2p.ir import Base
from quran_g2p.phonemize import phonemize
from quran_g2p.textbank import AyahRef, TextBank

TB = TextBank.load("tanzil")
GOLDEN_DIR = Path(__file__).parent / "goldens"


def load_goldens():
    rows = []
    for f in sorted(GOLDEN_DIR.glob("*.yaml")):
        for row in yaml.safe_load(f.read_text(encoding="utf-8")):
            row["_file"] = f.name
            rows.append(row)
    return rows


GOLDENS = load_goldens()


def phones_for(row):
    ref = AyahRef(row["surah"], row["ayah"])
    text = TB.ayah(ref)
    if "word" in row:
        w = next(w for w in text.split(" ") if w.startswith(row["word"]))
        (seg,) = phonemize(w, edition="tanzil").segments
    else:
        (seg,) = phonemize(text, edition="tanzil", ref=ref).segments
    return seg.phones


def matches(p, c):
    if "base" in c and p.base is not Base[c["base"].upper()]:
        return False
    if "kind" in c and p.kind != c["kind"]:
        return False
    if "geminated" in c and p.geminated != c["geminated"]:
        return False
    if "ghunna" in c and p.ghunna != c["ghunna"]:
        return False
    if "qalqalah" in c:
        want = c["qalqalah"]
        if want is None and p.qalqalah is not None:
            return False
        if want == "any" and p.qalqalah is None:
            return False
        if want not in (None, "any") and p.qalqalah != want:
            return False
    if "tafkheem" in c and p.tafkheem != c["tafkheem"]:
        return False
    if "sakt_after" in c and p.sakt_after != c["sakt_after"]:
        return False
    if "len_allowed" in c:
        if p.length is None or p.length.allowed != frozenset(c["len_allowed"]):
            return False
    if "len_canonical" in c:
        if p.length is None or p.length.canonical != c["len_canonical"]:
            return False
    if "len_kind" in c:
        if p.length is None or p.length.kind != c["len_kind"]:
            return False
    return True


def find_seq(phones, constraints, start_at=0):
    n = len(constraints)
    for i in range(start_at, len(phones) - n + 1):
        if all(matches(phones[i + j], constraints[j]) for j in range(n)):
            return i
    return -1


@pytest.mark.parametrize(
    "row", GOLDENS, ids=[r.get("id", f"row{i}") for i, r in enumerate(GOLDENS)])
def test_golden(row):
    if row.get("review_only"):
        pytest.skip("statement ruling for the expert packet; engine "
                    "coverage lives in the dedicated python tests")
    ph = phones_for(row)
    if "expect" in row:
        assert find_seq(ph, row["expect"]) >= 0, (
            f"{row['id']}: expected pattern not found in "
            f"{row['surah']}:{row['ayah']}")
    if "expect_at_end" in row:
        n = len(row["expect_at_end"])
        tail = ph[-n:]
        assert all(matches(tail[j], row["expect_at_end"][j]) for j in range(n)), (
            f"{row['id']}: ayah tail does not match")
    if "forbid" in row:
        assert find_seq(ph, row["forbid"]) < 0, (
            f"{row['id']}: forbidden pattern present in "
            f"{row['surah']}:{row['ayah']}")


def test_all_rows_carry_review_flag_and_cite():
    for row in GOLDENS:
        assert "expert_reviewed" in row, row.get("id")
        assert row.get("cite"), row.get("id")
        assert row.get("rule_ar"), row.get("id")
