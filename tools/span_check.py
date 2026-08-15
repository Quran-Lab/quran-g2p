"""Trigger-span cross-check vs cpfair/quran-tajweed (SPEC-000 layer d).

Their annotations index the Tanzil uthmani pause+sajdah variant; a skip-map
converts to our plain pinned text. Categories map to our rule ids; positions
match within ±2 chars. Per-category precision/recall over the whole corpus;
every residual must end up verdicted, never averaged away.
"""
from __future__ import annotations

import io
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from quran_g2p.phonemize import phonemize   # noqa: E402
from quran_g2p.textbank import AyahRef, TextBank  # noqa: E402

SKIP = {0x06D6, 0x06D7, 0x06D8, 0x06D9, 0x06DA, 0x06DB, 0x06E9, 0x06DC}

# their rule -> our trace rule-id prefixes ("TEXT:xxxx" = direct codepoint check)
CATEGORY = {
    "iqlab": {"R143"},
    "ikhfa": {"R144"},
    "ikhfa_shafawi": {"R150"},
    "idghaam_ghunnah": {"R141", "R133", "R160"},
    "idghaam_no_ghunnah": {"R142", "R133", "R160"},
    "idghaam_shafawi": {"R133", "R160"},
    "idghaam_mutajanisayn": {"R133", "R160", "R161"},
    "idghaam_mutaqaribayn": {"R133", "R160"},
    "ghunnah": {"R170"},
    "madd_muttasil": {"R185"},
    "madd_munfasil": {"R186", "R184", "R185"},  # fused ha-tanbih: ours muttasil (CONVENTION)
    "madd_6": {"R187", "R188"},
    "madd_246": {"R189", "R190", "R180_PAUSAL"},
    "madd_2": {"R180", "R181", "R134"},
    "qalqalah": {"R200", "R201", "R202", "R161"},
    "hamzat_wasl": {"TEXT:0671"},
    "silent": {"TEXT:06DF", "ABSENT", "R012"},  # their silent-sad = our recorded seen-substitution
    "lam_shamsiyyah": {"R133"},
}


def load_variant() -> dict[tuple[int, int], tuple[str, int]]:
    """(surah, ayah) -> (full variant text, basmala prefix length in chars).

    cpfair indices INCLUDE the embedded basmala on surah-initial ayat; the
    prefix length (0 elsewhere) shifts variant positions onto our stripped
    plain text.
    """
    blob = (ROOT / "data" / "tajweed_spans" / "cpfair-quran-uthmani.txt")
    ayat = {}
    for line in blob.read_bytes().decode("utf-8-sig").splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        s, a, t = line.split("|", 2)
        ayat[(int(s), int(a))] = (t, 0)
    for s in range(2, 115):
        if s == 9:
            continue
        t, _ = ayat[(s, 1)]
        sp = -1
        for _ in range(4):
            sp = t.find(" ", sp + 1)
        ayat[(s, 1)] = (t, sp + 1)
    return ayat


def pos_map(variant_text: str, plain_ext: str) -> list[int]:
    """variant index -> plain_ext index via SequenceMatcher opcodes — robust
    to insertions on either side (pause marks + padding spaces on the variant
    side; any encoding deltas on the plain side)."""
    from difflib import SequenceMatcher
    m = [0] * len(variant_text)
    sm = SequenceMatcher(None, variant_text, plain_ext, autojunk=False)
    for op, a0, a1, b0, b1 in sm.get_opcodes():
        if op == "equal":
            for k in range(a1 - a0):
                m[a0 + k] = b0 + k
        else:
            for k in range(a0, a1):
                m[k] = b0
    return m


def main() -> None:
    spans = json.loads((ROOT / "data" / "tajweed_spans" /
                        "tajweed.hafs.uthmani-pause-sajdah.json").read_text(encoding="utf-8"))
    variant = load_variant()
    tb = TextBank.load("tanzil")

    tp = Counter(); fn = Counter()
    fn_ex = defaultdict(list)
    for row in spans:
        ref = AyahRef(row["surah"], row["ayah"])
        entry = variant.get((ref.surah, ref.ayah))
        if entry is None:
            continue
        vtext, prefix = entry
        plain = tb.ayah(ref)
        basmala = tb.ayah(AyahRef(1, 1)) + " "
        plain_ext = (basmala + plain) if prefix else plain
        pm = pos_map(vtext, plain_ext)
        res = phonemize(plain, edition="tanzil", ref=ref)
        ours: dict[str, list[tuple[int, int]]] = defaultdict(list)
        for app in res.trace:
            ours[app.rule_id].append((app.trigger_span[0], app.trigger_span[1]))
        for p in res.segments[0].phones:
            for a in p.provenance:
                ours[a.rule_id].append((p.src_span[0], p.src_span[1]))

        plain_prefix = len(basmala) if prefix else 0

        covered = set()
        for p in res.segments[0].phones:
            covered.update(range(p.src_span[0], max(p.src_span[1], p.src_span[0] + 1)))

        for ann in row["annotations"]:
            cat = ann["rule"]
            if cat not in CATEGORY:
                continue
            start, end = ann["start"], ann["end"]
            if start >= len(pm):
                fn[cat] += 1
                continue
            w0 = pm[start] - plain_prefix
            w1 = (pm[end - 1] if end - 1 < len(pm) else pm[-1]) - plain_prefix
            if w1 < 0:
                continue  # annotation inside the stripped basmala
            w0 = max(w0, 0)
            lo, hi = w0 - 1, w1 + 2
            hit = False
            for pref in CATEGORY[cat]:
                if pref == "ABSENT":
                    # silence classes: no phone covers the annotated chars
                    if not any(k in covered for k in range(w0, w1 + 1)):
                        hit = True
                elif pref.startswith("TEXT:"):
                    cpv = int(pref[5:], 16)
                    if any(ord(c) == cpv for c in plain[max(0, lo):hi]):
                        hit = True
                else:
                    for rid, ranges in ours.items():
                        if rid.startswith(pref) and any(
                                r0 < hi and max(r1, r0 + 1) > lo for r0, r1 in ranges):
                            hit = True
                            break
                if hit:
                    break
            if hit:
                tp[cat] += 1
            else:
                fn[cat] += 1
                if len(fn_ex[cat]) < 3:
                    fn_ex[cat].append(
                        f"{ref.surah}:{ref.ayah}@{w0} …{plain[max(0, w0 - 4):w1 + 5]}…")

    print(f"{'category':26s} {'tp':>6s} {'fn':>5s}  recall")
    for cat in sorted(CATEGORY):
        t, f = tp[cat], fn[cat]
        r = t / max(t + f, 1)
        print(f"{cat:26s} {t:6d} {f:5d}  {r:.4f}  {fn_ex.get(cat, [])[:3]}")
    return tp, fn, fn_ex


if __name__ == "__main__":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    main()
