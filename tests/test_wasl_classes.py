"""SPEC-110 word classes at ibtida' — sourced tables (2026-08-15).

Standalone-word phonemization IS resume-at-word ibtida', so these tests
exercise exactly what P2-full will rely on. Word texts are sliced from the
pinned rasm (never hand-typed).
"""
from quran_g2p.ir import Base
from quran_g2p.phonemize import phonemize
from quran_g2p.textbank import AyahRef, TextBank

TB = TextBank.load("tanzil")


def word_from(s, a, idx):
    return TB.ayah(AyahRef(s, a)).split(" ")[idx]


def start_of(text):
    (seg,) = phonemize(text, edition="tanzil").segments
    return seg.phones


def test_noun_ismuhu_gets_kasra_not_damma():
    # 61:6 ...ٱسْمُهُۥٓ أَحْمَدُ: third slot has DAMMA (ismU-hu) — without
    # the noun list the verb rule would say damm. Sources: Jazariyya 101-103.
    ayah = TB.ayah(AyahRef(61, 6))
    w = next(w for w in ayah.split(" ") if w.startswith("ٱس"))
    ph = start_of(w)
    assert ph[0].base is Base.HAMZA and ph[1].base is Base.KASRA


def test_noun_ibnata_kasra():
    # 66:12 وَمَرْيَمَ ٱبْنَتَ عِمْرَٰنَ
    ayah = TB.ayah(AyahRef(66, 12))
    w = next(w for w in ayah.split(" ") if w.startswith("ٱبْن")
             or w.startswith("ٱب"))
    ph = start_of(w)
    assert ph[0].base is Base.HAMZA and ph[1].base is Base.KASRA


def test_arida_damma_imshu_kasra():
    # 38:6 أَنِ ٱمْشُوا۟: third slot sheen has damma, but it is 'arida
    # (imshuu از امشِيوا) -> KASRA (Hidayat al-Qari 2:482).
    ayah = TB.ayah(AyahRef(38, 6))
    w = next(w for w in ayah.split(" ") if w.startswith("ٱمْش")
             or w.startswith("ٱم"))
    ph = start_of(w)
    assert ph[0].base is Base.HAMZA and ph[1].base is Base.KASRA


def test_asliyya_damma_unzur_still_damm():
    # 4:50 ٱنظُرْ: asliyya damm -> hamza + DAMMA (regression guard for the
    # verb rule around the new lists)
    ayah = TB.ayah(AyahRef(4, 50))
    w = next(w for w in ayah.split(" ") if w.startswith("ٱن"))
    ph = start_of(w)
    assert ph[0].base is Base.HAMZA and ph[1].base is Base.DAMMA


def test_badal_ibtida_utumina():
    # 2:283 ...ٱؤْتُمِنَ: ibtida' = 'UU-tumina (hamza+damma, second hamza
    # becomes waw madd).
    ayah = TB.ayah(AyahRef(2, 283))
    w = next(w for w in ayah.split(" ") if w.startswith("ٱؤ"))
    ph = start_of(w)
    assert ph[0].base is Base.HAMZA and ph[1].base is Base.DAMMA
    assert ph[2].kind == "madd" and ph[2].base is Base.WAW_MADD


def test_badal_ibtida_ituni():
    # 12:50 ٱئْتُونِى: ibtida' = 'II-tuunii (hamza+kasra, second hamza
    # becomes yaa madd).
    ayah = TB.ayah(AyahRef(12, 50))
    w = next(w for w in ayah.split(" ") if w.startswith("ٱئ")
             or w.startswith("ٱء"))
    ph = start_of(w)
    assert ph[0].base is Base.HAMZA and ph[1].base is Base.KASRA
    assert ph[2].kind == "madd" and ph[2].base is Base.YEH_MADD


def test_17_7_liyasuu_restored_waw_both_editions():
    # li-yasūʾū: seen(u) + restored waw-madd (muttasil) + hamza(u) + waw-jama'a
    # madd — «همزة بين واوين» (al-Hujja 5:85); rasm elides the first waw
    # (al-Muhkam 1:168), the engine restores it (R013).
    from quran_g2p.textbank import TextBank
    for edition in ("tanzil", "kfgqpc"):
        tb2 = TextBank.load(edition)
        ref = AyahRef(17, 7)
        (seg,) = phonemize(tb2.ayah(ref), edition=edition, ref=ref).segments
        ph = seg.phones
        i = next(k for k in range(len(ph) - 4)
                 if ph[k].base is Base.SEEN and ph[k + 1].base is Base.DAMMA
                 and ph[k + 2].kind == "madd")
        assert ph[k + 2 if False else i + 2].base is Base.WAW_MADD, edition
        assert ph[i + 2].length.allowed == frozenset({4, 5}), edition  # muttasil
        assert ph[i + 3].base is Base.HAMZA, edition
        assert ph[i + 4].base is Base.DAMMA, edition
        assert ph[i + 5].kind == "madd", edition
