"""Per-rule corpus incidence: how often every registered ruling actually fires.

`test_registry_complete.py` proves the register equals the engine *statically*
— every id in `src/` is registered and every registered id is still in `src/`.
That says nothing about whether a rule ever fires. A rule that has quietly
stopped matching looks exactly like a rule whose configuration the mushaf
happens never to present, and no gate in the suite could tell the two apart.

This exporter counts, over the whole corpus under one declared reading
protocol, the phones and ayat each rule id appears on in a RuleApp trace, and
freezes the table at `tests/rule_incidence_frozen.json`.

A zero is not a failure. A zero **without a stated reason** is: every id that
fires nowhere must say why in `tests/rule_incidence_reasons.json`, and
`tests/test_rule_incidence.py` refuses the table until it does. That file is
hand-maintained and is the only hand-edited half; the frozen table itself is
generated. A reason is a fact about the text, the edition's dabt, or the
reading protocol below - never a ruling - so nothing here is the reviewer's
business.

The protocol is part of the frozen artifact because incidence is meaningless
without it: this is the per-ayah reading, stopping at the ayah end, with the
default config. Rules that need `phonemize_concat` (ayah-to-ayah junction) or
a non-default wajh knob are silent here by construction, and say so.

    python tools/export_incidence.py            # rewrite the frozen table
    python tools/export_incidence.py --check    # report drift, write nothing

Hand-written `reason` values are preserved across regeneration.
"""
from __future__ import annotations

import argparse
import json
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from quran_g2p.phonemize import phonemize  # noqa: E402
from quran_g2p.rules.registry import RULINGS  # noqa: E402
from quran_g2p.textbank import TextBank  # noqa: E402

#: base phone-emission provenance, excluded exactly as export_corpus.py does
EMIT = "EMIT"

FROZEN = ROOT / "tests" / "rule_incidence_frozen.json"
REASONS = ROOT / "tests" / "rule_incidence_reasons.json"
EDITION = "tanzil"
READING = ("per-ayah, WaqfSpec.ayah_end(), default HafsConfig(); "
           "no phonemize_concat, no non-default wajh knobs")


def measure(edition: str = EDITION) -> tuple[dict[str, dict[str, int]], int]:
    """Count each rule id over both channels a RuleApp can reach.

    A rule reports itself either by attaching provenance to the phone it
    changed (`phones`) or by appending to the result trace (`trace`). Some do
    only the latter: a ruling whose content is that something does NOT happen
    has no phone to hang off. Counting only provenance would make every such
    rule look dead, so both channels are counted and kept apart, and a rule is
    silent only when both are zero.
    """
    tb = TextBank.load(edition)
    phones: defaultdict[str, int] = defaultdict(int)
    traced: defaultdict[str, int] = defaultdict(int)
    ayahs: defaultdict[str, set] = defaultdict(set)
    n = 0
    for ref in tb.refs():
        n += 1
        result = phonemize(tb.ayah(ref), edition=edition, ref=ref)
        for seg in result.segments:
            for p in seg.phones:
                for app in p.provenance:
                    if app.rule_id == EMIT:
                        continue  # base phone emission, not a ruling
                    phones[app.rule_id] += 1
                    ayahs[app.rule_id].add(ref)
        for app in result.trace:
            if app.rule_id == EMIT:
                continue
            traced[app.rule_id] += 1
            ayahs[app.rule_id].add(ref)
    counts = {rid: {"phones": phones[rid], "trace": traced[rid],
                    "ayahs": len(ayahs[rid])}
              for rid in sorted(set(phones) | set(traced) | set(ayahs))}
    return counts, n


def load_reasons() -> dict[str, str]:
    """Hand-maintained: why a rule that fires nowhere is entitled to be silent."""
    if not REASONS.exists():
        return {}
    return json.loads(REASONS.read_text(encoding="utf-8"))


def build(counts: dict[str, dict[str, int]], n_ayat: int,
          reasons: dict[str, str]) -> dict:
    rules = {}
    for ruling in RULINGS:
        entry = dict(counts.get(ruling.id,
                               {"phones": 0, "trace": 0, "ayahs": 0}))
        reason = reasons.get(ruling.id)
        if reason:
            entry["reason"] = reason
        rules[ruling.id] = entry
    return {
        "protocol": {"edition": EDITION, "reading": READING, "ayat": n_ayat},
        "rules": dict(sorted(rules.items())),
    }


def is_silent(entry: dict) -> bool:
    """Fires nowhere in the corpus: neither a phone nor a trace entry."""
    return entry["phones"] == 0 and entry["trace"] == 0


def render(doc: dict) -> str:
    return json.dumps(doc, ensure_ascii=False, indent=2) + "\n"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true",
                    help="report drift against the frozen table, write nothing")
    args = ap.parse_args()

    counts, n_ayat = measure()
    doc = build(counts, n_ayat, load_reasons())
    text = render(doc)

    unregistered = sorted(set(counts) - {r.id for r in RULINGS})
    if unregistered:
        print("rule ids fired but not registered:", unregistered)
        return 1

    if args.check:
        if not FROZEN.exists():
            print(f"{FROZEN.name} does not exist")
            return 1
        if FROZEN.read_text(encoding="utf-8") == text:
            print(f"{FROZEN.name} is current ({n_ayat} ayat)")
            return 0
        print(f"{FROZEN.name} is stale; rerun without --check")
        return 1

    FROZEN.write_text(text, encoding="utf-8")
    silent = [rid for rid, e in doc["rules"].items() if is_silent(e)]
    print(f"{FROZEN.relative_to(ROOT)}: {len(doc['rules'])} rules over "
          f"{n_ayat} ayat; {len(silent)} fire nowhere")
    for rid in silent:
        mark = "ok " if doc["rules"][rid].get("reason") else "NO REASON"
        print(f"  {mark} {rid}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
