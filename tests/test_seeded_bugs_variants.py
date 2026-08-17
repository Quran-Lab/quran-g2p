"""Seeded-bug drill for the VARIANT / WAQF / JUNCTION paths (the
2026-08-17 behavioral audit): each mutant re-plants a failure of the
class the rawm-muttasil bug belonged to, and must be KILLED by the
stratified sweep detectors below. The corpus-scale versions of these
sweeps live in tools/audit_variant_paths.py; these detectors are their
fast cross-sections, chosen to cover every mode class.
"""
from dataclasses import replace as _replace

import pytest

import quran_g2p.variants as VR
import quran_g2p.phonemize as PZ
from quran_g2p.concat import phonemize_concat
from quran_g2p.ir import Base
from quran_g2p.phonemize import phonemize
from quran_g2p.textbank import AyahRef, TextBank
from quran_g2p.variants import enumerate_variants
from quran_g2p.waqf import WaqfSpec

TB = TextBank.load("tanzil")

# mode-class coverage: damm(2:259) kasr(95:8? use 1:5? damm) — chosen set:
VARIANT_SITES = [
    (1, 5),     # damm final, aared
    (2, 259),   # dammatan
    (14, 27),   # muttasil-final marfoo (THE bug site class)
    (1, 1),     # kasr-class final (al-Rahim)
    (74, 55),   # pronoun haa after fath (rawm+ishmam legal)
    (75, 16),   # pronoun haa after kasr (sukun only)
    (113, 1),   # qalqalah final (kasr class: rawm legal)
    (1, 2),     # fath final (sukun only)
]

STOP_SITES = [(2, 26), (2, 180), (11, 42), (76, 4)]

JUNCTION_PAIRS = [
    ((2, 26), (2, 27)),     # tanween junctions in baqara run
    ((15, 1), (15, 2)),     # bila-ghunna into reh
    ((9, 79), (9, 80)),     # wiqaya (tanween + hamzat wasl)
    ((27, 1), (27, 2)),     # izhar before haa
]


def _sig(p):
    return (p.base, p.kind, p.geminated, p.ghunna, p.qalqalah, p.tafkheem,
            None if p.length is None else (p.length.kind,
                                           tuple(sorted(p.length.allowed))))


# --- detectors ------------------------------------------------------------

def detect_variant_invariants():
    for s, a in VARIANT_SITES:
        ref = AyahRef(s, a)
        text = TB.ayah(ref)
        plain = phonemize(text, edition="tanzil", ref=ref).segments[0].phones
        (vs,) = enumerate_variants(text, edition="tanzil", ref=ref)
        modes = {}
        for v in vs:
            modes.setdefault(v.mode, v)
        su = modes["sukun"]
        assert [_sig(p) for p in su.phones] == [_sig(p) for p in plain]
        if "ishmam" in modes:
            ish = modes["ishmam"]
            assert [_sig(p) for p in ish.phones] == \
                [_sig(p) for p in su.phones]
        if "rawm" in modes:
            rw = modes["rawm"]
            assert rw.phones[-1].kind == "vowel"
            assert rw.phones[-1].pausal_role == "rawm"
            assert rw.phones[-2].qalqalah is None
            w = rw.phones[-2].word_index
            for p in rw.phones:
                if p.word_index == w and p.length is not None \
                        and p.length.kind == "free":
                    assert 6 not in p.length.allowed
    # admissibility of the fixed sites
    for s, a, allowed in [(1, 2, {"sukun"}), (75, 16, {"sukun"}),
                          (74, 55, {"sukun", "rawm", "ishmam"}),
                          (1, 1, {"sukun", "rawm"})]:
        (vs,) = enumerate_variants(TB.ayah(AyahRef(s, a)), edition="tanzil",
                                   ref=AyahRef(s, a))
        assert {v.mode for v in vs} == allowed, (s, a, {v.mode for v in vs})


def detect_stop_metamorphic():
    SHORT = {Base.FATHA, Base.DAMMA, Base.KASRA}
    for s, a in STOP_SITES:
        ref = AyahRef(s, a)
        text = TB.ayah(ref)
        base = phonemize(text, edition="tanzil", ref=ref).segments[0].phones
        nw = max(p.word_index for p in base) + 1
        bw = {}
        for p in base:
            bw.setdefault(p.word_index, []).append(_sig(p))
        for k in range(nw - 1):
            res = phonemize(text, edition="tanzil", ref=ref,
                            waqf=WaqfSpec(stops=(k,)))
            s1, s2 = res.segments
            w2 = {}
            for p in s2.phones:
                w2.setdefault(p.word_index, []).append(_sig(p))
            for wi in range(k + 2, nw):
                assert w2.get(wi) == bw.get(wi), (s, a, k, wi)
            last = s1.phones[-1]
            assert not (last.kind == "vowel" and last.base in SHORT
                        and last.pausal_role is None), (s, a, k)
            first = s2.phones[0]
            assert first.kind == "consonant" and not first.geminated, (s, a, k)


def detect_junction_classes():
    for (s1, a1), (s2, a2) in JUNCTION_PAIRS:
        r1, r2 = AyahRef(s1, a1), AyahRef(s2, a2)
        t1, t2 = TB.ayah(r1), TB.ayah(r2)
        n1 = max(p.word_index for p in
                 phonemize(t1, edition="tanzil", ref=r1).segments[0].phones) + 1
        ph = phonemize_concat([(r1, t1), (r2, t2)],
                              edition="tanzil").segments[0].phones
        tail = [p for p in ph if p.word_index == n1 - 1]
        head = [p for p in ph if p.word_index == n1]
        if (s1, a1) == (15, 1):        # bila ghunna into reh
            assert tail[-1].base not in (Base.NOON, Base.NOON_MUKHFAH)
            hc = next(p for p in head if p.kind != "vowel")
            assert hc.base is Base.REH and hc.geminated
        if (s1, a1) == (9, 79):        # wiqaya
            assert any(p.base is Base.NOON for p in tail[-3:])
            assert tail[-1].base in (Base.KASRA, Base.NOON)
        if (s1, a1) == (27, 1):        # izhar before haa
            assert any(p.base is Base.NOON for p in tail[-2:])


DETECTORS = [detect_variant_invariants, detect_stop_metamorphic,
             detect_junction_classes]


def killed():
    out = []
    for d in DETECTORS:
        try:
            d()
        except AssertionError:
            out.append(d.__name__)
        except Exception:
            out.append(d.__name__ + "(error)")
    return out


def test_detectors_pass_on_healthy_engine():
    assert killed() == []


# --- mutants --------------------------------------------------------------

def test_mutant_rawm_keeps_muttasil_six(monkeypatch):
    """Resurrect THE bug: rawm without the 6-drop branch."""
    def old_rawm(seg_phones, haraka):
        word = seg_phones[-1].word_index
        from quran_g2p.ir import Phone, RuleApp
        app = RuleApp("R123_RAWM", "SPEC-123", seg_phones[-1].src_span)
        out = []
        for p in seg_phones:
            if p.word_index == word and p.length is not None \
                    and p.length.kind == "free" and 2 in p.length.allowed:
                p = _replace(p, length=VR._QASR,
                             provenance=p.provenance + (app,))
            out.append(p)
        out[-1] = _replace(out[-1], qalqalah=None,
                           provenance=out[-1].provenance + (app,))
        out.append(Phone(base=haraka, kind="vowel", geminated=False,
                         length=None, ghunna=None, qalqalah=None,
                         tafkheem=out[-1].tafkheem, sakt_after=False,
                         pausal_role="rawm", provenance=(app,),
                         src_span=out[-1].src_span,
                         word_index=out[-1].word_index))
        return out
    monkeypatch.setattr(VR, "_rawm", old_rawm)
    assert "detect_variant_invariants" in killed()


def test_mutant_rawm_keeps_qalqalah(monkeypatch):
    orig = VR._rawm

    def patched(seg_phones, haraka):
        out = list(orig(seg_phones, haraka))
        out[-2] = _replace(out[-2], qalqalah=seg_phones[-1].qalqalah)
        return tuple(out)
    monkeypatch.setattr(VR, "_rawm", patched)
    assert "detect_variant_invariants" in killed()


def test_mutant_rawm_on_fath(monkeypatch):
    orig = VR.isharah_modes

    def patched(final_haraka, prev, **kw):
        return frozenset(orig(final_haraka, prev, **kw) | {"rawm"})
    monkeypatch.setattr(VR, "isharah_modes", patched)
    assert "detect_variant_invariants" in killed()


def test_mutant_ishmam_on_kasr(monkeypatch):
    orig = VR.isharah_modes

    def patched(final_haraka, prev, **kw):
        m = orig(final_haraka, prev, **kw)
        return frozenset(m | {"ishmam"}) if "rawm" in m else m
    monkeypatch.setattr(VR, "isharah_modes", patched)
    assert "detect_variant_invariants" in killed()


def test_mutant_ishmam_mutates_phones(monkeypatch):
    orig = VR._ishmam

    def patched(seg_phones):
        v = list(orig(seg_phones))
        v[-1] = _replace(v[-1], geminated=not v[-1].geminated)
        return tuple(v)
    monkeypatch.setattr(VR, "_ishmam", patched)
    assert "detect_variant_invariants" in killed()


def test_mutant_iskan_skipped_midstop(monkeypatch):
    orig = PZ._p4_pausal
    monkeypatch.setattr(PZ, "_p4_pausal", lambda segs, trace: segs)
    assert "detect_stop_metamorphic" in killed()


def test_mutant_resume_keeps_gemination(monkeypatch):
    monkeypatch.setattr(PZ, "_p3_strip_initial_shadda",
                        lambda segs, trace: segs)
    ks = killed()
    assert "detect_stop_metamorphic" in ks or \
        "detect_variant_invariants" in ks


def test_mutant_junction_wiqaya_dropped(monkeypatch):
    orig = PZ._p6_p7_noon_meem

    def patched(phones, trace):
        out = orig(phones, trace)
        # strip the wiqaya noon+kasra the junction inserted: emulate a
        # regression by deleting any noon that directly precedes a kasra
        # vowel at a word tail followed by a new word
        res = []
        for i, p in enumerate(out):
            if (p.base is Base.NOON and i + 1 < len(out)
                    and out[i + 1].base is Base.KASRA
                    and i + 2 < len(out)
                    and out[i + 2].word_index != p.word_index):
                continue
            res.append(p)
        return res
    monkeypatch.setattr(PZ, "_p6_p7_noon_meem", patched)
    assert "detect_junction_classes" in killed()


def test_mutant_junction_idgham_disabled(monkeypatch):
    orig = PZ._p6_p7_noon_meem

    def patched(phones, trace):
        return phones     # no noon rules at all
    monkeypatch.setattr(PZ, "_p6_p7_noon_meem", patched)
    ks = killed()
    assert "detect_junction_classes" in ks
