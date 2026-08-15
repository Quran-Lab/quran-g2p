"""Token layer (Part B1): letter-group tokens with length tags.

TOKEN := BASE (shadda?) (tafkheem '^'?) (haraka?) (residual?) (':' LEN)?
One token = one acoustic dwell. Expected tokens are BUILT from codepoints
(combining-mark order is part of the contract; hand-typed Arabic is banned).
Round-trip (parse∘format = id) is the contract.
"""
import pytest

from quran_g2p import codepoints as cp
from quran_g2p.phonemize import phonemize
from quran_g2p.textbank import AyahRef, TextBank
from quran_g2p.tokenlayer import parse_token, phones_to_tokens

SHADDA = cp.SHADDA
QLQ = "ڇ"  # ڇ residual (oracle-compatible qalqalah char)


def toks(ref, edition="tanzil"):
    tb = TextBank.load(edition)
    (seg,) = phonemize(tb.ayah(ref), edition=edition, ref=ref).segments
    return phones_to_tokens(seg.phones)


def texts(ref):
    return [t.text for t in toks(ref)]


def test_1_1_first_word_tokens():
    assert texts(AyahRef(1, 1))[:3] == [
        cp.BEH + cp.KASRA, cp.SEEN, cp.MEEM + cp.KASRA]


def test_madd_tokens_carry_length():
    ts = texts(AyahRef(1, 1))
    madds = [t for t in ts if ":" in t]
    assert madds
    assert madds[-1] == cp.SMALL_YEH + ":4"  # aared canonical 4 on the ۦ


def test_geminated_and_jalala():
    # 112:1 jalala lam mofakham after damma -> lam+shadda+^+fatha
    assert cp.LAM + SHADDA + "^" + cp.FATHA in texts(AyahRef(112, 1))
    assert "ا:2" in texts(AyahRef(112, 1))  # jalala alif ا:2
    # 1:1 jalala lam moraqaq after kasra -> plain lam+shadda+fatha
    assert cp.LAM + SHADDA + cp.FATHA in texts(AyahRef(1, 1))


def test_mukhfah_tokens():
    assert any(t.startswith("ں") for t in texts(AyahRef(107, 5)))


def test_qalqalah_residual():
    ts = texts(AyahRef(112, 3))
    assert ts[-1] == cp.DAL + QLQ


def test_roundtrip_parse_format():
    for ref in (AyahRef(1, 1), AyahRef(2, 255), AyahRef(112, 1), AyahRef(2, 1)):
        for t in toks(ref):
            assert parse_token(t.text).text == t.text


def test_tafkheem_marker_on_reh_and_lam_only():
    for t in toks(AyahRef(1, 1)):
        if "^" in t.text:
            assert t.text[0] in (cp.REH, cp.LAM)
    assert any(t.text.startswith(cp.REH + SHADDA + "^")
               for t in toks(AyahRef(1, 1)))
