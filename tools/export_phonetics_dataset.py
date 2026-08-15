"""Export the HF dataset: the complete canonical phonetic layer.

quran_phonetics.jsonl: one row per ayah, every phone fully attributed
(base, kind, gemination, ghunna grade, qalqalah, tafkheem + rank, sakt,
word index, set-valued length prescription, rule provenance, and the
seventeen sifat for consonants).
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from quran_g2p.phonemize import phonemize        # noqa: E402
from quran_g2p.sifat import sifat_of             # noqa: E402
from quran_g2p.textbank import TextBank          # noqa: E402

OUT = ROOT / "artifacts" / "hf_dataset"


def phone_row(p):
    d = {
        "base": p.base.value,
        "kind": p.kind,
        "geminated": p.geminated,
        "word_index": p.word_index,
    }
    if p.length is not None:
        d["length"] = {
            "kind": p.length.kind,
            "allowed": sorted(p.length.allowed),
            "canonical": p.length.canonical,
            "scoring": sorted(p.length.scoring),
        }
    if p.ghunna:
        d["ghunna"] = p.ghunna
    if p.qalqalah:
        d["qalqalah"] = p.qalqalah
    d["tafkheem"] = p.tafkheem
    if getattr(p, "tafkheem_rank", None):
        d["tafkheem_rank"] = p.tafkheem_rank
    if p.sakt_after:
        d["sakt_after"] = True
    rules = [a.rule_id for a in p.provenance]
    if rules:
        d["rules"] = rules
    if p.kind == "consonant":
        d["sifat"] = sifat_of(p)
    return d


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    tb = TextBank.load("tanzil")
    n_phones = 0
    with open(OUT / "quran_phonetics.jsonl", "w", encoding="utf-8") as f:
        for ref in tb.refs():
            (seg,) = phonemize(tb.ayah(ref), edition="tanzil",
                               ref=ref).segments
            rows = [phone_row(p) for p in seg.phones]
            n_phones += len(rows)
            f.write(json.dumps({
                "surah": ref.surah, "ayah": ref.ayah,
                "text": tb.ayah(ref),
                "phones": rows,
            }, ensure_ascii=False) + "\n")
    print(f"6,236 ayat, {n_phones} phones -> {OUT/'quran_phonetics.jsonl'}")


if __name__ == "__main__":
    main()
