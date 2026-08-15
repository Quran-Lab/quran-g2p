"""The '~' ghunna axis on naqis idgham targets (SPEC-003 amendment).

Idgham bi-ghunna into waw/yeh is NAQIS: the target is nasalized but not
geminated, so neither shadda nor a mukhfah base marks it - without an
axis marker the token stream renders a rule-bearing acoustic event
invisible (and unmappable onto the old vocab's dedicated units). '~' is
ASCII like '^': normalization-immune.
"""
from quran_g2p.phonemize import phonemize
from quran_g2p.textbank import AyahRef, TextBank
from quran_g2p.tokenlayer import phones_to_tokens

TB = TextBank.load("tanzil")


def tokens(s, a):
    ref = AyahRef(s, a)
    (seg,) = phonemize(TB.ayah(ref), edition="tanzil", ref=ref).segments
    return [t.text for t in phones_to_tokens(seg.phones)]


def test_tanween_waw_naqis_target_marked():
    # 2:7 غِشَٰوَةٞ وَلَهُمْ: the junction waw is nasalized -> و~َ
    assert "و~َ" in tokens(2, 7)


def test_noon_yeh_naqis_target_marked():
    # 36:9 بَيْنِ أَيْدِيهِمْ؟ no — use 2:2 هُدٗى لِّلْمُتَّقِينَ has lam;
    # 99:7 خَيْرٗا يَرَهُۥ: tanween + yeh -> ي~َ
    assert "ي~َ" in tokens(99, 7)


def test_plain_waw_unmarked():
    # the waw inside غِشَٰوَةٞ stays plain وَ
    toks = tokens(2, 7)
    assert "وَ" in toks  # plain consonant waws still exist in the ayah
