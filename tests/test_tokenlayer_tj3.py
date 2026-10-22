"""tj3 (tokenlayer_tj3, artifacts/tokenizer_tj3): one token per sound; the phone path and the tj2 + V_id path agree
(whole-corpus sweep: scratch tool, sampled here); lengths, gemination, rawm, ishmam and markers never reach a token."""
import hashlib
import json
from pathlib import Path

import pytest

from quran_g2p import codepoints as cp
from quran_g2p import tokenlayer_tj3 as T
from quran_g2p.phonemize import phonemize
from quran_g2p.textbank import AyahRef, TextBank
from quran_g2p.tokenlayer import phones_to_tokens
from quran_g2p.variants import enumerate_variants

ROOT = Path(__file__).parents[1]
# V_id (tarteel tajweedformer/vocab.py ID_CLASSES), spelled out so this repo stays standalone
VID = (["<blank>", "|", "lam", "meem", "noon", "hamza", "heh", "waw", "teh", "reh", "yeh", "beh", "kaf", "ain", "feh",
        "qaf", "seen", "dal", "thal", "hah", "jeem", "khah", "sheen", "sad", "dad", "zain", "theh", "tah", "ghain",
        "zah"] + ["alef_madd", "waw_madd", "yeh_madd"] + ["fatha", "kasra", "damma"] + ["<foreign>"])
_MERGE = {"noon_mukhfah": "noon", "meem_mukhfah": "meem", "hamza_musahhala": "hamza", "alef_imala": "alef_madd",
          "fatha_imala": "fatha", "damma_mukhtalasa": "damma"}


def vid_of(phones):
    ids, prev = [], None
    for p in phones:
        if prev is not None and p.word_index != prev:
            ids.append(1)
        ids.append(VID.index(_MERGE.get(p.base.value, p.base.value)))
        prev = p.word_index
    return ids


def both(phones):
    phones = list(phones)
    a = T.phones_to_tj3(phones)
    b, first = T.tj2_to_tj3([t.text for t in phones_to_tokens(phones)], vid_of(phones), VID)
    assert a == b
    return a, first


@pytest.fixture(scope="module")
def tb():
    return TextBank.load("tanzil")


def ayah(tb, s, a):
    ref = AyahRef(s, a)
    return [p for seg in phonemize(tb.ayah(ref), edition="tanzil", ref=ref).segments for p in seg.phones]


def test_vocab_file_and_manifest():
    lines = (ROOT / "artifacts/tokenizer_tj3/tokens.txt").read_text(encoding="utf-8").splitlines()
    assert [ln.rsplit(" ", 1)[0] for ln in lines] == T.TOKENS
    m = json.loads((ROOT / "artifacts/tokenizer_tj3/vocab_manifest.json").read_text(encoding="utf-8"))
    assert m["vocab_sha256"] == hashlib.sha256((ROOT / "artifacts/tokenizer_tj3/tokens.txt").read_bytes()).hexdigest()
    assert m["size"] == 38 and m["blank_id"] == 0 and m["word_id"] == 1


def test_no_length_or_marker_in_any_token():
    for t in T.TOKENS:
        assert ":" not in t and cp.SHADDA not in t and not set(t) & set("^~=")


def test_fatiha_long_vowels_and_boundaries(tb):
    toks, _ = both(ayah(tb, 1, 4))                 # maliki yawmi d-din
    assert toks[:4] == [cp.MEEM, "aa", cp.LAM, "i"]
    assert toks.count(T.WORD) == 2
    assert toks[-2:] == ["ii", cp.NOON]


def test_madd_count_never_changes_tokens(tb):
    phones = ayah(tb, 1, 7)                        # wa la d-dallin: madd lazim 6
    base = T.phones_to_tj3(phones)
    for i, p in enumerate(phones):
        if p.length is not None and p.length.kind == "free":
            for L in p.length.scoring:
                ph = list(phones)
                ph[i] = p.with_realized_len(L)
                assert T.phones_to_tj3(ph) == base


def test_shadda_is_one_token(tb):
    toks, _ = both(ayah(tb, 1, 2))                 # lillahi, rabbi: each geminate is one token
    assert not any(a == b and a in T.CONSONANTS for a, b in zip(toks, toks[1:]))
    assert [cp.REH, "a", cp.BEH, "i"] == toks[toks.index(cp.REH) - 0:toks.index(cp.REH) + 4]


def test_ikhfa_keeps_its_nasal(tb):
    toks, _ = both(ayah(tb, 1, 7))                 # an'amta: izhar (plain noon), no ikhfa here
    assert T.IKHFA not in toks
    toks, _ = both(ayah(tb, 2, 25))                # min tahtiha: ikhfa
    assert T.IKHFA in toks


def test_waqf_variants_rawm_ishmam(tb):
    ref = AyahRef(1, 4)
    for seg in enumerate_variants(tb.ayah(ref), edition="tanzil", ref=ref):
        for v in seg:
            toks, _ = both(v.phones)
            assert all(t in T.INDEX for t in toks)


def test_unit_first_points_into_tokens(tb):
    phones = ayah(tb, 2, 255)
    toks, first = both(phones)
    units = [t.text for t in phones_to_tokens(phones)]
    assert len(first) == len(units)
    for k, u in enumerate(units):
        assert 0 <= first[k] < len(toks) and toks[first[k]] != T.WORD
        if u[0] in (cp.ALEF, cp.SMALL_WAW, cp.SMALL_YEH):
            assert toks[first[k]] in ("aa", "uu", "ii")


def test_mismatched_vid_is_refused():
    with pytest.raises(T.Tj3Error):
        T.tj2_to_tj3([cp.BEH + cp.FATHA], [VID.index("teh"), VID.index("fatha")], VID)


def test_geminate_view(tb):
    phones = ayah(tb, 1, 2)                        # lillahi, rabbi: two geminates
    toks, first = both(phones)
    units = [t.text for t in phones_to_tokens(phones)]
    g = T.geminate_view(toks, units, first)
    assert sum(t in T.GEMINATE for t in g) == sum(cp.SHADDA in u.split(":")[0] for u in units) >= 2
    assert [t[0] if t in T.GEMINATE else t for t in g] == toks and all(t in T.INDEX_G for t in g)
    bare = [t for t in toks if t != T.WORD]        # crops: no unit_first, no boundaries
    assert T.geminate_view(bare, units) == [t for t in g if t != T.WORD]
    with pytest.raises(T.Tj3Error):
        T.geminate_view(bare[:-1], units)
