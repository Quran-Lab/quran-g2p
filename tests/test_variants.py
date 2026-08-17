"""Waqf-variant enumeration (plan A2 VariantPolicy; SPEC-123/183/184).

`enumerate_variants` surfaces, per segment, the tagged waqf alternates:
sukun (canonical, always first), rawm and ishmam where the five-sanf
taxonomy permits them, and the transmitted site wajhs (ta'manna
ikhtilas, salasila ithbat, aataani hadhf). Ambiguity is enumerated,
never averaged.
"""
from quran_g2p.ir import Base
from quran_g2p.textbank import AyahRef, TextBank
from quran_g2p.variants import enumerate_variants
from quran_g2p.waqf import WaqfSpec

TB = TextBank.load("tanzil")


def variants_of(s, a, stops=()):
    ref = AyahRef(s, a)
    return enumerate_variants(TB.ayah(ref), edition="tanzil", ref=ref,
                              waqf=WaqfSpec(stops=tuple(stops)))


def modes(vs):
    return [v.mode for v in vs]


def test_damm_final_gets_all_three():
    # 1:5 نَسْتَعِينُ: damm final -> sukun + rawm + ishmam
    (seg_vars,) = variants_of(1, 5)
    assert modes(seg_vars) == ["sukun", "rawm", "ishmam"]


def test_rawm_appends_partial_haraka_and_shortens_aared():
    (seg_vars,) = variants_of(1, 5)
    rawm = next(v for v in seg_vars if v.mode == "rawm")
    assert rawm.phones[-1].base is Base.DAMMA
    assert rawm.phones[-1].pausal_role == "rawm"
    # the 'aared madd reverts to qasr under rawm (SPEC-123)
    aared = [p for p in rawm.phones if p.kind == "madd"
             and p.word_index == rawm.phones[-1].word_index]
    assert aared and aared[-1].length.allowed == frozenset({2})


def test_ishmam_keeps_sukun_phones():
    (seg_vars,) = variants_of(1, 5)
    sukun = seg_vars[0]
    ishmam = next(v for v in seg_vars if v.mode == "ishmam")
    assert ishmam.phones[-1].base is sukun.phones[-1].base
    assert ishmam.phones[-1].pausal_role == "ishmam"


def test_kasr_final_no_ishmam():
    # 1:1 ends ٱلرَّحِيمِ (kasr) -> sukun + rawm only
    (seg_vars,) = variants_of(1, 1)
    assert modes(seg_vars) == ["sukun", "rawm"]


def test_fath_declension_final_sukun_only():
    # 1:2 ends ٱلْعَٰلَمِينَ with FATHA -> no isharah on fath
    (seg_vars,) = variants_of(1, 2)
    assert modes(seg_vars) == ["sukun"]


def test_fath_final_sukun_only():
    # 111:1 وَتَبَّ
    (seg_vars,) = variants_of(111, 1)
    assert modes(seg_vars) == ["sukun"]


def test_marbuta_sukun_only():
    # 101:1 ٱلْقَارِعَةُ: ta-marbuta haa carries no i'rab
    (seg_vars,) = variants_of(101, 1)
    assert modes(seg_vars) == ["sukun"]


def test_haa_sakt_sukun_only():
    # 69:19 كِتَٰبِيَهْ
    (seg_vars,) = variants_of(69, 19)
    assert modes(seg_vars) == ["sukun"]


def test_pronoun_haa_after_yaa_sukun_only():
    # stop on فِيهِۦ 25:69 (silah dropped): tafsil forbids the isharah
    ref = AyahRef(25, 69)
    words = TB.ayah(ref).split(" ")
    k = next(i for i, w in enumerate(words) if "فِي" in w)
    seg_vars = variants_of(25, 69, stops=[k])[0]
    assert modes(seg_vars) == ["sukun"]


def test_tanween_raf_final_keeps_isharah():
    # 2:255? use 112:2 ٱلصَّمَدُ (damm, no tanween) then a tanween case:
    # 112:1 أَحَدٌ: tanween raf' -> the underlying damm keeps rawm/ishmam
    (seg_vars,) = variants_of(112, 1)
    assert modes(seg_vars) == ["sukun", "rawm", "ishmam"]
    rawm = seg_vars[1]
    assert rawm.phones[-1].base is Base.DAMMA
    # and no tanween noon returns in the rawm variant
    assert rawm.phones[-2].base is Base.DAL


def test_rawm_strips_qalqalah():
    # rawm = partial haraka, the letter is not fully sakin -> no qalqalah
    (seg_vars,) = variants_of(112, 1)
    rawm = seg_vars[1]
    assert rawm.phones[-2].qalqalah is None
    sukun = seg_vars[0]
    assert sukun.phones[-1].qalqalah is not None


def test_taamanna_ikhtilas_variant():
    # 12:11 segment carries the transmitted ikhtilas wajh as an alternate
    (seg_vars,) = variants_of(12, 11)
    ikh = next(v for v in seg_vars if "taamanna_ikhtilas" in v.tags)
    bases = [p.base for p in ikh.phones]
    assert Base.DAMMA_MUKHTALASA in bases
    i = bases.index(Base.DAMMA_MUKHTALASA)
    assert bases[i - 1] is Base.NOON and bases[i + 1] is Base.NOON
    assert not ikh.phones[i - 1].geminated


def test_salasila_ithbat_variant_at_stop():
    ref = AyahRef(76, 4)
    seg_vars = variants_of(76, 4, stops=[3])[0]
    alt = next(v for v in seg_vars if "salasila_ithbat" in v.tags)
    assert alt.phones[-1].base is Base.ALEF_MADD


def test_aataani_hadhf_variant_at_stop():
    ref = AyahRef(27, 36)
    words = TB.ayah(ref).split(" ")
    k = next(i for i, w in enumerate(words) if "تَى" in w)
    seg_vars = variants_of(27, 36, stops=[k])[0]
    alt = next(v for v in seg_vars if "aataani_hadhf" in v.tags)
    assert alt.phones[-1].base is Base.NOON


def test_rawm_on_muttasil_drops_the_six():
    # 14:27 ends يَشَآءُ (muttasil, marfoo): pure sukun and ishmam keep
    # {4,5,6}; rawm is wasl-like, so the madd reverts to {4,5} with no 6
    # (ظاهرة المد في الأداء القرآني 1:408-409)
    variants = variants_of(14, 27)[-1]
    by_mode = {}
    for v in variants:
        by_mode.setdefault(v.mode, v)
    def muttasil(v):
        madds = [p for p in v.phones
                 if p.kind == "madd" and p.length is not None
                 and p.length.kind == "free" and 4 in p.length.allowed]
        return madds[-1]
    # same physical phone in every mode: the finder cannot drift
    spans = {muttasil(by_mode[m]).src_span for m in ("sukun", "ishmam", "rawm")}
    assert len(spans) == 1
    assert 6 in muttasil(by_mode["sukun"]).length.allowed
    assert 6 in muttasil(by_mode["ishmam"]).length.allowed
    assert muttasil(by_mode["rawm"]).length.allowed == frozenset({4, 5})
