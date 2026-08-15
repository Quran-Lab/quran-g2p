"""Regenerate artifacts/tokenizer_tj1/quran_labels_v1.jsonl (S1 deliverable).

Dual format per row: tj1 tokens + the legacy repeat-string the old trainer
consumes. Lives in tools/ because the legacy text comes from the
quarantined oracle/expand renderer (src/ never imports oracle/).
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT))

from quran_g2p.phonemize import phonemize            # noqa: E402
from quran_g2p.textbank import TextBank              # noqa: E402
from quran_g2p.tokenlayer import phones_to_tokens    # noqa: E402
from oracle.expand import expand                     # noqa: E402


def main() -> None:
    tb = TextBank.load("tanzil")
    manifest = json.loads((ROOT / "artifacts" / "tokenizer_tj1" /
                           "vocab_manifest.json").read_text(encoding="utf-8"))
    out = ROOT / "artifacts" / "tokenizer_tj1" / "quran_labels_v1.jsonl"
    n = 0
    with open(out, "w", encoding="utf-8") as f:
        f.write(json.dumps({"__meta__": {
            "engine_version": manifest["engine_version"],
            "edition": "tanzil", "waqf": "ayah_end",
            "vocab_sha256": manifest["vocab_sha256"],
        }}, ensure_ascii=False) + "\n")
        for ref in tb.refs():
            (seg,) = phonemize(tb.ayah(ref), edition="tanzil",
                               ref=ref).segments
            f.write(json.dumps({
                "surah": ref.surah, "ayah": ref.ayah,
                "tokens": [t.text for t in phones_to_tokens(seg.phones)],
                "text": expand(seg.phones),
            }, ensure_ascii=False) + "\n")
            n += 1
    print(f"wrote {n} rows -> {out.name}")


if __name__ == "__main__":
    main()
