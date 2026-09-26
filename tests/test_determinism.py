"""A6 criterion 7: frozen corpus determinism hash.

The canonical-config, ayah-end-waqf phonemization of the whole corpus hashes
to a FROZEN value. Any engine change that alters any phone of any ayah moves
the hash — intentional changes update it in the same commit with the reason.
"""
import hashlib
import json

from quran_g2p.phonemize import phonemize
from quran_g2p.textbank import TextBank
from quran_g2p.tokenlayer import phones_to_tokens

# Freeze log:
# 2026-08-15b — 89:4 يَسْرِ waqf-ra tarqeeq (sole delta 89:4).
# 2026-08-15c — 2:72 فَادَّارَأْتُمْ seat dagger (سرج الهمزة) suppressed per
#   Dalil al-Hayran 1:415 / Ward al-Taif 1:230 (sole delta 2:72).
# 2026-08-15d — 'ayn canonical 4 -> 6 (Shatibiyyah bayt 177 «والطول فضلا»;
#   Hidayat al-Qari 1:343); deltas 19:1, 42:2 only.
# 2026-08-15e — raa-khilaf corrections: the six وَنُذُرِ refrains flip to
#   tarqeeq muqaddam (Hidayat al-Qari 1:132-133; النُّذُر article-forms
#   excluded by gemination) and فِرْقٍ 26:63 wasl takes the tarqeeq tarjih.
#   Deltas verified: 26:63 + 54:16,18,21,30,37,39 only.
# 2026-08-15f — '~' ghunna axis on naqis idgham targets (tokenlayer only;
#   PHONES UNTOUCHED, proven by git: sole src delta = tokenlayer.py). The
#   2,430 tanween/noon->waw/yeh targets gain the marker (و~َ ي~َ ...);
#   vocab 229 -> 234, blank 228 -> 233.
# 2026-09-26 — sakin reh after a kasra of the PREVIOUS word (hamzat al-wasl
#   dropped in wasl) is mofakham: رَبِّ ٱرْحَمْهُمَا, أَمِ ٱرْتَابُوٓا۟, إِنِ
#   ٱرْتَبْتُمْ, لِمَنِ ٱرْتَضَىٰ ... Found by the two-way audit against the
#   KFGQPC colour-coded Madinah mushaf. Deltas verified: 5:106, 17:24, 21:28,
#   23:99, 24:50, 24:55, 65:4, 72:27 only.
FROZEN = "ebb0f10e1403edf262083fa79b5b78a7a9edd95782c1ec70b4ffcad73d174ff9"


def corpus_hash() -> str:
    tb = TextBank.load("tanzil")
    h = hashlib.sha256()
    for ref in tb.refs():
        (seg,) = phonemize(tb.ayah(ref), edition="tanzil", ref=ref).segments
        row = {"s": ref.surah, "a": ref.ayah,
               "t": [t.text for t in phones_to_tokens(seg.phones)]}
        h.update(json.dumps(row, ensure_ascii=False).encode("utf-8"))
    return h.hexdigest()


def test_corpus_hash_frozen():
    assert corpus_hash() == FROZEN
