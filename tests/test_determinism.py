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
FROZEN = "5c7e21d33000f204f74b967d61da6e1ab6700a8e15f1e4d497935740586d5619"


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
