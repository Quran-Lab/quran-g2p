"""Haa al-kinaya — the complete Hafs farsh, sourced and frozen (SPEC-100).

Shatibiyya bayts 158-159, 164, 166-168 (Matn 1:13); Siraj al-Qari 1:45-48;
al-Wafi 1:67-72; Fath al-Wasid 1:317-324; al-Nashr 1:306; al-Taysir 1:29-30;
Hidayat al-Qari 1:359. Silah drops at waqf («الصلة تسقط في الوقف» — Siraj
al-Qari 1:45) — the R183 basis. The rasm carries all eight rulings; these
tests freeze that the engine reads them.
"""
from quran_g2p.ir import Base
from quran_g2p.phonemize import phonemize
from quran_g2p.textbank import AyahRef, TextBank

TB = TextBank.load("tanzil")


def heh_contexts(s, a):
    ref = AyahRef(s, a)
    (seg,) = phonemize(TB.ayah(ref), edition="tanzil", ref=ref).segments
    ph = seg.phones
    out = []
    for i, p in enumerate(ph):
        if p.base is Base.HEH:
            nxt = ph[i + 1].base if i + 1 < len(ph) else None
            nxt2 = ph[i + 2].base if i + 2 < len(ph) else None
            out.append((nxt, nxt2))
    return out


def test_yardahu_39_7_qasr():
    # damma with NO silah waw (Shatibiyya 164 «والقصر فاذكره نوفلا»)
    assert (Base.DAMMA, Base.LAM) in heh_contexts(39, 7)


def test_fihi_muhanan_25_69_silah_after_sakin():
    # the SOLE Hafs silah-after-sakin (Shatibiyya 159 «وفيه مهانا معه حفص»)
    assert (Base.KASRA, Base.YEH_MADD) in heh_contexts(25, 69)


def test_arjih_7_111_and_26_36_iskan():
    # haa sakin (Shatibiyya 166-167 «وأسكن نصيرا فاز»)
    for s, a in ((7, 111), (26, 36)):
        ctxs = heh_contexts(s, a)
        assert any(nxt is Base.WAW for nxt, _ in ctxs), (s, a)


def test_faalqih_27_28_iskan():
    assert any(nxt is Base.HAMZA for nxt, _ in heh_contexts(27, 28))


def test_yattaqhi_24_52_qaf_sakin_haa_qasr():
    # «وقل بسكون القاف والقصر حفصهم» (bayt 162/168 by edition)
    ref = AyahRef(24, 52)
    (seg,) = phonemize(TB.ayah(ref), edition="tanzil", ref=ref).segments
    ph = seg.phones
    i = next(k for k in range(len(ph) - 2)
             if ph[k].base is Base.QAF and ph[k + 1].base is Base.HEH)
    assert ph[i + 2].base is Base.KASRA
    assert i + 3 >= len(ph) or ph[i + 3].kind != "madd"  # no silah


def test_ansaniihu_18_63_and_alayhu_48_10_damm():
    # the two haraka-specials: haa takes DAMM
    assert (Base.DAMMA, Base.HAMZA) in heh_contexts(18, 63)
    assert (Base.DAMMA, Base.LAM) in heh_contexts(48, 10)
