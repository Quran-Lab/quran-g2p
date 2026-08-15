"""P13 one-offs + the dabt-driven P6 refinement (SPEC-131/132/220/221/222).

- 75:27 مَنْ رَاقٍ: MARKED sukun noon = izhar witness; sakt blocks idgham —
  the noon must SURVIVE (and carry sakt_after).
- 83:14 بَلْ رَانَ: lam survives + sakt.
- 11:41 مَجْر۪ىٰهَا: imala — fatha_imala + alef_imala, reh moraqaq.
- 41:44 ءَا۬عْجَمِيٌّ: tasheel — hamza_musahhala replaces the marked seat.
- 12:11 تَأْمَ۫نَّا: ishmam recorded as an attribute event on the noon.
"""
from quran_g2p.ir import Base
from quran_g2p.phonemize import phonemize
from quran_g2p.textbank import AyahRef, TextBank


def phones_of(ref, edition="tanzil"):
    tb = TextBank.load(edition)
    (seg,) = phonemize(tb.ayah(ref), edition=edition, ref=ref).segments
    return seg.phones


def test_75_27_sakt_blocks_idgham_noon_survives():
    ph = phones_of(AyahRef(75, 27))
    # مَنْ رَاقٍ -> m a n(sakt) r a A q i n? (tanween izhar? next 75:28 — at
    # ayah level: raaqin ends the ayah -> tanween dropped? No: raaq-IN is
    # ayah-final -> iskan drops tanween -> q sakin. The noon of man MUST exist.
    seq = [(p.base, p.sakt_after) for p in ph]
    noon_sites = [i for i, (b, _) in enumerate(seq) if b is Base.NOON]
    assert noon_sites, "noon of man was deleted — sakt/izhar violated"
    assert any(s for (b, s) in seq if b is Base.NOON), "sakt_after missing on noon"


def test_83_14_sakt_on_bal():
    ph = phones_of(AyahRef(83, 14))
    lams = [p for p in ph if p.base is Base.LAM and p.sakt_after]
    assert lams, "sakt_after missing on bal's lam"
    # it must be the SAKIN lam of بَلْ (word 1), not one of كَلَّا's lams
    assert all(p.word_index == 1 and not p.geminated for p in lams)


def test_11_41_imala():
    ph = phones_of(AyahRef(11, 41))
    assert any(p.base is Base.FATHA_IMALA for p in ph)
    assert any(p.base is Base.ALEF_IMALA for p in ph)
    i = next(i for i, p in enumerate(ph) if p.base is Base.FATHA_IMALA)
    assert ph[i - 1].base is Base.REH and ph[i - 1].tafkheem == "moraqaq"


def test_41_44_tasheel():
    ph = phones_of(AyahRef(41, 44))
    assert any(p.base is Base.HAMZA_MUSAHHALA for p in ph)


def test_12_11_ishmam_event_recorded():
    ph = phones_of(AyahRef(12, 11))
    noons = [p for p in ph if p.base is Base.NOON and p.geminated]
    assert any(
        any("R220_ISHMAM" == a.rule_id for a in p.provenance) for p in noons
    ), "ishmam event missing on ta'manna's noon"
