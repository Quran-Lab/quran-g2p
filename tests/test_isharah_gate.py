"""Rawm/ishmam eligibility at waqf — the tafsil gate (SPEC-123 + SPEC-183).

Ibn al-Jazari's chosen madhhab («وهو أعدل المذاهب عندي» — al-Nashr 2:124,
Tayyiba «وخلف ها الضمير وامنع في الأتم من بعد يا أو واو أو كسر وضم»),
followed by al-Banna (Ithaf 1:135-136), al-Safaqusi (Ghayth al-Naf
1:86-87), al-Marsafi (Hidayat al-Qari 1:322, 1:327-328): on the pronoun
haa, no rawm/ishmam after damm, sakin waw, kasr, or sakin yaa; permitted
after fath, alif, or sakin sahih. Haa as-sakt takes neither, ever (it is
a sakin haa with no underlying haraka — al-Iqna' 1:244). General finals:
rawm on damm+kasr, ishmam on damm only (SPEC-123).

Contexts are extracted from phonemized pinned-corpus ayat, never typed.
"""
import pytest

from quran_g2p.ir import Base
from quran_g2p.phonemize import phonemize
from quran_g2p.textbank import AyahRef, TextBank
from quran_g2p.waqf import isharah_modes

TB = TextBank.load("tanzil")

S, R, I = "sukun", "rawm", "ishmam"


def haa_ctx(s, a, prev_base, haraka):
    """Locate a pronoun-haa context (prev phone, haa haraka) in the ayah."""
    ref = AyahRef(s, a)
    (seg,) = phonemize(TB.ayah(ref), edition="tanzil", ref=ref).segments
    ph = seg.phones
    for i in range(1, len(ph) - 1):
        if (ph[i].base is Base.HEH and ph[i - 1].base is prev_base
                and ph[i + 1].base is haraka):
            return ph[i - 1], haraka
    raise AssertionError(f"context not found in {s}:{a}")


# --- the five voweled farsh sites, per al-Nashr 2:124-125 ---------------

def test_yardahu_39_7_all_three():
    # damm after FATH -> sukun + rawm + ishmam
    prev, h = haa_ctx(39, 7, Base.FATHA, Base.DAMMA)
    assert isharah_modes(h, prev, pronoun_haa=True) == frozenset({S, R, I})


def test_fihi_25_69_sukun_only():
    # kasr after sakin YAA -> sukun only
    prev, h = haa_ctx(25, 69, Base.YEH_MADD, Base.KASRA)
    assert isharah_modes(h, prev, pronoun_haa=True) == frozenset({S})


def test_yattaqhi_24_52_sukun_and_rawm():
    # kasr after sakin sahih QAF -> rawm yes («ويتقه لحفص» in the jawaz
    # examples), ishmam no (maksura)
    prev, h = haa_ctx(24, 52, Base.QAF, Base.KASRA)
    assert isharah_modes(h, prev, pronoun_haa=True) == frozenset({S, R})


def test_ansaniihu_18_63_sukun_only():
    # damm after sakin YAA -> sukun only (al-Kanz 1:334 lists it)
    prev, h = haa_ctx(18, 63, Base.YEH_MADD, Base.DAMMA)
    assert isharah_modes(h, prev, pronoun_haa=True) == frozenset({S})


def test_alayhu_48_10_sukun_only():
    # damm after LEEN yaa -> sukun only (عليه is al-Nashr's own example)
    prev, h = haa_ctx(48, 10, Base.YEH, Base.DAMMA)
    assert isharah_modes(h, prev, pronoun_haa=True) == frozenset({S})


# --- the general tafsil contexts ----------------------------------------

def test_minhu_after_sakin_sahih_all_three():
    # 2:60 مِنْهُ: damm after sakin NOON -> all three
    prev, h = haa_ctx(2, 60, Base.NOON, Base.DAMMA)
    assert isharah_modes(h, prev, pronoun_haa=True) == frozenset({S, R, I})


def test_bihi_after_kasr_sukun_only():
    # 2:90 بِهِ: kasr after kasr -> sukun only
    prev, h = haa_ctx(2, 90, Base.KASRA, Base.KASRA)
    assert isharah_modes(h, prev, pronoun_haa=True) == frozenset({S})


def test_hadaahu_after_alif_all_three():
    # 39:18? هَدَىٰهُ occurs 6:71? use 16:121 هَدَىٰهُ: damm after alif -> all
    prev, h = haa_ctx(16, 121, Base.ALEF_MADD, Base.DAMMA)
    assert isharah_modes(h, prev, pronoun_haa=True) == frozenset({S, R, I})


def test_amruhu_after_damm_sukun_only():
    # 2:275 وَأَمْرُهُۥٓ: damm after damm -> sukun only
    prev, h = haa_ctx(2, 275, Base.DAMMA, Base.DAMMA)
    assert isharah_modes(h, prev, pronoun_haa=True) == frozenset({S})


# --- general (non-pronoun) finals: SPEC-123 legality --------------------

def test_general_damm_all_three():
    prev, h = haa_ctx(2, 60, Base.NOON, Base.DAMMA)  # context reuse
    assert isharah_modes(Base.DAMMA, None) == frozenset({S, R, I})


def test_general_kasr_no_ishmam():
    assert isharah_modes(Base.KASRA, None) == frozenset({S, R})


def test_general_fath_sukun_only():
    # rawm/ishmam never on fath (al-Nashr 2:121)
    assert isharah_modes(Base.FATHA, None) == frozenset({S})


def test_already_sakin_sukun_only():
    # arjih-type iskan finals and any sakin ending: nothing to indicate
    assert isharah_modes(None, None) == frozenset({S})


# --- haa as-sakt: never (al-Iqna' 1:244; Lataif 9:75) -------------------

HAA_SAKT_AYAH_FINAL = [(69, 19), (69, 20), (69, 25), (69, 26), (69, 28),
                       (69, 29), (101, 10)]
HAA_SAKT_MID = [(2, 259), (6, 90)]  # يتسنه، اقتده


@pytest.mark.parametrize("s,a", HAA_SAKT_AYAH_FINAL)
def test_haa_sakt_final_is_sakin_and_sukun_only(s, a):
    ref = AyahRef(s, a)
    (seg,) = phonemize(TB.ayah(ref), edition="tanzil", ref=ref).segments
    ph = seg.phones
    assert ph[-1].base is Base.HEH  # sakin haa closes the ayah
    assert isharah_modes(None, ph[-2], haa_sakt=True) == frozenset({S})


@pytest.mark.parametrize("s,a", HAA_SAKT_MID)
def test_haa_sakt_mid_ayah_sakin_in_wasl(s, a):
    # rasm-carried: the haa stays sakin in wasl too (thabita for Hafs)
    ref = AyahRef(s, a)
    (seg,) = phonemize(TB.ayah(ref), edition="tanzil", ref=ref).segments
    ph = seg.phones
    hit = any(ph[i].base is Base.HEH and ph[i + 1].kind == "consonant"
              for i in range(len(ph) - 1))
    assert hit, f"no sakin haa in wasl at {s}:{a}"


# --- the five-sanf exclusions (al-Nashr 2:122-124) -----------------------

def test_ta_marbuta_sukun_only():
    # sanf 3: the waqf-haa replacing ta marbuta carries no i'rab ->
    # sukun only (101:1 al-qari'atu, wasl haraka damma)
    ref = AyahRef(101, 1)
    (seg,) = phonemize(TB.ayah(ref), edition="tanzil", ref=ref).segments
    prev = seg.phones[-2]
    assert isharah_modes(Base.DAMMA, prev, ta_marbuta=True) == frozenset({S})


def test_arid_haraka_sukun_only():
    # sanf 5: a naql/iltiqa haraka is 'arida -> sukun only, whatever it is
    assert isharah_modes(Base.DAMMA, None, arid_haraka=True) == frozenset({S})
    assert isharah_modes(Base.KASRA, None, arid_haraka=True) == frozenset({S})


def test_written_taa_keeps_isharah():
    # al-Nashr 2:126 tanbih: stopping on a word WRITTEN with open taa
    # stops on the i'rab-bearing letter itself -> isharah runs normally
    assert isharah_modes(Base.KASRA, None) == frozenset({S, R})
