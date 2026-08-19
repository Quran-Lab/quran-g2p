"""P2-full farsh: the waqf rulings only reachable at mid-ayah stops.

Sites and rulings all sourced in the register: مصر tafkheem / القطر
tarqeeq (al-Nashr 2:105), فَأَسْرِ tarqeeq muqaddam (2:110), سلاسلا waqf
wajhan (printed dabt selects hadhf; ithbat = knob), آتاني waqf wajhan
(ithbat muqaddam, Hidayat al-Qari 2:544-545), أنا/لكنا realize the
rectangular-zero alif at waqf, أيه stops on the sakin haa.
"""
from quran_g2p.config import HafsConfig
from quran_g2p.ir import Base
from quran_g2p.phonemize import phonemize
from quran_g2p.textbank import AyahRef, TextBank
from quran_g2p.waqf import WaqfSpec

TB = TextBank.load("tanzil")


def stop_after_word(s, a, needle, config=None):
    """Phonemize with a stop right after the word containing `needle`;
    return that segment's phones."""
    ref = AyahRef(s, a)
    words = TB.ayah(ref).split(" ")
    k = next(i for i, w in enumerate(words) if needle in w)
    res = phonemize(TB.ayah(ref), edition="tanzil", ref=ref, config=config,
                    waqf=WaqfSpec(stops=(k,)))
    return res.segments[0].phones


def test_misr_waqf_tafkheem_default():
    # 12:99 ٱدْخُلُوا۟ مِصْرَ: waqf on misr -> reh MOFAKHAM (al-Nashr's
    # ikhtiyar, misr_waqf_tafkheem=True default)
    ph = stop_after_word(12, 99, "مِصْرَ")
    assert ph[-1].base is Base.REH and ph[-1].tafkheem == "mofakham"


def test_misr_waqf_tarqeeq_knob():
    ph = stop_after_word(12, 99, "مِصْرَ",
                         config=HafsConfig(misr_waqf_tafkheem=False))
    assert ph[-1].base is Base.REH and ph[-1].tafkheem == "moraqaq"


def test_qitr_waqf_tarqeeq_default():
    # 34:12 عَيْنَ ٱلْقِطْرِ: waqf -> reh MURAQQAQ (qitr_waqf_tafkheem=False)
    ph = stop_after_word(34, 12, "ٱلْقِطْرِ")
    assert ph[-1].base is Base.REH and ph[-1].tafkheem == "moraqaq"


def test_asr_waqf_tarqeeq_default():
    # 11:81 فَأَسْرِ بِأَهْلِكَ: waqf -> tarqeeq muqaddam (kasrat al-binaa)
    ph = stop_after_word(11, 81, "فَأَسْرِ")
    assert ph[-1].base is Base.REH and ph[-1].tafkheem == "moraqaq"


def test_salasila_waqf_hadhf_default():
    # 76:4 سَلَٰسِلَا۟: printed round-zero dabt selects HADHF -> ends lam
    ph = stop_after_word(76, 4, "سَلَٰسِلَا۟")
    assert ph[-1].base is Base.LAM
    assert ph[-1].kind == "consonant"


def test_salasila_waqf_ithbat_knob():
    ph = stop_after_word(76, 4, "سَلَٰسِلَا۟",
                         config=HafsConfig(salasila_waqf_alif=True))
    assert ph[-1].base is Base.ALEF_MADD
    assert ph[-1].length.canonical == 2


def test_aataani_waqf_ithbat_default():
    # 27:36 ءَاتَىٰنِۦَ: ithbat of the sakin yaa is muqaddam -> the final
    # yaa is a madd letter after the kasra
    ph = stop_after_word(27, 36, "ءَاتَىٰنِ")
    assert ph[-1].base is Base.YEH_MADD
    assert ph[-2].base is Base.KASRA


def test_aataani_waqf_hadhf_knob():
    ph = stop_after_word(27, 36, "ءَاتَىٰنِ",
                         config=HafsConfig(aataani_waqf_yaa=False))
    assert ph[-1].base is Base.NOON


def test_ana_waqf_realizes_alif():
    # 2:258 أَنَا۠: the rectangular-zero alif is REALIZED at a stop on it
    ph = stop_after_word(2, 258, "أَنَا۠")
    assert ph[-1].base is Base.ALEF_MADD
    assert ph[-1].length.canonical == 2


def test_lakinna_waqf_realizes_alif():
    # 18:38 لَّٰكِنَّا۠
    ph = stop_after_word(18, 38, "كِنّ")
    assert ph[-1].base is Base.ALEF_MADD


def test_ayyuha_waqf_on_haa():
    # 43:49 يَٰٓأَيُّهَ: Hafs stops on the sakin haa following the rasm
    ph = stop_after_word(43, 49, "يُّه")
    assert ph[-1].base is Base.HEH
    assert ph[-1].kind == "consonant"


def _skel(w):
    return "".join(c for c in w if not (0x064B <= ord(c) <= 0x0652
                                        or ord(c) in (0x0670, 0x0653)))


def test_open_taa_stops_as_taa_not_haa():
    # 43:32 رَحْمَتَ is written with OPEN taa (rasm), so waqf keeps the
    # taa sakinah; the haa conversion (R122) triggers on taa MARBUTA only
    # (al-Nashr 2:131-133, statement row sup2-taa-maftuha-waqf).
    ref = AyahRef(43, 32)
    words = TB.ayah(ref).split(" ")
    k = next(i for i, w in enumerate(words) if "رحمت" in _skel(w))
    res = phonemize(TB.ayah(ref), edition="tanzil", ref=ref,
                    waqf=WaqfSpec(stops=(k,)))
    ph = res.segments[0].phones
    assert ph[-1].base is Base.TEH      # open taa stands at waqf
    assert ph[-1].base is not Base.HEH  # and is never converted to haa
