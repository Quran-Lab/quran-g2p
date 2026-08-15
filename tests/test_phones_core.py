"""End-to-end phone emission goldens: P2 waqf split -> P3 ibtida' (v1) ->
P4 pausal -> emission -> (P5 wasl elision, lam-jalala alif).

Golden notation: consonants by a short letter code ('*' = geminated), vowels
a/u/i, madd phones A/U/I (length classification is P10's job and not asserted
here), pausal-sakin implicit by absence of a following vowel.
"""
import pytest

from quran_g2p.config import HafsConfig
from quran_g2p.ir import Base, Phone
from quran_g2p.phonemize import phonemize
from quran_g2p.textbank import AyahRef, TextBank

SHORT = {
    Base.HAMZA: "'", Base.BEH: "b", Base.TEH: "t", Base.THEH: "th", Base.JEEM: "j",
    Base.HAH: "H", Base.KHAH: "x", Base.DAL: "d", Base.THAL: "dh", Base.REH: "r",
    Base.ZAIN: "z", Base.SEEN: "s", Base.SHEEN: "sh", Base.SAD: "S", Base.DAD: "D",
    Base.TAH: "T", Base.ZAH: "Z", Base.AIN: "3", Base.GHAIN: "gh", Base.FEH: "f",
    Base.QAF: "q", Base.KAF: "k", Base.LAM: "l", Base.MEEM: "m", Base.NOON: "n",
    Base.HEH: "h", Base.WAW: "w", Base.YEH: "y",
    Base.ALEF_MADD: "A", Base.WAW_MADD: "U", Base.YEH_MADD: "I",
    Base.FATHA: "a", Base.DAMMA: "u", Base.KASRA: "i",
    Base.NOON_MUKHFAH: "N", Base.MEEM_MUKHFAH: "M",
}


def brief(phones: list[Phone]) -> list[str]:
    out = []
    for p in phones:
        s = SHORT[p.base]
        if p.geminated:
            s += "*"
        out.append(s)
    return out


def go(ref, edition="tanzil"):
    tb = TextBank.load(edition)
    return phonemize(tb.ayah(ref), edition=edition, ref=ref)


@pytest.mark.parametrize("edition", ["tanzil", "kfgqpc"])
def test_112_1_qul_huwa_allahu_ahad(edition):
    res = go(AyahRef(112, 1), edition)
    (seg,) = res.segments
    # qul huwa (a)llahu 'ahad — wasla elided, lam-jalala geminated with the
    # implicit alif madd, final tanween dropped at waqf (iskan), dal sakin.
    assert brief(seg.phones) == [
        "q", "u", "l",
        "h", "u", "w", "a",
        "l*", "a", "A", "h", "u",
        "'", "a", "H", "a", "d",
    ]


def test_1_1_bismillah(edition="tanzil"):
    res = go(AyahRef(1, 1), edition)
    (seg,) = res.segments
    assert brief(seg.phones) == [
        "b", "i", "s", "m", "i",
        "l*", "a", "A", "h", "i",
        "r*", "a", "H", "m", "a", "A", "n", "i",
        "r*", "a", "H", "i", "I", "m",
    ]


def test_112_4_ends_with_iskan_of_tanween_and_waqf():
    # وَلَمْ يَكُن لَّهُۥ كُفُوًا أَحَدٌۢ — final ahad(un) -> iskan: ...H a d
    res = go(AyahRef(112, 4))
    (seg,) = res.segments
    assert brief(seg.phones)[-3:] == ["H", "a", "d"]
