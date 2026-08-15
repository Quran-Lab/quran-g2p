"""ayyuha x3 + aataani 27:36 — the last two farsh threads, closed from the
local Shamela corpus (2026-08-15).

ayyuha (43:49, 24:31, 55:31): the rasm drops the alif; Abu 'Amr/Kisa'i/
Ya'qub stop with alif against the rasm, THE REST — Hafs among them —
stop on the sakin haa following the rasm: «ووقف عليها الباقون بالحذف
اتباعا للرسم» (al-Nashr 2:142, bab al-waqf 'ala marsum al-khatt; also
2:332); «فتعين للباقين الوقف على الهاء من غير ألف اتباعا للرسم» (Siraj
al-Qari 129-131 ed. Shamela); Ghayth al-Naf' 531, 568 («النحويان يقفان
بالألف... والباقون بالسكون تبعا للرسم»); Ithaf 410. Wasl is unaffected
(haa fathted into the article) — verified here; the waqf form is plain
P4 iskan, P2-full territory, no alif logic needed for Hafs.

aataani (27:36): both waqf wajhs are Shatibiyyah-transmitted; taqdim =
ITHBAT of the sakin yaa — «والإثبات هو المقدم في الأداء على الحذف إن
وقف بهما معا» (Hidayat al-Qari 2:545). The hadhf-wujub lists in Hidayat
al-Qari 1:290-295 are TAYYIBA qasr-munfasil tahrir obligations («الأحكام
التي تجب لحفص حال القصر في المنفصل من طريق طيبة النشر» 1:291-292), not
Shatibiyyah rulings — outside our tariq.
"""
from quran_g2p.ir import Base
from quran_g2p.phonemize import phonemize
from quran_g2p.textbank import AyahRef, TextBank

TB = TextBank.load("tanzil")


def phones(s, a):
    ref = AyahRef(s, a)
    (seg,) = phonemize(TB.ayah(ref), edition="tanzil", ref=ref).segments
    return seg.phones


def ayyuha_context(ph):
    """Locate the unique 'ayyu-ha' run: geminated yeh + damma + heh + fatha."""
    for i in range(len(ph) - 3):
        if (ph[i].base is Base.YEH and ph[i].geminated
                and ph[i + 1].base is Base.DAMMA
                and ph[i + 2].base is Base.HEH
                and ph[i + 3].base is Base.FATHA):
            return ph[i + 4] if i + 4 < len(ph) else None
    return None


def test_ayyuha_43_49_wasl_into_shamsi_article():
    nxt = ayyuha_context(phones(43, 49))
    assert nxt is not None and nxt.base is Base.SEEN and nxt.geminated


def test_ayyuha_55_31_wasl_into_shamsi_article():
    nxt = ayyuha_context(phones(55, 31))
    assert nxt is not None and nxt.base is Base.THEH and nxt.geminated


def test_ayyuha_24_31_wasl_into_qamari_article():
    nxt = ayyuha_context(phones(24, 31))
    assert nxt is not None and nxt.base is Base.LAM  # al-mu'minun: lam kept


def test_no_alif_after_ayyuha_haa():
    # the rasm-dropped alif must never surface in wasl for any of the three
    for s, a in ((43, 49), (24, 31), (55, 31)):
        ph = phones(s, a)
        for i in range(len(ph) - 3):
            if (ph[i].base is Base.YEH and ph[i].geminated
                    and ph[i + 1].base is Base.DAMMA
                    and ph[i + 2].base is Base.HEH):
                assert ph[i + 3].base is not Base.ALEF_MADD, (s, a)
