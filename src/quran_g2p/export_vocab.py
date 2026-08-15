"""Vocab export (Part B2): tokens.txt + vocab_manifest.json.

tokens.txt IS the contract: one `symbol id` per line, ids dense from 0,
`<blk>` LAST. The manifest carries vocab_sha256 (hash of tokens.txt bytes) —
every downstream artifact embeds and asserts it, which structurally kills the
blank-index confusion class.

The inventory = the canonical corpus enumeration UNION the free-choice
closure: every free LengthSpec's scoring set expands its madd token so
alignment-derived labels (S3) are expressible without vocab changes.
"""
from __future__ import annotations

import hashlib
import json
from collections import Counter
from dataclasses import dataclass
from pathlib import Path

from .phonemize import phonemize
from .textbank import TextBank
from .tokenlayer import phones_to_tokens

_ENGINE_VERSION = "0.0.1"
_SCHEMA_VERSION = 1
_VOCAB_ID = "tj1"
_BLANK = "<blk>"


@dataclass(frozen=True)
class Vocab:
    tokens: tuple[str, ...]          # WITHOUT blank; ordered
    frequencies: dict[str, int]      # canonical-corpus counts (closure -> 0)


def build_vocab(edition: str = "tanzil") -> Vocab:
    tb = TextBank.load(edition)
    freq: Counter[str] = Counter()
    closure: set[str] = set()
    for ref in tb.refs():
        (seg,) = phonemize(tb.ayah(ref), edition=edition, ref=ref).segments
        for tok in phones_to_tokens(seg.phones):
            freq[tok.text] += 1
        toks = phones_to_tokens(seg.phones)
        # map each length-bearing phone to its emitted token text to derive
        # the closure by substituting every scoring-set length
        ti = 0
        for p in seg.phones:
            if p.kind == "vowel":
                continue  # vowels fold into their consonant's token
            tok = toks[ti].text
            ti += 1
            if p.length is None or p.length.kind != "free" or ":" not in tok:
                continue
            stem = tok.rsplit(":", 1)[0]
            for L in p.length.scoring:
                closure.add(f"{stem}:{L}")
    tokens = sorted(set(freq) | closure)
    frequencies = {t: freq.get(t, 0) for t in tokens}
    return Vocab(tuple(tokens), frequencies)


def write_vocab(vocab: Vocab, out_dir: Path) -> dict:
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    lines = [f"{t} {i}" for i, t in enumerate(vocab.tokens)]
    lines.append(f"{_BLANK} {len(vocab.tokens)}")
    blob = ("\n".join(lines) + "\n").encode("utf-8")
    (out_dir / "tokens.txt").write_bytes(blob)
    manifest = {
        "schema_version": _SCHEMA_VERSION,
        "vocab_id": _VOCAB_ID,
        "vocab_sha256": hashlib.sha256(blob).hexdigest(),
        "size": len(vocab.tokens) + 1,
        "blank_id": len(vocab.tokens),
        "engine_version": _ENGINE_VERSION,
        "frequencies": vocab.frequencies,
    }
    (out_dir / "vocab_manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=1), encoding="utf-8")
    return manifest
