"""Freeze the khilaf site table: flip every knob corpus-wide and record exactly which ayat and words change.

For each topological knob (khilaf.KNOBS) and each ayah, the four stop patterns of the lattice are run under the base
and the flipped config; an ayah is a site when any word's form differs, and the words that differ are recorded. The
junction knob (maliyah) is diffed on every adjacent ayah pair. The declared ayat in KNOBS must equal the discovered
ones (None = discovered only), so a knob that leaks outside its sites fails here.

  python tools/build_khilaf_sites.py            -> artifacts/khilaf_sites.json (+ sha256 of the site list)
"""
import hashlib, json, sys, time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from quran_g2p import khilaf as KH  # noqa: E402
from quran_g2p.config import HafsConfig  # noqa: E402
from quran_g2p.lattice import _fill, _word_maps  # noqa: E402
from quran_g2p.textbank import TextBank  # noqa: E402


def phones_key(forms):
    return {k: [tuple((p.base, p.kind, p.geminated, p.ghunna, p.qalqalah, p.tafkheem, p.tafkheem_rank,
                       p.sakt_after, p.pausal_role, p.length) for p in f.phones) for f in fs]
            for k, fs in forms.items()}


def main():
    tb = TextBank.load("tanzil")
    base_cfg = HafsConfig()
    t0 = time.time()
    found = {k: {} for k in KH.KNOBS}
    refs = list(tb.refs())
    for ref in refs:
        items = [(ref, tb.ayah(ref))]
        n = len(_word_maps(items, "tanzil", base_cfg)[0])
        base = phones_key(_fill(items, "tanzil", base_cfg, n, 0, n - 1))
        for knob, (alt, _, _, _) in KH.KNOBS.items():
            if knob in KH.JUNCTION_KNOBS:
                continue
            flipped = phones_key(_fill(items, "tanzil", KH.flip(base_cfg, **{knob: alt}), n, 0, n - 1))
            words = sorted({w for (w, l, r) in base if base[(w, l, r)] != flipped.get((w, l, r))})
            if words:
                found[knob][f"{ref.surah}:{ref.ayah}"] = words
    for knob, (a, b) in KH.JUNCTION_KNOBS.items():
        alt = KH.KNOBS[knob][0]
        for x, y in zip(refs, refs[1:]):
            if x.surah != y.surah:
                continue
            items = [(x, tb.ayah(x)), (y, tb.ayah(y))]
            n = len(_word_maps(items, "tanzil", base_cfg)[0])
            base = phones_key(_fill(items, "tanzil", base_cfg, n, 0, n - 1))
            flipped = phones_key(_fill(items, "tanzil", KH.flip(base_cfg, **{knob: alt}), n, 0, n - 1))
            words = sorted({w for k, w in [(k, k[0]) for k in base] if base[k] != flipped.get(k)})
            if words:
                found[knob][f"{x.surah}:{x.ayah}"] = words
    problems = []
    for knob, (alt, declared, rows, tag) in KH.KNOBS.items():
        got = {tuple(map(int, k.split(":"))) for k in found[knob]}
        if declared is not None and set(map(tuple, declared)) != got:
            problems.append((knob, sorted(set(map(tuple, declared)) ^ got)))
        if not got:
            problems.append((knob, "no site found"))
    sites = {k: sorted([list(map(int, a.split(":"))) for a in v]) for k, v in found.items()}
    blob = json.dumps({"sites": sites, "words": found}, ensure_ascii=False, sort_keys=True)
    out = {"sites": sites, "words": found, "sha256": hashlib.sha256(blob.encode()).hexdigest(),
           "excluded_rows": KH.EXCLUDED_ROWS}
    (ROOT / "artifacts" / "khilaf_sites.json").write_text(json.dumps(out, ensure_ascii=False, indent=1),
                                                          encoding="utf-8")
    for k, v in found.items():
        print(f"{k:24s} {len(v):3d} ayat  {dict(list(v.items())[:6])}")
    print("sha256", out["sha256"], f"{time.time() - t0:.0f} s")
    if problems:
        print("PROBLEMS", problems)
        sys.exit(1)


if __name__ == "__main__":
    main()
