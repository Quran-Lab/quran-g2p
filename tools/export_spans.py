"""Rule spans as character offsets into the pinned edition.

The engine's native output is a phone stream; its rulings are reachable only
by running it. This exporter republishes the same rulings in the shape a
reader, a colouring UI, or another corpus needs: `(surah, ayah, start, end,
rule_id)` over the exact text of a pinned edition, with no runtime.

Nothing is decided here. Every span is the `trigger_span` a RuleApp already
carries, so the file is a re-serialisation of what `phonemize` produced, not a
second opinion about it. Both channels are read - the provenance on each phone
and the result trace - because a ruling whose content is that something does
NOT happen has no phone to hang off and reports itself only in the trace.

Two things a consumer needs and usually is not given:

  * **The offsets are into ONE text.** The manifest names the edition and
    carries its SHA-256, the same pin `TextBank.load` enforces. Offsets into a
    different Uthmani text are different numbers; check the digest.
  * **Every ayah is present, always.** An ayah with no spans is written with
    an empty list rather than omitted, so "no rule applies here" and "this
    ayah was not computed" can never be confused for one another.

    python tools/export_spans.py [--edition tanzil] [--out DIR]
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from quran_g2p.phonemize import phonemize  # noqa: E402
from quran_g2p.textbank import TextBank, _PINS  # noqa: E402

EMIT = "EMIT"
OUT = ROOT / "artifacts" / "spans"
READING = ("per-ayah, WaqfSpec.ayah_end(), default HafsConfig(); "
           "no phonemize_concat, no non-default wajh knobs")


def spans_for_ayah(text: str, ref, edition: str) -> list[dict]:
    result = phonemize(text, edition=edition, ref=ref)
    seen: set[tuple[str, int, int]] = set()
    for seg in result.segments:
        for p in seg.phones:
            for app in p.provenance:
                if app.rule_id != EMIT:
                    seen.add((app.rule_id, *app.trigger_span))
    for app in result.trace:
        if app.rule_id != EMIT:
            seen.add((app.rule_id, *app.trigger_span))
    return [{"rule": r, "start": s, "end": e}
            for r, s, e in sorted(seen, key=lambda x: (x[1], x[2], x[0]))]


def export(edition: str, out_dir: Path) -> dict:
    tb = TextBank.load(edition)
    out_dir.mkdir(parents=True, exist_ok=True)
    path = out_dir / f"spans-{edition}.jsonl"

    rows, n_spans, n_empty = [], 0, 0
    rule_ids: set[str] = set()
    for ref in tb.refs():
        spans = spans_for_ayah(tb.ayah(ref), ref, edition)
        n_spans += len(spans)
        n_empty += not spans
        rule_ids.update(s["rule"] for s in spans)
        rows.append({"surah": ref.surah, "ayah": ref.ayah, "spans": spans})

    manifest = {
        "generator": "tools/export_spans.py",
        "edition": edition,
        "edition_file": _PINS[edition][0],
        "edition_sha256": _PINS[edition][1],
        "reading": READING,
        "offsets": "character offsets into the ayah text of the pinned edition",
        "ayat": len(rows),
        "ayat_without_spans": n_empty,
        "spans": n_spans,
        "rules": len(rule_ids),
    }
    with path.open("w", encoding="utf-8", newline="\n") as f:
        f.write(json.dumps({"manifest": manifest}, ensure_ascii=False) + "\n")
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")
    (out_dir / f"manifest-{edition}.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8")
    return manifest


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--edition", default="tanzil", choices=sorted(_PINS))
    ap.add_argument("--out", type=Path, default=OUT)
    args = ap.parse_args()
    m = export(args.edition, args.out)
    print(f"{args.out}/spans-{args.edition}.jsonl: {m['spans']} spans, "
          f"{m['rules']} rules, {m['ayat']} ayat "
          f"({m['ayat_without_spans']} with none)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
