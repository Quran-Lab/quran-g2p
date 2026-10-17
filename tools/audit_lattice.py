"""Corpus-wide lattice audit (the slow version of tests/test_lattice.py).

  python tools/audit_lattice.py locality [--trials 6]     every ayah: random multi-stop sets, all-adjacent stop sets,
                                                           lattice path == phonemize(stops), all waqf modes legal
  python tools/audit_lattice.py junctions [--trials 3]    every adjacent ayah pair (and the surah joins through the
                                                           basmala): lattice path == phonemize_concat(stops)
"""
import argparse, random, sys, time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from quran_g2p.concat import phonemize_concat  # noqa: E402
from quran_g2p.lattice import build_lattice  # noqa: E402
from quran_g2p.phonemize import phonemize  # noqa: E402
from quran_g2p.textbank import AyahRef, TextBank  # noqa: E402
from quran_g2p.waqf import WaqfSpec  # noqa: E402


def sig(p):
    return (p.base, p.kind, p.geminated, p.ghunna, p.qalqalah, p.tafkheem, p.tafkheem_rank, p.sakt_after,
            p.pausal_role, p.length, p.word_index)


def stop_sets(lat, rng, trials):
    ks = [k for k in range(lat.n_words - 1) if lat.stoppable[k]]
    sets = [[], ks]                                   # none, every boundary (all single-word groups)
    for _ in range(trials):
        p = rng.choice((0.15, 0.4, 0.7))
        sets.append([k for k in ks if rng.random() < p])
    if len(ks) >= 2:                                  # adjacent pairs: one single-word group in the middle
        i = rng.randrange(len(ks) - 1)
        sets.append([ks[i], ks[i + 1]])
    return sets


def cmd_locality(a):
    tb = TextBank.load(a.edition)
    rng = random.Random(a.seed)
    bad, n, t0 = 0, 0, time.time()
    for ref in tb.refs():
        text = tb.ayah(ref)
        lat = build_lattice([(ref, text)], edition=a.edition)
        for st in stop_sets(lat, rng, a.trials):
            want = [sig(p) for seg in phonemize(text, edition=a.edition, ref=ref, waqf=WaqfSpec(tuple(st))).segments
                    for p in seg.phones]
            got = [sig(p) for p in lat.path(st)]
            n += 1
            if got != want:
                bad += 1
                print("MISMATCH", ref, st, flush=True)
    print(f"locality: {n} stop sets over {len(list(tb.refs()))} ayat, {bad} mismatches, {time.time() - t0:.0f} s")
    return bad


def pairs(tb):
    refs = list(tb.refs())
    for x, y in zip(refs, refs[1:]):
        if x.surah == y.surah:
            yield [x, y]
        elif y.surah != 9:                           # surah join through the basmala (wasl al-jamee')
            yield [x, AyahRef(1, 1), y] if y.surah != 1 else [x, y]
        else:
            yield [x, y]                             # Anfal -> Tawba, no basmala


def cmd_junctions(a):
    tb = TextBank.load(a.edition)
    rng = random.Random(a.seed)
    bad, n, t0 = 0, 0, time.time()
    n_ind = [0]
    for refs in pairs(tb):
        items = [(r, tb.ayah(r)) for r in refs]
        lat = build_lattice(items, edition=a.edition)
        for st in stop_sets(lat, rng, a.trials):
            if refs[-1] == AyahRef(1, 1):
                continue
            try:
                want = [sig(p) for seg in phonemize_concat(items, edition=a.edition, waqf=WaqfSpec(tuple(st))).segments
                        for p in seg.phones]
            except ValueError:
                continue                              # a forbidden basmala join
            got = [sig(p) for p in lat.path(st)]
            n += 1
            if got != want:
                bad += 1
                print("MISMATCH", refs, st, flush=True)
            # a stop on every ayah boundary must reproduce the independent per-ayah runs (word indices shifted)
            offs = sorted({lat.word_item.index(i) for i in range(len(items))})
            cuts = [o - 1 for o in offs[1:]]
            if all(c in st for c in cuts):
                ind = []
                for i, (r, tx) in enumerate(items):
                    lo = offs[i]
                    hi = offs[i + 1] - 1 if i + 1 < len(offs) else lat.n_words - 1
                    loc = tuple(k - lo for k in st if lo <= k < hi)
                    for seg in phonemize(tx, edition=a.edition, ref=r, waqf=WaqfSpec(loc)).segments:
                        ind += [sig(p)[:-1] + (p.word_index + lo,) for p in seg.phones]
                n_ind[0] += 1
                if ind != want:
                    bad += 1
                    print("CONCAT != INDEPENDENT", refs, st, flush=True)
    print(f"junctions: {n} stop sets ({n_ind[0]} with every ayah boundary stopped, checked against independent "
          f"per-ayah runs), {bad} mismatches, {time.time() - t0:.0f} s")
    return bad


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=("locality", "junctions"))
    ap.add_argument("--trials", type=int, default=6)
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--edition", default="tanzil")
    a = ap.parse_args()
    sys.exit(1 if {"locality": cmd_locality, "junctions": cmd_junctions}[a.cmd](a) else 0)


if __name__ == "__main__":
    main()
