"""Seeded-bug drill for the LATTICE path (Phase III): each mutant re-plants a plausible failure of the per-word
lattice, the concat-with-stops split, the khilaf splice or the rawm fix, and must be KILLED by the fast detectors
below (cross-sections of tools/audit_lattice.py and test_lattice.py).
"""
import random

import pytest

import quran_g2p.concat as CC
import quran_g2p.lattice as LT
import quran_g2p.variants as VR
from quran_g2p.concat import phonemize_concat
from quran_g2p.ir import Base
from quran_g2p.lattice import build_lattice
from quran_g2p.phonemize import phonemize
from quran_g2p.textbank import AyahRef, TextBank
from quran_g2p.waqf import WaqfSpec

TB = TextBank.load("tanzil")
STOP_AYAT = [(2, 26), (2, 255), (11, 42), (24, 52), (36, 52), (75, 27), (112, 1)]
PAIRS = [((3, 1), (3, 2)), ((69, 28), (69, 29)), ((112, 1), (112, 2)), ((18, 1), (18, 2))]


def sig(p):
    return (p.base, p.kind, p.geminated, p.ghunna, p.qalqalah, p.tafkheem, p.tafkheem_rank, p.sakt_after,
            p.pausal_role, p.length, p.word_index)


def items_of(*refs):
    return [(AyahRef(*r), TB.ayah(AyahRef(*r))) for r in refs]


# --- detectors ---------------------------------------------------------------------------------------------------

def detect_locality():
    rng = random.Random(7)
    for s, a in STOP_AYAT:
        (ref, text), = items_of((s, a))
        lat = build_lattice([(ref, text)])
        ks = [k for k in range(lat.n_words - 1) if lat.stoppable[k]]
        for st in ([], ks, [k for k in ks if rng.random() < 0.5], ks[:2]):
            want = [sig(p) for seg in phonemize(text, edition="tanzil", ref=ref, waqf=WaqfSpec(tuple(st))).segments
                    for p in seg.phones]
            assert [sig(p) for p in lat.path(st)] == want, (s, a, st)


def detect_junctions():
    for x, y in PAIRS:
        items = items_of(x, y)
        n1 = len(LT._word_maps(items[:1], "tanzil", LT.HafsConfig())[0])
        # a stop at the ayah boundary = the two ayat read independently
        got = phonemize_concat(items, edition="tanzil", waqf=WaqfSpec((n1 - 1,))).segments
        a = [sig(p) for p in phonemize(items[0][1], edition="tanzil", ref=items[0][0]).segments[0].phones]
        b = [sig(p)[:-1] + (p.word_index + n1,)
             for p in phonemize(items[1][1], edition="tanzil", ref=items[1][0]).segments[0].phones]
        assert [sig(p) for p in got[0].phones] == a and [sig(p) for p in got[1].phones] == b, (x, y)
        lat = build_lattice(items)
        for st in ([], [n1 - 1]):
            want = [sig(p) for seg in phonemize_concat(items, edition="tanzil", waqf=WaqfSpec(tuple(st))).segments
                    for p in seg.phones]
            assert [sig(p) for p in lat.path(st)] == want, (x, y, st)


def detect_sites():
    lat = build_lattice(items_of((54, 16)))
    (site,) = list(lat.sites)
    w = lat.n_words - 1
    base = lat.path([])
    alt = lat.path([], choice={site: lat.sites[site]["wajh"]})
    assert base != alt and base[-1].tafkheem == "moraqaq" and alt[-1].tafkheem == "mofakham"
    assert [sig(p) for p in base if p.word_index != w] == [sig(p) for p in alt if p.word_index != w]


def detect_rawm():
    lat = build_lattice(items_of((89, 1)))
    rawm = next(f for f in lat.forms[(0, "ibtida", "waqf")] if f.mode == "rawm")
    assert [p for p in rawm.phones if p.base is Base.REH][-1].tafkheem == "moraqaq"
    lat = build_lattice(items_of((1, 1)))
    w = lat.n_words - 1
    fs = {f.mode: f for f in lat.forms[(w, "wasl", "waqf")]}
    rawm, sukun = fs["rawm"], fs["sukun"]
    assert {p.word_index for p in rawm.phones} == {w}
    # rawm = the sukun form plus the partial haraka, nothing else added or lost
    assert len(rawm.phones) == len(sukun.phones) + 1
    assert [p.base for p in rawm.phones[:-1]] == [p.base for p in sukun.phones]


DETECTORS = [detect_locality, detect_junctions, detect_sites, detect_rawm]


def killed():
    for d in DETECTORS:
        try:
            d()
        except (AssertionError, KeyError, IndexError, ValueError, StopIteration):
            return True
    return False


def test_detectors_pass_on_clean_engine():
    for d in DETECTORS:
        d()


# --- mutants -----------------------------------------------------------------------------------------------------

def test_mutant_state_swap(monkeypatch):
    """L/R semantics swapped: a stop BEFORE w read as a stop after it."""
    def bad(w, stops, n):
        left = LT.IBTIDA if (w == 0 or w in stops) else LT.WASL
        right = LT.WAQF if (w == n - 1 or (w - 1) in stops) else LT.WASL
        return left, right
    monkeypatch.setattr(LT, "_state_of", bad)
    assert killed()


def test_mutant_missing_pattern(monkeypatch):
    """only three stop patterns: some (word, state) slots never filled."""
    orig = LT._patterns
    monkeypatch.setattr(LT, "_patterns", lambda n: {k: v for k, v in orig(n).items() if k != "odd"})
    assert killed()


def test_mutant_waqf_form_keeps_segment(monkeypatch):
    """the waqf variants keep the whole breath group instead of the last word."""
    orig = LT._fill

    def bad(items, edition, config, n, lo, hi, want_variants=True):
        forms = orig(items, edition, config, n, lo, hi, want_variants)
        for k, fs in forms.items():
            if k[2] == LT.WAQF and len(fs) > 1 and k[0] > 0:
                prev = forms.get((k[0] - 1, LT.WASL if k[1] == LT.WASL else LT.IBTIDA, LT.WASL))
                if prev:
                    fs[1] = LT.WordForm(fs[1].word, fs[1].left, fs[1].right, fs[1].mode,
                                        prev[0].phones + fs[1].phones)
        return forms
    monkeypatch.setattr(LT, "_fill", bad)
    assert killed()


def test_mutant_concat_split_without_rerun(monkeypatch):
    """concat with stops joins first and only cuts the stream at the stops: the junction rules (3:1 -> 3:2
    connective fatha, 69:28 -> 69:29 sakt, tanween junctions) leak across a stop."""
    real = CC.phonemize_concat

    def bad(items, edition, config=None, waqf=None):
        res = real(items, edition, config, None)
        if waqf is None or not waqf.stops:
            return res
        from quran_g2p.phonemize import Segment
        cuts, segs, cur = sorted(waqf.stops), [], []
        for p in res.segments[0].phones:
            while cuts and p.word_index > cuts[0]:
                segs.append(cur)
                cur = []
                cuts.pop(0)
            cur.append(p)
        segs.append(cur)
        res.segments = [Segment(x, "x") for x in segs if x]
        return res
    monkeypatch.setattr(CC, "phonemize_concat", bad)
    assert killed()


def test_mutant_site_choice_ignored(monkeypatch):
    """word_forms ignores the site choice: the alternate wajh can never be selected."""
    monkeypatch.setattr(LT.WordLattice, "word_forms", lambda self, w, l, r, choice=None: self.forms[(w, l, r)])
    assert killed()


def test_mutant_rawm_keeps_sakin_raa_tafkheem(monkeypatch):
    """the pre-fix rawm: the final raa keeps its sakin-raa tafkheem (89:1, 97:5 token not in tj1)."""
    orig = VR._rawm

    def old(seg_phones, haraka):
        out = list(orig(seg_phones, haraka))
        from dataclasses import replace
        last_cons = len(out) - 2
        out[last_cons] = replace(out[last_cons], tafkheem=seg_phones[-1].tafkheem,
                                 tafkheem_rank=seg_phones[-1].tafkheem_rank)
        return tuple(out)
    monkeypatch.setattr(VR, "_rawm", old)
    assert killed()


def test_mutant_iskan_variants_whole_segment(monkeypatch):
    """rawm madd reduction applied to every word of the breath group, not only the stopped word."""
    from dataclasses import replace
    orig = VR._rawm

    def bad(seg_phones, haraka):
        out = list(orig(seg_phones, haraka))
        return tuple(replace(p, word_index=out[-1].word_index) if i < len(out) - 3 else p
                     for i, p in enumerate(out))
    monkeypatch.setattr(VR, "_rawm", bad)
    assert killed()
