"""P9 ghunna grades, P11 qalqalah, P12 tafkheem goldens.

Sites: 103:2 (mushaddadah noon + ikhfa), 110:2 (qalqalah sughra dal),
112:3 (qalqalah kubra final dal), 112:1 vs 1:1 (lam-jalala tafkheem by
preceding vowel), 1:1 (reh mofakham + vowel/madd inheritance),
89:14 (reh sakin after kasra before isti'la -> mofakham).
"""
from quran_g2p.ir import Base
from quran_g2p.phonemize import phonemize
from quran_g2p.textbank import AyahRef, TextBank


def phones_of(ref, edition="tanzil"):
    tb = TextBank.load(edition)
    (seg,) = phonemize(tb.ayah(ref), edition=edition, ref=ref).segments
    return seg.phones


def test_103_2_mushaddadah_noon_and_ikhfa():
    ph = phones_of(AyahRef(103, 2))
    gem_noons = [p for p in ph if p.base is Base.NOON and p.geminated]
    assert gem_noons and all(p.ghunna == "mushaddadah" for p in gem_noons)
    assert any(p.base is Base.NOON_MUKHFAH and p.ghunna == "ikhfa" for p in ph)


def test_110_2_qalqalah_sughra_mid_word():
    ph = phones_of(AyahRef(110, 2))  # يَدْخُلُونَ
    dals = [p for p in ph if p.base is Base.DAL]
    assert any(p.qalqalah == "sughra" for p in dals)


def test_112_3_qalqalah_kubra_at_waqf():
    ph = phones_of(AyahRef(112, 3))  # …وَلَمْ يُولَدْ
    assert ph[-1].base is Base.DAL and ph[-1].qalqalah == "kubra"


def test_lam_jalala_tafkheem_follows_preceding_vowel():
    # 112:1 …هُوَ ٱللَّهُ: prev vowel a -> mofakham
    ph = phones_of(AyahRef(112, 1))
    gem_lams = [p for p in ph if p.base is Base.LAM and p.geminated]
    assert gem_lams[0].tafkheem == "mofakham"
    # 1:1 بِسْمِ ٱللَّهِ: prev vowel i -> moraqaq
    ph = phones_of(AyahRef(1, 1))
    gem_lams = [p for p in ph if p.base is Base.LAM and p.geminated]
    assert gem_lams[0].tafkheem == "moraqaq"


def test_1_1_reh_mofakham_and_inheritance():
    ph = phones_of(AyahRef(1, 1))
    rehs = [i for i, p in enumerate(ph) if p.base is Base.REH]
    assert ph[rehs[0]].tafkheem == "mofakham"
    # the fatha right after inherits
    assert ph[rehs[0] + 1].tafkheem == "mofakham"


def test_89_14_reh_sakin_after_kasra_before_istila_is_mofakham():
    ph = phones_of(AyahRef(89, 14))  # لَبِٱلْمِرْصَادِ
    rehs = [p for p in ph if p.base is Base.REH]
    assert any(p.tafkheem == "mofakham" for p in rehs)


def test_istila_letters_default_mofakham_low_with_kasra():
    ph = phones_of(AyahRef(1, 6))  # ٱلصِّرَٰطَ: sad with kasra -> low_mofakham
    sads = [p for p in ph if p.base is Base.SAD]
    assert sads and sads[0].tafkheem == "low_mofakham"
    tahs = [p for p in ph if p.base is Base.TAH]
    assert tahs and tahs[0].tafkheem == "mofakham"
