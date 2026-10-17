"""Vocabulary coverage audit over EVERY legal form (the tj2 builder's input).

Sweeps the whole corpus through the lattice: every word under every boundary state (wasl / ibtida / waqf), every waqf
mode (sukun, rawm, ishmam), every khilaf site's alternate wajh, every junction between consecutive ayat (and the
surah joins through the basmala), and every free length in each phone's scoring set. Each token is checked against a
vocabulary (tokens.txt) and the missing ones are reported with a first example.

  python tools/audit_vocab_coverage.py [--vocab artifacts/tokenizer_tj1/tokens.txt] [--out audit.json]
"""
import argparse, collections, json, sys, time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from quran_g2p.lattice import build_lattice  # noqa: E402
from quran_g2p.textbank import AyahRef, TextBank  # noqa: E402
from quran_g2p.tokenlayer import phones_to_tokens  # noqa: E402


def form_tokens(phones):
    """Tokens of a form, with every free-length phone expanded over its scoring set (one phone at a time; tokens
    are independent of each other's lengths)."""
    base = [t.text for t in phones_to_tokens(list(phones))]
    out = set(base)
    for i, p in enumerate(phones):
        if p.length is not None and p.length.kind == "free":
            for L in p.length.scoring:
                ph = list(phones)
                ph[i] = p.with_realized_len(L)
                out.update(t.text for t in phones_to_tokens(ph))
    return out, base


def lattice_forms(lat):
    for k, fs in lat.forms.items():
        for f in fs:
            yield k, f, None
    for k, fs in lat.site_forms.items():
        for f in fs:
            yield k[1:], f, k[0]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--vocab", default=str(ROOT / "artifacts/tokenizer_tj1/tokens.txt"))
    ap.add_argument("--out", default="")
    ap.add_argument("--edition", default="tanzil")
    a = ap.parse_args()
    vocab = {l.rsplit(" ", 1)[0] for l in Path(a.vocab).read_text(encoding="utf-8").splitlines() if l.strip()}
    tb = TextBank.load(a.edition)
    seen = collections.Counter()          # token -> number of (word, state, mode, site) forms using it
    canonical = collections.Counter()     # canonical-length tokens only (frequency proxy)
    example = {}
    by_source = collections.defaultdict(set)
    t0 = time.time()
    refs = list(tb.refs())

    def take(lat, label):
        for (w, left, right), f, site in lattice_forms(lat):
            toks, base = form_tokens(f.phones)
            src = ("site" if site else f"{left}/{right}/{f.mode}")
            for t in toks:
                seen[t] += 1
                by_source[t].add(src if t in base else src + "/len")
                example.setdefault(t, f"{label} w{w} {left}/{right} {f.mode}{' ' + site if site else ''}")
            for t in base:
                canonical[t] += 1

    for ref in refs:
        lat = build_lattice([(ref, tb.ayah(ref))], edition=a.edition)
        take(lat, f"{ref.surah}:{ref.ayah}")
    n_j = 0
    for x, y in zip(refs, refs[1:]):
        if x.surah == y.surah:
            groups = [[x, y]]
        elif y.surah == 9:
            groups = [[x, y]]
        else:
            groups = [[x, AyahRef(1, 1), y]]
        for g in groups:
            items = [(r, tb.ayah(r)) for r in g]
            lat = build_lattice(items, edition=a.edition)
            # only the junction words matter here: the last word of each non-final item and the first of the next
            take(lat, "+".join(f"{r.surah}:{r.ayah}" for r in g))
            n_j += 1
    missing = sorted(t for t in seen if t not in vocab)
    unused = sorted(t for t in vocab if t not in seen and t != "<blk>")
    print(f"{len(refs)} ayat + {n_j} junction groups in {time.time() - t0:.0f} s: {len(seen)} distinct tokens over "
          f"all legal forms; {len(missing)} missing from {Path(a.vocab).parent.name}; {len(unused)} vocab tokens unused")
    for t in missing:
        print(f"  MISSING {t:10s} forms={seen[t]:6d} via {sorted(by_source[t])[:4]}  e.g. {example[t]}")
    if a.out:
        Path(a.out).write_text(json.dumps({"missing": {t: {"forms": seen[t], "sources": sorted(by_source[t]),
                                                            "example": example[t]} for t in missing},
                                           "unused": unused, "seen": dict(seen), "canonical": dict(canonical)},
                                          ensure_ascii=False, indent=1), encoding="utf-8")


if __name__ == "__main__":
    main()
