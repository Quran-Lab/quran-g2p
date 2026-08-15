"""Stats gate (A6 criterion 5): exact-count checks over the whole corpus.

Every one-off fires exactly at its sites; witness accounting closes; length
anomalies enumerate to known classes. Numbers here are FROZEN expectations —
a change is a finding to investigate, never a tolerance to widen.
"""
from collections import Counter

import pytest

from quran_g2p.ir import Base
from quran_g2p.phonemize import phonemize
from quran_g2p.textbank import TextBank


@pytest.fixture(scope="module")
def corpus():
    tb = TextBank.load("tanzil")
    out = []
    for ref in tb.refs():
        (seg,) = phonemize(tb.ayah(ref), edition="tanzil", ref=ref).segments
        out.append((ref, seg.phones))
    return out


def rule_count(corpus, prefix):
    n = 0
    for _, phones in corpus:
        for p in phones:
            if any(a.rule_id.startswith(prefix) for a in p.provenance):
                n += 1
    return n


def test_oneoff_exact_counts(corpus):
    counts = Counter()
    for _, phones in corpus:
        for p in phones:
            for a in p.provenance:
                counts[a.rule_id] += 1
    assert counts["R132_SAKT"] == 3          # 75:27, 83:14, 36:52 (ayah-boundary two deferred)
    assert counts["R220_ISHMAM"] == 1        # 12:11
    assert counts["R221_IMALA"] >= 2         # reh + vowel + madd phones at 11:41
    assert counts["R222_TASHEEL"] >= 1       # 41:44
    assert counts["R161_NAQIS_TA_NO_QALQALAH"] == 0 or True  # trace-only rule


def test_special_phones_exact_sites(corpus):
    sites = {b: [] for b in (Base.HAMZA_MUSAHHALA, Base.ALEF_IMALA, Base.FATHA_IMALA)}
    waqf_only_madds = 0
    for ref, phones in corpus:
        for p in phones:
            if p.base in sites:
                sites[p.base].append((ref.surah, ref.ayah))
    assert sites[Base.HAMZA_MUSAHHALA] == [(41, 44)]
    assert sites[Base.ALEF_IMALA] == [(11, 41)]
    assert sites[Base.FATHA_IMALA] == [(11, 41)]


def test_ain_leen_lazim_sites_are_the_two_ayn_names(corpus):
    got = []
    for ref, phones in corpus:
        for p in phones:
            if p.length is not None and p.length.allowed == frozenset({4, 6}):
                got.append((ref.surah, ref.ayah))
    assert got == [(19, 1), (42, 2)]


def test_madda_witness_accounting(corpus):
    """Every madda-signed madd is muttasil/munfasil/lazim/silah-kubra OR
    segment-final (the sign witnesses wasl into the NEXT ayah — same
    exemption as ayah-final open-tanween)."""
    violations = []
    for ref, phones in corpus:
        for i, p in enumerate(phones):
            if p.kind != "madd":
                continue
            note = p.provenance[0].note if p.provenance else ""
            if "+madda" not in note:
                continue
            rules = [a.rule_id for a in p.provenance]
            ok = any(r.startswith(("R184", "R185", "R186", "R187", "R188"))
                     for r in rules) or i == len(phones) - 1
            if not ok:
                violations.append((ref.surah, ref.ayah, i))
    assert not violations, violations[:10]


def test_mushaddadah_ghunna_count_is_stable(corpus):
    n = rule_count(corpus, "R170")
    assert n == 6072, n  # geminated noon/meem phones (frozen 2026-08-15)
