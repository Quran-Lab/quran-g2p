"""P1 orthographic decode goldens.

Expected seg streams are hand-derived phonological judgments (documented in
SPEC-002); the input codepoints are facts of the pinned texts. 1:1 is the
first cross-edition equality case: its editions differ only in the sukun
codepoint, so the decoded streams must be identical.
"""
import pytest

from quran_g2p import codepoints as cp
from quran_g2p.decode import decode_text
from quran_g2p.ir import Base
from quran_g2p.ortho import ConsSeg, MaddSeg, MaddSource, SukunKind, TanweenMode, VQ
from quran_g2p.textbank import AyahRef, TextBank


def brief(seg):
    """Compact structural view used by the goldens."""
    if isinstance(seg, MaddSeg):
        return ("madd", seg.quality.value, seg.source.value, seg.word_index)
    vowel = seg.vowel.value if seg.vowel else None
    tan = (seg.tanween.quality.value, seg.tanween.mode.value) if seg.tanween else None
    suk = seg.sukun.value if seg.sukun else None
    return (seg.letter.value, vowel, tan, suk, seg.shadda, seg.word_index)


GOLDEN_1_1 = [
    # بِسْمِ
    ("beh", "i", None, None, False, 0),
    ("seen", None, None, "marked", False, 0),
    ("meem", "i", None, None, False, 0),
    # ٱللَّهِ — first lam bare (idgham into lam of Allah), second geminated
    ("hamzat_wasl", None, None, None, False, 1),
    ("lam", None, None, "bare", False, 1),
    ("lam", "a", None, None, True, 1),
    ("heh", "i", None, None, False, 1),
    # ٱلرَّحْمَٰنِ — lam shamsiyya bare, reh geminated, dagger alif on meem
    ("hamzat_wasl", None, None, None, False, 2),
    ("lam", None, None, "bare", False, 2),
    ("reh", "a", None, None, True, 2),
    ("hah", None, None, "marked", False, 2),
    ("meem", "a", None, None, False, 2),
    ("madd", "a", "dagger_alef", 2),
    ("noon", "i", None, None, False, 2),
    # ٱلرَّحِيمِ — bare yeh after kasra = madd i
    ("hamzat_wasl", None, None, None, False, 3),
    ("lam", None, None, "bare", False, 3),
    ("reh", "a", None, None, True, 3),
    ("hah", "i", None, None, False, 3),
    ("madd", "i", "bare_yeh", 3),
    ("meem", "i", None, None, False, 3),
]


@pytest.mark.parametrize("edition", ["tanzil", "kfgqpc"])
def test_golden_1_1(edition):
    tb = TextBank.load(edition)
    res = decode_text(tb.ayah(AyahRef(1, 1)), edition=edition)
    assert [brief(s) for s in res.segs] == GOLDEN_1_1
    assert res.n_words == 4


def test_editions_agree_on_1_1():
    a = decode_text(TextBank.load("tanzil").ayah(AyahRef(1, 1)), edition="tanzil")
    b = decode_text(TextBank.load("kfgqpc").ayah(AyahRef(1, 1)), edition="kfgqpc")
    assert [brief(s) for s in a.segs] == [brief(s) for s in b.segs]


def test_tanween_plain_tanzil_vs_open_kfgqpc():
    # hudan: HEH+DAMMA, DAL+tanween-fath, ALEF MAKSURA (eiwad seat)
    tanzil_word = cp.HEH + cp.DAMMA + cp.DAL + cp.FATHATAN + cp.ALEF_MAKSURA
    kf_word = cp.HEH + cp.DAMMA + cp.DAL + cp.INVERTED_DAMMA + cp.ALEF_MAKSURA
    a = decode_text(tanzil_word, edition="tanzil").segs
    b = decode_text(kf_word, edition="kfgqpc").segs
    assert brief(a[1]) == ("dal", None, ("a", "plain"), None, False, 0)
    assert brief(b[1]) == ("dal", None, ("a", "open"), None, False, 0)
    assert brief(a[2]) == ("madd", "a", "alef_maksura", 0)
    assert brief(b[2]) == brief(a[2])


def test_kfgqpc_open_dammatan_and_kasratan():
    # constructed: BEH+dammatan-open, BEH+kasratan-open
    segs = decode_text(cp.BEH + cp.FATHA_WITH_TWO_DOTS, edition="kfgqpc").segs
    assert brief(segs[0]) == ("beh", None, ("u", "open"), None, False, 0)
    segs = decode_text(cp.BEH + cp.SUBSCRIPT_ALEF, edition="kfgqpc").segs
    assert brief(segs[0]) == ("beh", None, ("i", "open"), None, False, 0)


def test_kfgqpc_silent_letter_uses_plain_sukun_glyph():
    # KFGQPC writes silent letters with U+0652; e.g. a silent waw seat.
    # Constructed: QAF+FATHA, ALEF? no — use WAW with 0652 after damma: silent.
    segs = decode_text(cp.LAM + cp.DAMMA + cp.WAW + cp.SUKUN, edition="kfgqpc").segs
    assert [brief(s) for s in segs] == [("lam", "u", None, None, False, 0)]


def test_tanzil_silent_circle_deletes_letter():
    # أُو۟لَٰٓئِكَ-style: WAW with U+06DF after damma is silent
    segs = decode_text(
        cp.HAMZA + cp.DAMMA + cp.WAW + cp.SMALL_HIGH_ROUNDED_ZERO, edition="tanzil"
    ).segs
    assert [brief(s) for s in segs] == [("hamza", "u", None, None, False, 0)]


def test_bare_waw_after_damma_is_madd_u():
    segs = decode_text(cp.QAF + cp.DAMMA + cp.WAW, edition="tanzil").segs
    assert [brief(s) for s in segs] == [
        ("qaf", "u", None, None, False, 0),
        ("madd", "u", "bare_waw", 0),
    ]


def test_open_sukun_alef_is_waqf_only_madd():
    # أَنَا۠: ALEF + U+06E0 — silent in wasl, alif at waqf (66 sites).
    segs = decode_text(
        cp.NOON + cp.FATHA + cp.ALEF + cp.SMALL_HIGH_UPRIGHT_RECTANGULAR_ZERO,
        edition="tanzil",
    ).segs
    assert len(segs) == 2
    madd = segs[1]
    assert isinstance(madd, MaddSeg) and madd.waqf_only is True
    assert madd.quality == VQ.A


def test_tanzil_maksura_with_vowel_state_is_consonant_yeh():
    # Tanzil writes consonant yaa dotless: شَىْءٍ, هِىَ (SPEC-002 finding 2026-08-15)
    segs = decode_text(cp.HEH + cp.KASRA + cp.ALEF_MAKSURA + cp.FATHA, edition="tanzil").segs
    assert [brief(s) for s in segs] == [
        ("heh", "i", None, None, False, 0),
        ("yeh", "a", None, None, False, 0),
    ]


def test_bare_waw_after_fatha_is_leen_consonant_in_idgham_context():
    # KFGQPC عَصَوا۟ وَّ…: leen waw left bare = assimilated into following waw
    segs = decode_text(cp.SAD + cp.FATHA + cp.WAW, edition="kfgqpc").segs
    assert [brief(s) for s in segs] == [
        ("sad", "a", None, None, False, 0),
        ("waw", None, None, "bare", False, 0),
    ]


def test_seat_letter_before_hamza_carrier_is_silent():
    # KFGQPC تِلۡقَآيِٕ: bare yeh + combining hamza(+kasra) — yeh is a silent seat
    segs = decode_text(
        cp.QAF + cp.FATHA + cp.ALEF + cp.MADDAH_ABOVE + cp.YEH + cp.HAMZA_BELOW + cp.KASRA,
        edition="kfgqpc",
    ).segs
    assert [brief(s) for s in segs] == [
        ("qaf", "a", None, None, False, 0),
        ("madd", "a", "plain_alef", 0),
        ("hamza", "i", None, None, False, 0),
    ]


def test_iqlab_mark_recorded_as_witness():
    # Tanzil: NOON bare + 06E2 on it? The mark rides the noon cluster.
    segs = decode_text(cp.MEEM + cp.KASRA + cp.NOON + cp.SMALL_HIGH_MEEM_ISOLATED_FORM,
                       edition="tanzil").segs
    noon = segs[-1]
    assert isinstance(noon, ConsSeg) and noon.iqlab_mark is True
    assert noon.sukun == SukunKind.BARE


def test_iqlab_tanween_canonicalized_across_editions():
    # Tanzil: MEEM + DAMMATAN + 06E2  |  KFGQPC: MEEM + DAMMA + 06E2
    # Both must decode to tanween (u, iqlab).
    a = decode_text(cp.MEEM + cp.DAMMATAN + cp.SMALL_HIGH_MEEM_ISOLATED_FORM,
                    edition="tanzil").segs[0]
    b = decode_text(cp.MEEM + cp.DAMMA + cp.SMALL_HIGH_MEEM_ISOLATED_FORM,
                    edition="kfgqpc").segs[0]
    for seg in (a, b):
        assert isinstance(seg, ConsSeg)
        assert seg.vowel is None
        assert seg.tanween == (seg.tanween.__class__(VQ.U, TanweenMode.IQLAB))
        assert seg.iqlab_mark is True


def test_kfgqpc_hamza_seat_with_madda_is_hamza_a_plus_madd():
    # KFGQPC بِٱلۡأٓخِرَةِ: hamza-on-alef seat + madda, no fatha, no separate
    # alef — decodes as HAMZA(a) + madd(a) to match Tanzil's ءَا encoding.
    segs = decode_text(cp.ALEF_WITH_HAMZA_ABOVE + cp.MADDAH_ABOVE, edition="kfgqpc").segs
    assert [brief(s) for s in segs] == [
        ("hamza", "a", None, None, False, 0),
        ("madd", "a", "plain_alef", 0),
    ]
