"""Post-reference classical upgrades: 5-rank tafkheem, ghunna duration
prescriptions, waqf-ra khilaf knobs, badal provenance (SPEC-210/170/180).
"""
from quran_g2p.config import HafsConfig
from quran_g2p.ir import Base
from quran_g2p.phonemize import phonemize
from quran_g2p.textbank import AyahRef, TextBank

TB = TextBank.load("tanzil")


def phones_of(s, a, config=None):
    ref = AyahRef(s, a)
    (seg,) = phonemize(TB.ayah(ref), edition="tanzil", ref=ref,
                       config=config or HafsConfig()).segments
    return seg.phones


def test_tafkheem_ranks_follow_maraatib():
    # 1:6 ٱلصِّرَٰطَ: sad+kasra rank 5; the mofakham REH carries fath+alif
    # (رَٰ) = rank 1; tah has plain fath = rank 2.
    ph = phones_of(1, 6)
    sad = next(p for p in ph if p.base is Base.SAD)
    assert sad.tafkheem_rank == 5
    reh = next(p for p in ph if p.base is Base.REH and p.tafkheem == "mofakham")
    assert reh.tafkheem_rank == 1
    tah = next(p for p in ph if p.base is Base.TAH)
    assert tah.tafkheem_rank == 2
    # 110:1 نَصْرُ: sad sakin -> rank 4
    ph = phones_of(110, 1)
    sad = next(p for p in ph if p.base is Base.SAD)
    assert sad.tafkheem_rank == 4
    # muraqqaq phones carry no rank
    for p in ph:
        if p.tafkheem == "moraqaq":
            assert p.tafkheem_rank is None


def test_vowels_inherit_rank():
    # the fatha and dagger-alif after the rank-1 reh of ٱلصِّرَٰطَ inherit rank 1
    ph = phones_of(1, 6)
    i = next(i for i, p in enumerate(ph)
             if p.base is Base.REH and p.tafkheem == "mofakham")
    assert ph[i + 1].kind == "vowel" and ph[i + 1].tafkheem_rank == 1
    assert ph[i + 2].kind == "madd" and ph[i + 2].tafkheem_rank == 1


def test_ghunna_carriers_carry_duration_prescription():
    ph = phones_of(103, 2)  # إِنَّ + ٱلْإِنسَٰنَ
    gem_noon = next(p for p in ph if p.base is Base.NOON and p.geminated)
    assert gem_noon.length is not None
    assert gem_noon.length.canonical == 2
    assert gem_noon.length.scoring == frozenset({1, 2, 3})
    mukhfah = next(p for p in ph if p.base is Base.NOON_MUKHFAH)
    assert mukhfah.length is not None and mukhfah.length.canonical == 2


def test_ghunna_length_stays_off_token_axis():
    from quran_g2p.tokenlayer import phones_to_tokens
    ph = phones_of(103, 2)
    ts = [t.text for t in phones_to_tokens(ph)]
    assert not any(t.startswith("نّ") and ":" in t for t in ts)


def test_waqf_ra_khilaf_defaults_and_flip():
    # 54:16 وَنُذُرِ -> TARQEEQ muqaddam (Hidayat al-Qari 1:132-133: ten of
    # the eleven two-wajh waqf raa'at are tarqeeq-first; the deleted yaa of
    # نُذُرِي) — default False
    ph = phones_of(54, 16)
    assert ph[-1].base is Base.REH and ph[-1].tafkheem == "moraqaq"
    ph = phones_of(54, 16, HafsConfig(nudhur_waqf_tafkheem=True))
    assert ph[-1].tafkheem == "mofakham"
    # 89:4 يَسْرِ -> tarqeeq awlaa (al-Nashr 2:110-111), default False
    ph = phones_of(89, 4)
    assert ph[-1].base is Base.REH and ph[-1].tafkheem == "moraqaq"
    ph = phones_of(89, 4, HafsConfig(yasr_waqf_tafkheem=True))
    assert ph[-1].tafkheem == "mofakham"


def test_firq_wasl_tarqeeq_default_and_flip():
    # 26:63 فِرْقٍ in wasl: maksur isti'la weakens — tarqeeq default
    # (al-Dani's wajhan jayyidan; tarqeeq = the later tarjih)
    ph = phones_of(26, 63)
    rehs = [p for p in ph if p.base is Base.REH]
    sakin_rehs = [p for i, p in enumerate(ph) if p.base is Base.REH
                  and (i + 1 >= len(ph) or ph[i + 1].kind != "vowel")]
    assert any(p.tafkheem == "moraqaq" for p in sakin_rehs)
    ph = phones_of(26, 63, HafsConfig(firq_wasl_tafkheem=True))
    sakin_rehs = [p for i, p in enumerate(ph) if p.base is Base.REH
                  and (i + 1 >= len(ph) or ph[i + 1].kind != "vowel")]
    assert any(p.tafkheem == "mofakham" for p in sakin_rehs)


def test_badal_provenance():
    # 2:4 ...بِٱلْءَاخِرَةِ? use 106:1-2 إِيلَٰفِ: hamza+kasra+yaa-madd = badal
    ph = phones_of(106, 1)
    badal = [p for p in ph if any(a.rule_id == "R181_BADAL" for a in p.provenance)]
    assert badal and all(p.length.allowed == frozenset({2}) for p in badal)


def test_daaf_30_54_wajhan():
    # default: fath (the riwaya, muqaddam); knob: damm (Hafs' ikhtiyar)
    ph = phones_of(30, 54)
    dads = [i for i, p in enumerate(ph) if p.base is Base.DAD]
    fath_dads = [i for i in dads if ph[i + 1].base is Base.FATHA]
    assert len(fath_dads) >= 3
    ph = phones_of(30, 54, HafsConfig(daaf_30_54_damm=True))
    dads = [i for i, p in enumerate(ph) if p.base is Base.DAD]
    damm_dads = [i for i in dads if ph[i + 1].base is Base.DAMMA]
    assert len(damm_dads) >= 3


def test_istifham_tasheel_wajh_all_six_sites():
    # default = ibdal (lazim 6, muqaddam); knob = tasheel (musahhala, no madd)
    sites = [(6, 143), (6, 144), (10, 51), (10, 59), (10, 91), (27, 59)]
    for s, a in sites:
        ph = phones_of(s, a)
        assert any(p.kind == "madd" and p.length
                   and p.length.allowed == frozenset({6}) for p in ph), (s, a)
        ph = phones_of(s, a, HafsConfig(istifham_tasheel=True))
        assert any(p.base is Base.HAMZA_MUSAHHALA for p in ph), (s, a)


def test_sifat_inhiraf_and_idhlaq_complete():
    # the Jazariyya's full seventeen: inhiraf = lam+reh, idhlaq = فر من لب
    from quran_g2p.ir import Base, Phone
    from quran_g2p.sifat import sifat_of

    def mk(base):
        return Phone(base=base, kind="consonant", geminated=False,
                     length=None, ghunna=None, qalqalah=None,
                     tafkheem="moraqaq", sakt_after=False,
                     pausal_role=None, provenance=(), src_span=(0, 0),
                     word_index=0)

    assert sifat_of(mk(Base.LAM))["inhiraf"] == "monharif"
    assert sifat_of(mk(Base.REH))["inhiraf"] == "monharif"
    assert sifat_of(mk(Base.SEEN))["inhiraf"] == "not_monharif"
    for b in (Base.FEH, Base.REH, Base.MEEM, Base.NOON, Base.LAM, Base.BEH):
        assert sifat_of(mk(b))["idhlaq"] == "mothlaq", b
    assert sifat_of(mk(Base.QAF))["idhlaq"] == "mosmat"
