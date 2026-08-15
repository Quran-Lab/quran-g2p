"""Vocab export (B2): tokens.txt is the contract — blank LAST, hash-manifested.

Determinism: two builds are byte-identical. The manifest's vocab_sha256 is
the anti-footgun key every downstream artifact asserts against.
"""
import json

from quran_g2p.export_vocab import build_vocab, write_vocab


def test_build_deterministic_and_blank_last(tmp_path):
    v1 = build_vocab(edition="tanzil")
    v2 = build_vocab(edition="tanzil")
    assert v1.tokens == v2.tokens
    p1 = tmp_path / "a"
    p2 = tmp_path / "b"
    m1 = write_vocab(v1, p1)
    m2 = write_vocab(v2, p2)
    assert (p1 / "tokens.txt").read_bytes() == (p2 / "tokens.txt").read_bytes()
    assert m1["vocab_sha256"] == m2["vocab_sha256"]

    lines = (p1 / "tokens.txt").read_text(encoding="utf-8").splitlines()
    assert lines[-1].split()[0] == "<blk>"
    assert int(lines[-1].split()[1]) == len(lines) - 1
    manifest = json.loads((p1 / "vocab_manifest.json").read_text(encoding="utf-8"))
    assert manifest["blank_id"] == len(lines) - 1
    assert manifest["size"] == len(lines)
    assert manifest["vocab_id"] == "tj1"
    # frequency table covers every non-blank token
    assert set(manifest["frequencies"]) == set(t for t in v1.tokens)


def test_vocab_includes_free_choice_closure(tmp_path):
    v = build_vocab(edition="tanzil")
    # canonical corpus emits ا:2/ا:4/ا:6; the closure adds the attested
    # munfasil/aared alternatives so alignment-derived labels are expressible
    for t in ("ا:3", "ا:5", "ۦ:3", "ۦ:5", "ۥ:3", "ۥ:5"):
        assert t in v.tokens, t
