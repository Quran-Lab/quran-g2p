"""Corpus exports (Part B2): ayah_tokens.jsonl + rule_index.jsonl.

ayah_tokens: per ayah — the token sequence (canonical lengths until S3 fills
realized ones) under an explicit config stamp, plus the engine trace summary.

rule_index: per ayah — every attribute-bearing phone with its FULL
prescription (set-valued lengths), dynamic attributes, provenance rule ids,
source span and word index. This is the DB that keeps prescription and
observation separable downstream (tajweed grading, S3 label resolution).
"""
from __future__ import annotations

import json
from dataclasses import asdict
from pathlib import Path

from .config import HafsConfig
from .phonemize import phonemize
from .textbank import TextBank
from .tokenlayer import phones_to_tokens

_ENGINE_VERSION = "0.0.1"


def _length_dict(p):
    if p.length is None:
        return None
    return {
        "kind": p.length.kind,
        "allowed": sorted(p.length.allowed),
        "canonical": p.length.canonical,
        "scoring": sorted(p.length.scoring),
        "realized": p.realized_len,
    }


def export_corpus(out_dir: Path, edition: str = "tanzil",
                  config: HafsConfig | None = None) -> dict:
    config = config or HafsConfig()
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    tb = TextBank.load(edition)

    n_tokens = 0
    with open(out_dir / "ayah_tokens.jsonl", "w", encoding="utf-8") as ft, \
         open(out_dir / "rule_index.jsonl", "w", encoding="utf-8") as fr:
        header = {"__meta__": {"engine_version": _ENGINE_VERSION,
                               "edition": edition,
                               "config": asdict(config),
                               "waqf": "ayah_end"}}
        ft.write(json.dumps(header, ensure_ascii=False) + "\n")
        fr.write(json.dumps(header, ensure_ascii=False) + "\n")
        for ref in tb.refs():
            (seg,) = phonemize(tb.ayah(ref), edition=edition, ref=ref,
                               config=config).segments
            tokens = [t.text for t in phones_to_tokens(seg.phones)]
            n_tokens += len(tokens)
            ft.write(json.dumps(
                {"surah": ref.surah, "ayah": ref.ayah, "tokens": tokens},
                ensure_ascii=False) + "\n")
            entries = []
            for i, p in enumerate(seg.phones):
                rules = [a.rule_id for a in p.provenance if a.rule_id != "EMIT"]
                if (p.length is None and p.ghunna is None and p.qalqalah is None
                        and not p.sakt_after and p.tafkheem == "moraqaq"
                        and not rules):
                    continue
                entries.append({
                    "i": i, "base": p.base.value, "kind": p.kind,
                    "gem": p.geminated,
                    "length": _length_dict(p),
                    "ghunna": p.ghunna, "qalqalah": p.qalqalah,
                    "tafkheem": p.tafkheem, "sakt": p.sakt_after,
                    "rules": rules, "span": list(p.src_span),
                    "word": p.word_index,
                })
            fr.write(json.dumps(
                {"surah": ref.surah, "ayah": ref.ayah, "phones": entries},
                ensure_ascii=False) + "\n")
    return {"ayat": tb.n_ayat, "tokens": n_tokens}
