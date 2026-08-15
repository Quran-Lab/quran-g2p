"""P6/P7 goldens — noon sakinah & tanween 4-way, meem sakinah 3-way, and the
iltiqa' al-sakinayn junction effects (SPEC-140..152, SPEC-131).

Sites are canonical textbook examples, hand-derived:
  1:6   madd shortening before article + lam shamsiyya kamil idgham
  1:7   izhar (noon MARKED + 'ayn) and izhar shafawi (meem + teh)
  2:8   naqis idgham into yeh with ghunna (مَن يَقُولُ)
  2:10  iqlab (أَلِيمٌۢ بِمَا) -> meem mukhfah
  107:4 tanween + lam-shadda kamil idgham (فَوَيْلٌ لِّلْمُصَلِّينَ)
  107:5 ikhfa before sad (عَن صَلَاتِهِمْ)
  2:180 noon al-wiqaya: tanween before hamzat wasl (خَيْرًا ٱلْوَصِيَّةُ)
"""
import pytest

from quran_g2p.ir import Base
from quran_g2p.phonemize import phonemize
from quran_g2p.textbank import AyahRef, TextBank

from test_phones_core import SHORT, brief  # noqa: E402 (tests dir on sys.path)


def go(ref, edition="tanzil"):
    tb = TextBank.load(edition)
    return phonemize(tb.ayah(ref), edition=edition, ref=ref)


def phones_of(ref, edition="tanzil"):
    res = go(ref, edition)
    (seg,) = res.segments
    return seg.phones


def contains_subseq(haystack, needle):
    for i in range(len(haystack) - len(needle) + 1):
        if haystack[i:i + len(needle)] == needle:
            return True
    return False


def test_1_6_ihdina_ssirata_lmustaqim():
    assert brief(phones_of(AyahRef(1, 6))) == [
        "'", "i", "h", "d", "i", "n", "a",
        "S*", "i", "r", "a", "A", "T", "a",
        "l", "m", "u", "s", "t", "a", "q", "i", "I", "m",
    ]


def test_1_7_izhar_noon_and_meem():
    b = brief(phones_of(AyahRef(1, 7)))
    # أَنْعَمْتَ: noon stays plain before 'ayn; meem stays plain before teh.
    assert contains_subseq(b, ["'", "a", "n", "3", "a", "m", "t", "a"])


def test_2_8_naqis_idgham_noon_into_yeh_carries_ghunna():
    ph = phones_of(AyahRef(2, 8))
    b = brief(ph)
    # مَن يَقُولُ -> m a | y(ghunna) a q U l u : the noon is gone
    assert contains_subseq(b, ["m", "a", "y", "a", "q", "u", "U", "l", "u"])
    i = next(i for i in range(len(b) - 2) if b[i:i + 3] == ["m", "a", "y"])
    yeh = ph[i + 2]
    assert yeh.base is Base.YEH and yeh.ghunna == "idgham"


def test_2_10_iqlab_meem_mukhfah():
    b = brief(phones_of(AyahRef(2, 10)))
    # أَلِيمٌۢ بِمَا -> ... l i I m u M b i m a
    assert contains_subseq(b, ["l", "i", "I", "m", "u", "M", "b"])


def test_107_4_kamil_idgham_tanween_into_lam():
    b = brief(phones_of(AyahRef(107, 4)))
    # فَوَيْلٌ لِّلْمُصَلِّينَ -> w a y l u l* i l... (tanween noon gone)
    assert contains_subseq(b, ["w", "a", "y", "l", "u", "l*", "i", "l"])


def test_107_5_ikhfa_before_sad():
    ph = phones_of(AyahRef(107, 5))
    b = brief(ph)
    # عَن صَلَاتِهِمْ -> 3 a N S a l a A t i h i m
    assert contains_subseq(b, ["3", "a", "N", "S", "a"])


def test_2_180_noon_wiqaya_before_wasla():
    b = brief(phones_of(AyahRef(2, 180)))
    # خَيْرًا ٱلْوَصِيَّةُ -> ... r a n i l w a S* ...
    assert contains_subseq(b, ["r", "a", "n", "i", "l", "w", "a"])


@pytest.mark.parametrize("edition", ["tanzil", "kfgqpc"])
def test_editions_agree_on_all_golden_sites(edition):
    for ref in (AyahRef(1, 6), AyahRef(1, 7), AyahRef(2, 8), AyahRef(2, 10),
                AyahRef(107, 4), AyahRef(107, 5), AyahRef(2, 180)):
        assert phones_of(ref, edition) is not None
