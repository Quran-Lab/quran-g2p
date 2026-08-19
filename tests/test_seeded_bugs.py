"""«فَٱرْجِعِ ٱلْبَصَرَ هَلْ تَرَىٰ مِن فُطُورٍ ۝ ثُمَّ ٱرْجِعِ ٱلْبَصَرَ كَرَّتَيْنِ يَنقَلِبْ إِلَيْكَ ٱلْبَصَرُ خَاسِئًا وَهُوَ حَسِيرٌ» — الملك 3–4
"Return your gaze: do you see any flaw? Then return your gaze twice again —
your sight will come back to you humbled and weary." (al-Mulk 3–4)

Seeded-bug drill (A6 criterion 6): each hand-designed mutant must be
KILLED by at least one harness detector. This measures the harness, not the
engine — a surviving mutant means a blind spot, and the kill matrix documents
which layer catches which failure class.
"""
import pytest

import quran_g2p.phonemize as PZ
from quran_g2p.ir import Base
from quran_g2p.phonemize import phonemize
from quran_g2p.textbank import AyahRef, TextBank

TB = TextBank.load("tanzil")


def phones_of(ref):
    (seg,) = phonemize(TB.ayah(ref), edition="tanzil", ref=ref).segments
    return seg.phones


# --- detectors (thin probes over existing golden/invariant facts) ---------

def detect_izhar_mutlaq_dunya():
    # 2:85 ٱلدُّنْيَا: the same-word noon right before yeh must SURVIVE
    # (izhar — whether via the dabt-marked gate or the izhar-mutlaq branch).
    ph = phones_of(AyahRef(2, 85))
    ok = False
    for i, p in enumerate(ph):
        if (p.base is Base.NOON and p.ghunna == "asl" and i + 1 < len(ph)
                and ph[i + 1].base is Base.YEH
                and ph[i + 1].word_index == p.word_index):
            ok = True
    assert ok


def detect_munfasil_sets():
    ph = [p for p in phones_of(AyahRef(2, 4)) if p.kind == "madd"]
    assert any(p.length.allowed == frozenset({4, 5}) for p in ph)


def detect_sakt_noon_survives():
    ph = phones_of(AyahRef(75, 27))
    assert any(p.base is Base.NOON and p.sakt_after for p in ph)


def detect_initial_shadda_stripped():
    ph = phones_of(AyahRef(2, 177))
    assert not ph[0].geminated


def detect_iqlab_meem():
    ph = phones_of(AyahRef(2, 10))
    assert any(p.base is Base.MEEM_MUKHFAH for p in ph)


def detect_jalala_alif():
    ph = phones_of(AyahRef(112, 1))
    lams = [i for i, p in enumerate(ph) if p.base is Base.LAM and p.geminated]
    assert lams and ph[lams[0] + 2].kind == "madd"


def detect_aared_final():
    ph = [p for p in phones_of(AyahRef(1, 1)) if p.kind == "madd"]
    assert ph[-1].length.allowed == frozenset({2, 4, 6})


DETECTORS = [
    detect_izhar_mutlaq_dunya, detect_munfasil_sets, detect_sakt_noon_survives,
    detect_initial_shadda_stripped, detect_iqlab_meem, detect_jalala_alif,
    detect_aared_final,
]


def killed_by_any():
    kills = []
    for d in DETECTORS:
        try:
            d()
        except AssertionError:
            kills.append(d.__name__)
        except Exception:
            kills.append(d.__name__ + "(error)")
    return kills


# --- mutants --------------------------------------------------------------

def test_mutant_idgham_through_marked_sukun(monkeypatch):
    """Ignore the MARKED-sukun izhar gate: 75:27's noon gets deleted."""
    orig = PZ._note
    monkeypatch.setattr(PZ, "_note", lambda p: orig(p).replace("sukun:marked", "sukun:bare"))
    kills = killed_by_any()
    assert kills, "mutant survived: marked-sukun gate has no detector"


def test_mutant_no_initial_shadda_strip(monkeypatch):
    monkeypatch.setattr(PZ, "_p3_strip_initial_shadda", lambda segs, trace: segs)
    kills = killed_by_any()
    assert "detect_initial_shadda_stripped" in kills


def test_mutant_no_iqlab(monkeypatch):
    orig = PZ._p6_p7_noon_meem

    def patched(phones, trace):
        out = orig(phones, trace)
        from dataclasses import replace
        return [replace(p, base=Base.NOON, ghunna=None)
                if p.base is Base.MEEM_MUKHFAH else p for p in out]
    monkeypatch.setattr(PZ, "_p6_p7_noon_meem", patched)
    kills = killed_by_any()
    assert "detect_iqlab_meem" in kills


def test_mutant_munfasil_fixed_two(monkeypatch):
    orig = PZ._free

    def patched(allowed, canonical, scoring):
        if allowed == {4, 5} or allowed == frozenset({4, 5}):
            return orig({2}, 2, {2})
        return orig(allowed, canonical, scoring)
    monkeypatch.setattr(PZ, "_free", patched)
    kills = killed_by_any()
    assert "detect_munfasil_sets" in kills


def test_mutant_no_jalala(monkeypatch):
    monkeypatch.setattr(PZ, "_is_jalala_word", lambda segs, word: False)
    kills = killed_by_any()
    assert "detect_jalala_alif" in kills


def test_mutant_aared_ignores_arid(monkeypatch):
    orig = PZ._p10_madd

    def patched(phones, trace, config):
        out = orig(phones, trace, config)
        from dataclasses import replace
        return [replace(p, length=PZ._TABEEI)
                if p.length is not None and p.length.allowed == frozenset({2, 4, 6})
                else p for p in out]
    monkeypatch.setattr(PZ, "_p10_madd", patched)
    kills = killed_by_any()
    assert "detect_aared_final" in kills


def test_mutant_izhar_mutlaq_dropped(monkeypatch):
    orig = PZ._p6_p7_noon_meem

    def patched(phones, trace):
        out = orig(phones, trace)
        # simulate: same-word noon+yeh wrongly idghams (delete those noons)
        keep = []
        for i, p in enumerate(out):
            if (p.base is Base.NOON and i + 1 < len(out)
                    and out[i + 1].base is Base.YEH
                    and out[i + 1].word_index == p.word_index):
                continue
            keep.append(p)
        return keep
    monkeypatch.setattr(PZ, "_p6_p7_noon_meem", patched)
    kills = killed_by_any()
    assert "detect_izhar_mutlaq_dunya" in kills


def test_all_detectors_pass_unmutated():
    assert killed_by_any() == []
