"""The seven alifs (thabita waqfan, mahdhufa waslan) — sourced and frozen.

Shatibiyya «وحق صحاب قصر وصل الظنون والرسول السبيلا وهو في الوقف في حلا»
(Siraj al-Qari 1:325-326); al-Taysir 1:177-178, 1:217-218; al-Nashr
2:347-348 (mushaf ijma' on the rasm); Hujjat al-Qiraat 1:572-574 (ru'us
al-ayat tawjeeh, alif al-itlaq like qawafi); al-Hujja 5:144-146 (lakinna);
Jamal al-Qurra 1:747-748 (ana: the alif guards the haraka at waqf);
al-Saba 1:664-665, Jami' al-Bayan 4:1678-1679 (qawarira first-vs-second).

The pinned rasm carries the whole system: U+06E0 (open rectangular zero,
x66 = ana x61 + lakinna + al-zununa + al-rasula + al-sabila + qawarira-1)
= dropped in wasl, realized at waqf; U+06DF (round zero) = never realized
- and the dabt prints U+06DF on salasila 76:4, selecting the HADHF wajh
of the Shatibiyya's two waqf wajhs (taqdim disputed among ada' scholars:
al-Dabba'/Bassa hadhf vs al-Marsafi ithbat - Hidayat al-Qari 2:526,
al-'Amid 1:160-161); the ithbat wajh is P2-full variant territory.
"""
from quran_g2p.ir import Base
from quran_g2p.phonemize import phonemize
from quran_g2p.textbank import AyahRef, TextBank

TB = TextBank.load("tanzil")


def phones(s, a):
    ref = AyahRef(s, a)
    (seg,) = phonemize(TB.ayah(ref), edition="tanzil", ref=ref).segments
    return seg.phones


def has_run(ph, seq):
    vals = [p.base for p in ph]
    return any(vals[i:i + len(seq)] == seq
               for i in range(len(vals) - len(seq) + 1))


def test_ayah_final_ithbat_alif_tabeei():
    # 33:10/66/67 + 76:15: the alif is REALIZED at waqf, plain tabee'i {2}
    for s, a in ((33, 10), (33, 66), (33, 67), (76, 15)):
        ph = phones(s, a)
        assert ph[-1].base is Base.ALEF_MADD, (s, a)
        assert ph[-1].length.canonical == 2, (s, a)
        assert ph[-2].base is Base.FATHA, (s, a)


def test_ana_wasl_drops_alif():
    # 2:258 أَنَا۠ أُحْىِۦ: noon's fatha flows straight to the next hamza
    ph = phones(2, 258)
    assert has_run(ph, [Base.HAMZA, Base.FATHA, Base.NOON, Base.FATHA,
                        Base.HAMZA, Base.DAMMA])


def test_lakinna_18_38_wasl_drops_alif():
    # لَّٰكِنَّا۠ هُوَ: kaf-kasra-noon-fatha then heh directly
    ph = phones(18, 38)
    assert has_run(ph, [Base.KAF, Base.KASRA, Base.NOON, Base.FATHA,
                        Base.HEH, Base.DAMMA])


def test_salasila_76_4_wasl_no_alif_no_tanween():
    # سَلَٰسِلَا۟ وَأَغْلَٰلًا: lam-fatha then waw directly (U+06DF hadhf)
    ph = phones(76, 4)
    assert has_run(ph, [Base.SEEN, Base.KASRA, Base.LAM, Base.FATHA,
                        Base.WAW, Base.FATHA])


def test_qawarira_76_16_never_alif():
    # the second qawarira: reh-fatha then meem of من (no alif, no tanween)
    ph = phones(76, 16)
    assert has_run(ph, [Base.REH, Base.FATHA, Base.MEEM, Base.KASRA])


def test_aataani_27_36_wasl_yaa_maftuha():
    # ءَاتَىٰنِۦَ ٱللَّهُ: zawaid yaa present and FATHTED in wasl, into jalala
    ph = phones(27, 36)
    assert has_run(ph, [Base.NOON, Base.KASRA, Base.YEH, Base.FATHA,
                        Base.LAM, Base.FATHA])
