"""Concat phase (SPEC-005): consecutive ayat joined in wasl.

`phonemize_concat` merges the decoded streams (each ayah decoded with
its own ref so site tables apply) and runs the phase chain once, so
every junction rule fires across ayah boundaries exactly as it does
across words. The three cross-ayah specials are site-handled: the
Anfal->Tawba iqlab, the الم+الله junction (connective FATHA, jalala
mofakham, the meem-name madd keeps its ishba'), عوجا's 'iwad-alif and
sakt surviving wasl (18:1->2), and ماليه izhar-with-sakt (69:28->29).
"""
from quran_g2p.concat import phonemize_concat
from quran_g2p.ir import Base
from quran_g2p.textbank import AyahRef, TextBank

TB = TextBank.load("tanzil")


def concat(*refs):
    items = [(AyahRef(s, a), TB.ayah(AyahRef(s, a))) for s, a in refs]
    return phonemize_concat(items, edition="tanzil")


def bases(ph):
    return [p.base for p in ph]


def find_run(ph, seq, start=0):
    vals = bases(ph)
    for i in range(start, len(vals) - len(seq) + 1):
        if vals[i:i + len(seq)] == seq:
            return i
    return -1


def test_plain_junction_wasl_elision():
    # 2:2 ends ...لِّلْمُتَّقِينَ + 2:3 ٱلَّذِينَ: fatha flows into the
    # article's geminated lam, wasl hamza gone
    (seg,) = concat((2, 2), (2, 3)).segments
    ph = seg.phones
    i = find_run(ph, [Base.QAF, Base.KASRA, Base.YEH_MADD, Base.NOON,
                      Base.FATHA, Base.LAM])
    assert i >= 0
    lam = ph[i + 5]
    assert lam.geminated  # ٱلَّذِينَ's lam


def test_tanween_junction_noon_wiqaya():
    # 112:1 أَحَدٌ + 112:2 ٱللَّهُ: iltiqa -> noon al-wiqaya with kasra,
    # and the jalala goes MURAQQAQ after that kasra
    (seg,) = concat((112, 1), (112, 2)).segments
    ph = seg.phones
    i = find_run(ph, [Base.DAL, Base.DAMMA, Base.NOON, Base.KASRA,
                      Base.LAM])
    assert i >= 0
    lam = ph[i + 4]
    assert lam.geminated and lam.tafkheem == "moraqaq"


def test_anfal_tawba_iqlab():
    # 8:75 ends عَلِيمٌۢ + 9:1 بَرَآءَةٌ: the printed iqlab meem fires
    (seg,) = concat((8, 75), (9, 1)).segments
    ph = seg.phones
    i = find_run(ph, [Base.MEEM_MUKHFAH, Base.BEH])
    assert i >= 0


def test_alif_lam_meem_allah_junction():
    # 3:1 الٓمٓ + 3:2 ٱللَّهُ: the meem takes FATHA (not the general
    # iltiqa kasra), the jalala stays MOFAKHAM, and the meem-name's
    # lazim madd keeps {6}
    (seg,) = concat((3, 1), (3, 2)).segments
    ph = seg.phones
    i = find_run(ph, [Base.MEEM, Base.FATHA, Base.LAM])
    assert i >= 0
    assert ph[i + 2].geminated and ph[i + 2].tafkheem == "mofakham"
    madd_before = [p for p in ph[:i] if p.kind == "madd"][-1]
    assert madd_before.length.allowed == frozenset({6})


def test_maliyah_izhar_with_sakt():
    # 69:28 مَالِيَهْ + 69:29 هَلَكَ: izhar with sakt muqaddam — the two
    # haas do NOT idgham; the first carries sakt_after
    (seg,) = concat((69, 28), (69, 29)).segments
    ph = seg.phones
    i = find_run(ph, [Base.HEH, Base.HEH, Base.FATHA, Base.LAM])
    assert i >= 0
    assert ph[i].sakt_after
    assert not ph[i + 1].geminated


def test_iwaja_sakt_survives_wasl():
    # 18:1 ends عِوَجَا ۜ + 18:2 قَيِّمًا: the 'iwad alif stays even in
    # wasl, carries the sakt, and NO tanween rules fire at the junction
    (seg,) = concat((18, 1), (18, 2)).segments
    ph = seg.phones
    i = find_run(ph, [Base.JEEM, Base.FATHA, Base.ALEF_MADD, Base.QAF])
    assert i >= 0
    assert ph[i + 2].sakt_after
    assert find_run(ph, [Base.NOON_MUKHFAH, Base.QAF]) == -1


def test_word_indices_are_global():
    res = concat((112, 1), (112, 2), (112, 3))
    (seg,) = res.segments
    n1 = len(TB.ayah(AyahRef(112, 1)).split(" "))
    n2 = len(TB.ayah(AyahRef(112, 2)).split(" "))
    n3 = len(TB.ayah(AyahRef(112, 3)).split(" "))
    assert max(p.word_index for p in seg.phones) == n1 + n2 + n3 - 1
