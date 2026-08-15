"""P14 — sifat projection (SPEC-214b): static table read off the IR.

sifat_of(phone) returns the 10-sifa vector; dynamic sifat (tafkheem, qalqalah,
ghunna) come from the phone's own attributes — never re-derived by regex.
"""
from quran_g2p.ir import Base
from quran_g2p.phonemize import phonemize
from quran_g2p.sifat import sifat_of
from quran_g2p.textbank import AyahRef, TextBank


def test_static_table_examples():
    from quran_g2p.ir import Phone

    def mk(base, **kw):
        d = dict(base=base, kind="consonant", geminated=False, length=None,
                 ghunna=None, qalqalah=None, tafkheem="moraqaq",
                 sakt_after=False, pausal_role=None, provenance=(),
                 src_span=(0, 1), word_index=0)
        d.update(kw)
        return Phone(**d)

    s = sifat_of(mk(Base.SAD))
    assert s["safeer"] == "safeer" and s["hams_or_jahr"] == "hams"
    assert s["itbaq"] == "motbaq"
    s = sifat_of(mk(Base.REH))
    assert s["tikraar"] == "mokarar" and s["hams_or_jahr"] == "jahr"
    s = sifat_of(mk(Base.SHEEN))
    assert s["tafashie"] == "motafashie"
    s = sifat_of(mk(Base.DAD))
    assert s["istitala"] == "mostateel" and s["shidda_or_rakhawa"] == "rikhw"
    s = sifat_of(mk(Base.QAF, qalqalah="sughra"))
    assert s["qalqla"] == "moqalqal" and s["shidda_or_rakhawa"] == "shadeed"
    s = sifat_of(mk(Base.NOON, ghunna="mushaddadah", geminated=True))
    assert s["ghonna"] == "maghnoon"
    s = sifat_of(mk(Base.TAH, tafkheem="mofakham"))
    assert s["tafkheem_or_taqeeq"] == "mofakham"


def test_projection_over_real_ayah():
    tb = TextBank.load("tanzil")
    (seg,) = phonemize(tb.ayah(AyahRef(1, 1)), edition="tanzil",
                       ref=AyahRef(1, 1)).segments
    vecs = [sifat_of(p) for p in seg.phones if p.kind == "consonant"]
    assert all(set(v) == {
        "hams_or_jahr", "shidda_or_rakhawa", "tafkheem_or_taqeeq", "itbaq",
        "safeer", "qalqla", "tikraar", "tafashie", "istitala", "ghonna",
        "inhiraf", "idhlaq",
    } for v in vecs)
