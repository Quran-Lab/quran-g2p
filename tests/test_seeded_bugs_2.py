"""Seeded-bug drill, round 2: +18 mutants (A6 criterion 6, target >=25).

Same discipline as round 1: each mutant simulates a distinct failure class
(mostly by transforming a phase's correct output into the buggy stream, so
the drill measures DETECTOR sensitivity); every mutant must be killed.
"""
from dataclasses import replace

import quran_g2p.phonemize as PZ
import quran_g2p.tokenlayer as TL
from quran_g2p.ir import Base
from quran_g2p.phonemize import phonemize
from quran_g2p.textbank import AyahRef, TextBank
from quran_g2p.tokenlayer import phones_to_tokens

TB = TextBank.load("tanzil")


def phones_of(s, a):
    ref = AyahRef(s, a)
    (seg,) = phonemize(TB.ayah(ref), edition="tanzil", ref=ref).segments
    return seg.phones


# --- detectors ------------------------------------------------------------

def detect_ghunna_axis_token():
    # 2:7 tanween+waw naqis target must carry the '~' marker
    assert "و~َ" in [t.text for t in phones_to_tokens(phones_of(2, 7))]


def detect_kamil_target_geminated():
    # 2:61 لَن نَّصْبِرَ: kamil noon->noon, target geminated with ghunna
    ph = phones_of(2, 61)
    assert any(p.base is Base.NOON and p.geminated and p.ghunna is not None
               for p in ph)


def detect_noon_wiqaya():
    # 2:180 khayran-i-l-wasiyya: tanween meets wasl -> noon al-wiqaya
    # + kasra, then the qamari article lam: [NOON, KASRA, LAM, WAW]
    ph = phones_of(2, 180)
    seq = [p.base for p in ph]
    want = [Base.NOON, Base.KASRA, Base.LAM, Base.WAW]
    assert any(seq[i:i + 4] == want for i in range(len(seq) - 3))


def detect_2_72_no_seat_madd():
    # fa-ddaara'tum: plain fatha on the reh, NO madd before the hamza
    ph = phones_of(2, 72)
    for i, p in enumerate(ph):
        if p.base is Base.HAMZA and i >= 2 and ph[i - 2].base is Base.REH:
            assert ph[i - 1].base is Base.FATHA and ph[i - 1].kind == "vowel"
            return
    raise AssertionError("2:72 reh+hamza context not found")


def detect_ain_leen_spec():
    # 19:1 'ayn: leen madd allowed {4,6}
    ph = phones_of(19, 1)
    assert any(p.length is not None
               and p.length.allowed == frozenset({4, 6}) for p in ph)


def detect_nudhur_tarqeeq():
    # 54:16 ayah-final nudhur at waqf: reh muraqqaq
    ph = phones_of(54, 16)
    reh = [p for p in ph if p.base is Base.REH][-1]
    assert reh.tafkheem == "moraqaq"


def detect_non_jalala_lam_raqiq():
    # 2:116 (contains a jalala AND ordinary geminated lams): every
    # geminated lam WITHOUT R212 provenance stays muraqqaq
    ph = phones_of(2, 116)
    others = [p for p in ph if p.base is Base.LAM and p.geminated
              and not any("R212" in a.rule_id for a in p.provenance)]
    assert others and all(p.tafkheem == "moraqaq" for p in others)


def detect_naqis_tah_survives():
    # 5:28 basaTta: TAH retained as its own phone, no qalqalah, TEH follows
    ph = phones_of(5, 28)
    for i, p in enumerate(ph):
        if (p.base is Base.TAH and i + 1 < len(ph)
                and ph[i + 1].base is Base.TEH):
            assert p.qalqalah is None
            return
    raise AssertionError("naqis-tah context missing in 5:28")


def detect_mukhfah_tafkheem_follows_trigger():
    # 15:26 min Salsal: the noon_mukhfah before SAD is mofakham
    ph = phones_of(15, 26)
    for i, p in enumerate(ph):
        if (p.base is Base.NOON_MUKHFAH and i + 1 < len(ph)
                and ph[i + 1].base is Base.SAD):
            assert p.tafkheem == "mofakham"
            return
    raise AssertionError("mukhfah-before-sad missing in 15:26")


def detect_lazim_in_dallin():
    # 1:7 aD-Daalleen: lazim fixed {6}
    ph = phones_of(1, 7)
    assert any(p.length is not None and p.length.allowed == frozenset({6})
               and p.length.kind == "fixed" for p in ph)


def detect_wasl_elision():
    # 1:2 rabbi l-'aalameen: no hamza phone at the article junction
    ph = phones_of(1, 2)
    for i, p in enumerate(ph):
        if (p.base is Base.HAMZA and i >= 1 and ph[i - 1].base is Base.KASRA
                and i + 1 < len(ph) and ph[i + 1].base is Base.LAM):
            raise AssertionError("article hamza survived wasl")


def detect_marbuta_pausal_heh():
    # 101:1 al-qaari'atu at waqf -> haa sakin
    ph = phones_of(101, 1)
    assert ph[-1].base is Base.HEH and ph[-1].kind == "consonant"


def detect_iwad_alif():
    # 78:16 alfaafa: waqf on tanween-fath -> 'iwad alif {2}, noon gone
    ph = phones_of(78, 16)
    assert ph[-1].base is Base.ALEF_MADD and ph[-1].length.canonical == 2
    assert not any(p.base is Base.NOON for p in ph[-3:])


def detect_ism_noun_kasra():
    w = next(w for w in TB.ayah(AyahRef(61, 6)).split(" ")
             if w.startswith("ٱس"))
    (seg,) = phonemize(w, edition="tanzil").segments
    ph = seg.phones
    assert ph[0].base is Base.HAMZA and ph[1].base is Base.KASRA


def detect_unzur_damm():
    w = next(w for w in TB.ayah(AyahRef(4, 50)).split(" ")
             if w.startswith("ٱن"))
    (seg,) = phonemize(w, edition="tanzil").segments
    assert (seg.phones[0].base is Base.HAMZA
            and seg.phones[1].base is Base.DAMMA)


def detect_sakt_attr():
    ph = phones_of(75, 27)
    assert any(p.sakt_after for p in ph)


def detect_no_len_tag_on_gem_yeh():
    # leen ':LEN' must never appear on a geminated yeh (iyyaka 1:5)
    toks = [t.text for t in phones_to_tokens(phones_of(1, 5))]
    assert not any(t.startswith("يّ") and ":" in t for t in toks)


def detect_qalqalah_kubra_final():
    # 113:1 al-falaq at waqf: qaf sakin with qalqalah
    ph = phones_of(113, 1)
    assert ph[-1].base is Base.QAF and ph[-1].qalqalah is not None


DET2 = [v for k, v in sorted(globals().items()) if k.startswith("detect_")]


def kills():
    out = []
    for d in DET2:
        try:
            d()
        except Exception:
            out.append(d.__name__)
    return out


def test_all_detectors_pass_unmutated():
    assert kills() == []


# --- mutants (transform correct phase output into the buggy stream) -------

def _post(monkeypatch, fname, transform):
    orig = getattr(PZ, fname)

    def patched(*args, **kw):
        return transform(orig(*args, **kw))
    monkeypatch.setattr(PZ, fname, patched)


def test_mutant_ghunna_axis_dropped(monkeypatch):
    orig = TL.phones_to_tokens

    def patched(phones):
        return [TL.Token(t.text.replace("~", "")) for t in orig(phones)]
    monkeypatch.setattr(TL, "phones_to_tokens", patched)
    monkeypatch.setitem(globals(), "phones_to_tokens", patched)
    assert "detect_ghunna_axis_token" in kills()


def test_mutant_kamil_ungeminated(monkeypatch):
    _post(monkeypatch, "_p9_ghunna", lambda ph: [
        replace(p, geminated=False)
        if p.base is Base.NOON and p.geminated and p.ghunna is not None
        else p for p in ph])
    assert "detect_kamil_target_geminated" in kills()


def test_mutant_noon_wiqaya_dropped(monkeypatch):
    def drop(ph):
        out = []
        i = 0
        while i < len(ph):
            p = ph[i]
            seq = [q.base for q in ph[i:i + 4]]
            if seq == [Base.NOON, Base.KASRA, Base.LAM, Base.WAW]:
                i += 2  # swallow the wiqaya noon and its kasra
                continue
            out.append(p)
            i += 1
        return out
    _post(monkeypatch, "_emit", drop)
    assert "detect_noon_wiqaya" in kills()


def test_mutant_seat_dagger_regression(monkeypatch):
    def add_madd(ph):
        out = []
        for i, p in enumerate(ph):
            out.append(p)
            if (p.kind == "vowel" and p.base is Base.FATHA and i >= 1
                    and ph[i - 1].base is Base.REH and i + 1 < len(ph)
                    and ph[i + 1].base is Base.HAMZA):
                out.append(replace(ph[i - 1], base=Base.ALEF_MADD,
                                   kind="madd", length=PZ._TABEEI))
        return out
    _post(monkeypatch, "_p10_madd", add_madd)
    assert "detect_2_72_no_seat_madd" in kills()


def test_mutant_ain_leen_fixed(monkeypatch):
    _post(monkeypatch, "_p10_madd", lambda ph: [
        replace(p, length=PZ._TABEEI)
        if p.length is not None and p.length.allowed == frozenset({4, 6})
        else p for p in ph])
    assert "detect_ain_leen_spec" in kills()


def test_mutant_nudhur_tafkheem(monkeypatch):
    _post(monkeypatch, "_p12b_waqf_ra_khilaf", lambda ph: [
        replace(p, tafkheem="mofakham")
        if p.base is Base.REH else p for p in ph])
    assert "detect_nudhur_tarqeeq" in kills()


def test_mutant_jalala_overbroad(monkeypatch):
    _post(monkeypatch, "_p12b_waqf_ra_khilaf", lambda ph: [
        replace(p, tafkheem="mofakham")
        if p.base is Base.LAM and p.geminated else p for p in ph])
    assert "detect_non_jalala_lam_raqiq" in kills()


def test_mutant_naqis_tah_deleted(monkeypatch):
    _post(monkeypatch, "_p8_mutamathilayn", lambda ph: [
        p for i, p in enumerate(ph)
        if not (p.base is Base.TAH and i + 1 < len(ph)
                and ph[i + 1].base is Base.TEH)])
    assert "detect_naqis_tah_survives" in kills()


def test_mutant_qalqalah_on_naqis_tah(monkeypatch):
    _post(monkeypatch, "_p11_qalqalah", lambda ph: [
        replace(p, qalqalah="sughra")
        if (p.base is Base.TAH and i + 1 < len(ph)
            and ph[i + 1].base is Base.TEH)
        else p for i, p in enumerate(ph)])
    assert "detect_naqis_tah_survives" in kills()


def test_mutant_mukhfah_always_raqiq(monkeypatch):
    _post(monkeypatch, "_p12_tafkheem", lambda ph: [
        replace(p, tafkheem="moraqaq")
        if p.base is Base.NOON_MUKHFAH else p for p in ph])
    assert "detect_mukhfah_tafkheem_follows_trigger" in kills()


def test_mutant_lazim_demoted(monkeypatch):
    _post(monkeypatch, "_p10_madd", lambda ph: [
        replace(p, length=PZ._free(frozenset({4, 5}), 4,
                                   frozenset({2, 3, 4, 5, 6})))
        if p.length is not None and p.length.allowed == frozenset({6})
        else p for p in ph])
    assert "detect_lazim_in_dallin" in kills()


def test_mutant_wasl_hamza_survives(monkeypatch):
    def add_hamza(ph):
        out = []
        for i, p in enumerate(ph):
            out.append(p)
            if (p.base is Base.KASRA and i + 1 < len(ph)
                    and ph[i + 1].base is Base.LAM
                    and p.word_index != ph[i + 1].word_index):
                out.append(replace(ph[i + 1], base=Base.HAMZA,
                                   kind="consonant", geminated=False))
        return out
    _post(monkeypatch, "_emit", add_hamza)
    assert "detect_wasl_elision" in kills()


def test_mutant_marbuta_stays_teh(monkeypatch):
    def teh(ph):
        if ph and ph[-1].base is Base.HEH:
            return ph[:-1] + [replace(ph[-1], base=Base.TEH)]
        return ph
    _post(monkeypatch, "_emit", teh)
    assert "detect_marbuta_pausal_heh" in kills()


def test_mutant_iwad_keeps_noon(monkeypatch):
    def keep_noon(ph):
        if ph and ph[-1].base is Base.ALEF_MADD:
            return ph[:-1] + [replace(ph[-1], base=Base.NOON,
                                      kind="consonant", length=None)]
        return ph
    _post(monkeypatch, "_emit", keep_noon)
    assert "detect_iwad_alif" in kills()


def test_mutant_noun_list_dropped(monkeypatch):
    def flip_ism(ph):
        if (len(ph) >= 2 and ph[0].base is Base.HAMZA
                and ph[1].base is Base.KASRA
                and len(ph) >= 3 and ph[2].base is Base.SEEN):
            return [ph[0], replace(ph[1], base=Base.DAMMA)] + ph[2:]
        return ph
    _post(monkeypatch, "_emit", flip_ism)
    assert "detect_ism_noun_kasra" in kills()


def test_mutant_verb_rule_always_kasra(monkeypatch):
    def flip(ph):
        if (len(ph) >= 2 and ph[0].base is Base.HAMZA
                and ph[1].base is Base.DAMMA):
            return [ph[0], replace(ph[1], base=Base.KASRA)] + ph[2:]
        return ph
    _post(monkeypatch, "_emit", flip)
    assert "detect_unzur_damm" in kills()


def test_mutant_sakt_dropped(monkeypatch):
    _post(monkeypatch, "_p13_oneoffs", lambda ph: [
        replace(p, sakt_after=False) if p.sakt_after else p for p in ph])
    assert "detect_sakt_attr" in kills()


def test_mutant_len_tag_on_gem(monkeypatch):
    orig = TL.phones_to_tokens

    def patched(phones):
        return [TL.Token(t.text + ":2")
                if t.text.startswith("يّ") and ":" not in t.text else t
                for t in orig(phones)]
    monkeypatch.setattr(TL, "phones_to_tokens", patched)
    monkeypatch.setitem(globals(), "phones_to_tokens", patched)
    assert "detect_no_len_tag_on_gem_yeh" in kills()


def test_mutant_kubra_qalqalah_dropped(monkeypatch):
    _post(monkeypatch, "_p11_qalqalah", lambda ph: (
        ph[:-1] + [replace(ph[-1], qalqalah=None)]
        if ph and ph[-1].qalqalah is not None else ph))
    assert "detect_qalqalah_kubra_final" in kills()
