"""Build artifacts/tokenizer_tj1/bijection_old250.json (plan B4 warm-start map).

Empirical harvest: for every ayah, the tj1 token stream and the old-greedy
chunking of the oracle-convention expand() string are aligned 1:1; the
observed (tj1 token -> old unit) pairs become the map. Unobserved vocab
tokens (tafkheem '^' splits, scoring-length closure) get a warm-start
parent token instead.
"""
from __future__ import annotations

import hashlib
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT))

from quran_g2p.phonemize import phonemize            # noqa: E402
from quran_g2p.textbank import TextBank              # noqa: E402
from quran_g2p.tokenlayer import phones_to_tokens    # noqa: E402
from oracle.expand import expand                     # noqa: E402

OLD_VOCAB = Path(r"C:\Users\Anon\research\tarteel-asr\data\zipformer_rnnt_ctc"
                 r"\tokenizer\phoneme_units.json")
ART = ROOT / "artifacts" / "tokenizer_tj1"


def greedy(text: str, units: set[str], max_len: int) -> list[str]:
    out = []
    for piece in text.split(" "):
        i = 0
        while i < len(piece):
            for l in range(min(max_len, len(piece) - i), 0, -1):
                if piece[i:i + l] in units:
                    out.append(piece[i:i + l])
                    i += l
                    break
            else:
                raise ValueError(f"unmatchable at {piece[i:]!r} in {piece!r}")
    return out


def merge_splits(toks: list[str], chunks: list[str]) -> list[str]:
    """Reconcile old-vocab granularity limits: greedy fragments a run the
    old inventory caps (leen-7 -> 5+2, pausal geminate-noon 4 -> 3+1) and
    never fused the musahhala with its haraka (tasheel). Merge the tail
    fragment back so alignment stays 1:1; '|' marks the split point (never
    a vocab char)."""
    out = []
    j = 0
    while j < len(chunks):
        c = chunks[j]
        if j + 1 < len(chunks) and len(chunks) - j > len(toks) - len(out):
            n = chunks[j + 1]
            same_run = (len(set(c)) == 1 and len(set(n)) == 1
                        and c[0] == n[0])
            if same_run or (c + n) == "زَ"[:0] + chr(0x0672) + chr(0x064E):
                out.append(c + "|" + n)
                j += 2
                continue
        out.append(c)
        j += 1
    return out


def main() -> None:
    raw = OLD_VOCAB.read_bytes()
    old = json.loads(raw.decode("utf-8"))
    units = {u for u in old if u != "<blank>"}
    max_len = max(len(u) for u in units)

    tb = TextBank.load("tanzil")
    pair_counts: dict[str, Counter] = defaultdict(Counter)
    aligned = mismatches = 0
    mismatch_samples = []
    for ref in tb.refs():
        (seg,) = phonemize(tb.ayah(ref), edition="tanzil", ref=ref).segments
        toks = [t.text for t in phones_to_tokens(seg.phones)]
        chunks = greedy(expand(seg.phones), units, max_len)
        if len(toks) != len(chunks):
            chunks = merge_splits(toks, chunks)
        if len(toks) != len(chunks):
            mismatches += 1
            if len(mismatch_samples) < 5:
                mismatch_samples.append(
                    (f"{ref.surah}:{ref.ayah}", len(toks), len(chunks)))
            continue
        aligned += 1
        for t, c in zip(toks, chunks):
            pair_counts[t][c] += 1

    if mismatches:
        print("MISMATCHES:", mismatches, mismatch_samples)

    # functional resolution: dominant old unit per token; flag conflicts
    mapping = {}
    conflicts = []
    for t, ctr in pair_counts.items():
        unit, n = ctr.most_common(1)[0]
        if len(ctr) > 1:
            conflicts.append((t, dict(ctr)))
        if "|" in unit:
            head, tail = unit.split("|")
            mapping[t] = {"old_unit": head, "old_id_file": old[head],
                          "old_unit_tail": tail,
                          "count": sum(ctr.values()),
                          "provenance": "observed_split"}
        else:
            mapping[t] = {"old_unit": unit, "old_id_file": old[unit],
                          "count": sum(ctr.values()), "provenance": "observed"}
    if conflicts:
        print("CONFLICTS:", json.dumps(conflicts[:8], ensure_ascii=False))

    # vocab closure: unobserved tokens get warm-start parents
    vocab = [line.split(" ")[0] for line in
             (ART / "tokens.txt").read_text(encoding="utf-8").splitlines()]
    observed = set(mapping)
    for tok in vocab:
        if tok in observed or tok == "<blk>":
            continue
        parent = None
        if "^" in tok and tok.replace("^", "") in observed:
            parent = tok.replace("^", "")
        else:
            stem = tok.split(":")[0]
            cands = [o for o in observed if o.split(":")[0] == stem]
            if "^" in stem and not cands:
                cands = [o for o in observed
                         if o.split(":")[0] == stem.replace("^", "")]
            if cands:
                def leng(x):
                    return int(x.split(":")[1]) if ":" in x else 1
                want = leng(tok)
                parent = min(cands, key=lambda o: abs(leng(o) - want))
        mapping[tok] = {"old_unit": None, "old_id_file": None, "count": 0,
                        "provenance": "unmapped", "parent_token": parent}

    out = {
        "meta": {
            "old_vocab_path": str(OLD_VOCAB),
            "old_vocab_sha256": hashlib.sha256(raw).hexdigest(),
            "old_units": sorted(units),
            "old_blank_file_id": 0,
            "old_blank_trainer_id": 250,
            "new_blank_id": 233,
            "ayat_aligned": aligned,
            "alignment_mismatches": mismatches,
            "n_observed": len(observed),
            "n_unmapped": sum(1 for e in mapping.values()
                              if e["provenance"] == "unmapped"),
            "n_conflicts": len(conflicts),
        },
        "map": mapping,
    }
    with open(ART / "bijection_old250.json", "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=1)
    print(json.dumps(out["meta"] | {"old_units": "..."}, ensure_ascii=False))


if __name__ == "__main__":
    main()
