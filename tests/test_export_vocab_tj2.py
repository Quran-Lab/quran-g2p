"""tj2 (artifacts/tokenizer_tj2): tj1's tokens at their ids, new tokens appended, blank last, every legal form
covered (tools/audit_vocab_coverage.py over the whole corpus: 0 missing at the last run; sampled here), and a
warm-start mapping in which every new row has an existing parent."""
import hashlib
import json
from pathlib import Path

from quran_g2p.export_vocab_tj2 import read_tokens
from quran_g2p.lattice import build_lattice
from quran_g2p.textbank import AyahRef, TextBank
from quran_g2p.tokenlayer import parse_token, phones_to_tokens

ROOT = Path(__file__).parents[1]
TJ1 = ROOT / "artifacts/tokenizer_tj1/tokens.txt"
TJ2 = ROOT / "artifacts/tokenizer_tj2"


def test_tj2_extends_tj1_in_place():
    t1, t2 = read_tokens(TJ1), read_tokens(TJ2 / "tokens.txt")
    assert t1[-1] == "<blk>" and t2[-1] == "<blk>"
    assert t2[:len(t1) - 1] == t1[:-1]
    assert len(set(t2)) == len(t2)
    for t in t2[:-1]:
        parse_token(t)


def test_manifest_and_mapping():
    m = json.loads((TJ2 / "vocab_manifest.json").read_text(encoding="utf-8"))
    blob = (TJ2 / "tokens.txt").read_bytes()
    assert m["vocab_sha256"] == hashlib.sha256(blob).hexdigest()
    t2 = read_tokens(TJ2 / "tokens.txt")
    assert m["size"] == len(t2) and m["blank_id"] == len(t2) - 1
    mp = json.loads((TJ2 / "tj1_to_tj2.json").read_text(encoding="utf-8"))
    t1 = read_tokens(TJ1)
    assert mp["old_to_new"][str(len(t1) - 1)] == len(t2) - 1
    for tok, d in mp["new_rows"].items():
        assert t2[d["id"]] == tok and t1[d["parent_tj1_id"]] == d["parent"]
    # b8's head: every row lands somewhere, its no-burst rows on the bare qalqalah letters
    b8 = mp.get("b8_to_new")
    if b8:
        assert len(b8) == 239 and all(0 <= v < len(t2) for v in b8.values())


def test_sampled_legal_forms_are_covered():
    vocab = set(read_tokens(TJ2 / "tokens.txt"))
    tb = TextBank.load("tanzil")
    for s, a in ((1, 1), (2, 74), (2, 255), (12, 11), (69, 28), (77, 20), (89, 1), (8, 56)):
        refs = [AyahRef(s, a)] + ([AyahRef(69, 29)] if (s, a) == (69, 28) else [])
        lat = build_lattice([(r, tb.ayah(r)) for r in refs])
        for fs in list(lat.forms.values()) + list(lat.site_forms.values()):
            for f in fs:
                for t in phones_to_tokens(list(f.phones)):
                    assert t.text in vocab, (s, a, t.text)
