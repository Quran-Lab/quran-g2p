"""Generate pseudolabels from a request manifest (Phase IV feeder).

Input: JSONL rows, one per clip label request:
  {"surah": 2, "ayah": 255}                          # plain ayah
  {"surah": 2, "ayah": 255, "stops": [4, 11]}        # mid-ayah pauses
  {"surah": 112, "ayah_start": 1, "ayah_end": 4}     # multi-ayah wasl

Output: JSONL rows with the tj1 token sequence, per-segment token lists
(so a pause-aware trainer can insert its own gap handling), the legacy
repeat-string the old tokenizer consumes, and provenance="canonical"
(free-choice lengths are canonical until the alignment ruler passes the
S4 gate; never label these gold).

Usage:
  python tools/make_pseudolabels.py requests.jsonl labels.jsonl
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT))

from quran_g2p.concat import phonemize_concat        # noqa: E402
from quran_g2p.phonemize import phonemize            # noqa: E402
from quran_g2p.textbank import AyahRef, TextBank     # noqa: E402
from quran_g2p.tokenlayer import phones_to_tokens    # noqa: E402
from quran_g2p.waqf import WaqfSpec                  # noqa: E402
from oracle.expand import expand                     # noqa: E402


def label_for(req: dict, tb: TextBank) -> dict:
    if "ayah_start" in req:
        s = req["surah"]
        refs = [AyahRef(s, a)
                for a in range(req["ayah_start"], req["ayah_end"] + 1)]
        items = [(r, tb.ayah(r)) for r in refs]
        res = phonemize_concat(items, edition=tb.edition)
        loc = {"surah": s, "ayah_start": req["ayah_start"],
               "ayah_end": req["ayah_end"]}
    else:
        ref = AyahRef(req["surah"], req["ayah"])
        stops = tuple(req.get("stops", ()))
        res = phonemize(tb.ayah(ref), edition=tb.edition, ref=ref,
                        waqf=WaqfSpec(stops=stops))
        loc = {"surah": ref.surah, "ayah": ref.ayah}
        if stops:
            loc["stops"] = list(stops)

    seg_tokens = [[t.text for t in phones_to_tokens(seg.phones)]
                  for seg in res.segments]
    flat = [t for seg in seg_tokens for t in seg]
    legacy = " ".join(expand(seg.phones) for seg in res.segments)
    return loc | {
        "tokens": flat,
        "segments": seg_tokens,
        "text_legacy": legacy,
        "provenance": "canonical",
    }


def main() -> None:
    src, dst = sys.argv[1], sys.argv[2]
    tb = TextBank.load("tanzil")
    n = 0
    with open(src, encoding="utf-8") as fin, \
            open(dst, "w", encoding="utf-8") as fout:
        for line in fin:
            line = line.strip()
            if not line:
                continue
            row = label_for(json.loads(line), tb)
            fout.write(json.dumps(row, ensure_ascii=False) + "\n")
            n += 1
    print(f"{n} labels -> {dst}")


if __name__ == "__main__":
    main()
