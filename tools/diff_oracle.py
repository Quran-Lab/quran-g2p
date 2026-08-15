"""Differential: our engine vs the reference engine (quran_transcript), whole corpus.

Runs the oracle on ITS OWN packaged text (its rules read its own dabt
density); runs our engine on our pinned Tanzil; expands ours to their
convention; clusters character-level disagreements by local context shape.
Agreement % is INFORMATIONAL — the output that matters is the cluster list,
each of which must be triaged into verdicts (SPEC-000).

Usage: python tools/diff_oracle.py [--limit N] [--ghunna 4] [--ikhfa 3]
"""
from __future__ import annotations

import argparse
import io
import sys
from collections import Counter
from difflib import SequenceMatcher
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from quran_g2p.phonemize import phonemize          # noqa: E402
from quran_g2p.textbank import AyahRef, TextBank   # noqa: E402
from oracle.expand import expand                   # noqa: E402

import quran_transcript as qt                      # noqa: E402


def oracle_string(surah: int, ayah: int, moshaf) -> str:
    uth = qt.Aya(surah, ayah).get().uthmani
    return qt.quran_phonetizer(uth, moshaf, remove_spaces=False).phonemes


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--ghunna", type=int, default=4)
    ap.add_argument("--ikhfa", type=int, default=3)
    args = ap.parse_args()

    moshaf = qt.MoshafAttributes(
        rewaya="hafs",
        madd_monfasel_len=4, madd_mottasel_len=4,
        madd_mottasel_waqf=4, madd_aared_len=4,
    )

    tb = TextBank.load("tanzil")
    refs = list(tb.refs())
    if args.limit:
        refs = refs[: args.limit]

    total = eq = 0
    char_total = char_diff = 0
    clusters: Counter = Counter()
    examples: dict = {}
    hard_fail = 0
    for ref in refs:
        total += 1
        try:
            theirs = oracle_string(ref.surah, ref.ayah, moshaf)
        except Exception as e:  # oracle failure is a cluster too
            clusters[("ORACLE_ERROR", str(e)[:40])] += 1
            hard_fail += 1
            continue
        (seg,) = phonemize(tb.ayah(ref), edition="tanzil", ref=ref).segments
        ours = expand(seg.phones, ghunna_repeat=args.ghunna,
                      ikhfa_repeat=args.ikhfa)
        char_total += max(len(ours), len(theirs))
        if ours == theirs:
            eq += 1
            continue
        sm = SequenceMatcher(None, theirs, ours, autojunk=False)
        for op, a0, a1, b0, b1 in sm.get_opcodes():
            if op == "equal":
                continue
            char_diff += max(a1 - a0, b1 - b0)
            ctx_t = theirs[max(0, a0 - 3):a1 + 3]
            ctx_o = ours[max(0, b0 - 3):b1 + 3]
            key = (op, theirs[a0:a1][:8], ours[b0:b1][:8])
            clusters[key] += 1
            examples.setdefault(key, (f"{ref.surah}:{ref.ayah}", ctx_t, ctx_o))

    print(f"ayah-exact: {eq}/{total} ({100*eq/max(total,1):.1f}%)  "
          f"char-diff: {char_diff}/{char_total} ({100*char_diff/max(char_total,1):.2f}%)  "
          f"oracle-errors: {hard_fail}")
    print(f"distinct clusters: {len(clusters)}")
    for key, n in clusters.most_common(28):
        ex = examples.get(key, ("", "", ""))
        print(f"  [{n:5d}] {key}  @{ex[0]}  theirs=…{ex[1]}…  ours=…{ex[2]}…")


if __name__ == "__main__":
    main()
