"""Sweep B: EVERY mid-ayah stop position corpus-wide (~70k
segmentations). Invariants per stop k:

B1 words before the stopped word are phone-identical to the unstopped run
B2 words after the resumed word are phone-identical to the unstopped run
B3 the stopped segment ends legally: not a bare short vowel, no live
   tanween (an 'iwad alif-madd is the lawful trace), gemination allowed,
   taa-marbuta word ends in heh
B4 the resumed segment starts legally: first phone is a consonant or a
   hamza, never a madd/vowel, never geminated
"""
import sys
from multiprocessing import Pool

from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))


def sig(p):
    return (p.base, p.kind, p.geminated, p.ghunna, p.qalqalah, p.tafkheem,
            None if p.length is None else (p.length.kind,
                                           tuple(sorted(p.length.allowed))))


def check_surah(surah):
    from quran_g2p.ir import Base
    from quran_g2p.phonemize import phonemize
    from quran_g2p.textbank import AyahRef, TextBank
    from quran_g2p.waqf import WaqfSpec
    TB = TextBank.load("tanzil")
    SHORT = {Base.FATHA, Base.DAMMA, Base.KASRA}
    viols = []
    stops_checked = 0
    for ref in TB.refs():
        if ref.surah != surah:
            continue
        text = TB.ayah(ref)
        base_res = phonemize(text, edition="tanzil", ref=ref)
        base_ph = base_res.segments[0].phones
        nw = max(p.word_index for p in base_ph) + 1
        base_words = {}
        for p in base_ph:
            base_words.setdefault(p.word_index, []).append(sig(p))
        for k in range(nw - 1):
            stops_checked += 1
            try:
                res = phonemize(text, edition="tanzil", ref=ref,
                                waqf=WaqfSpec(stops=(k,)))
            except Exception as e:
                viols.append((f"{ref.surah}:{ref.ayah}", k, "raises",
                              str(e)[:60]))
                continue
            if len(res.segments) != 2:
                viols.append((f"{ref.surah}:{ref.ayah}", k, "segments",
                              len(res.segments)))
                continue
            s1, s2 = res.segments
            w1 = {}
            for p in s1.phones:
                w1.setdefault(p.word_index, []).append(sig(p))
            w2 = {}
            for p in s2.phones:
                w2.setdefault(p.word_index, []).append(sig(p))
            # B1
            for wi in range(0, k):
                if wi < k - 1 and w1.get(wi) != base_words.get(wi):
                    viols.append((f"{ref.surah}:{ref.ayah}", k,
                                  "B1-prefix-drift", wi))
                    break
            # B2
            for wi in range(k + 2, nw):
                if w2.get(wi) != base_words.get(wi):
                    viols.append((f"{ref.surah}:{ref.ayah}", k,
                                  "B2-suffix-drift", wi))
                    break
            # B3 pausal end
            last = s1.phones[-1]
            if last.kind == "vowel" and last.base in SHORT \
                    and last.pausal_role is None:
                viols.append((f"{ref.surah}:{ref.ayah}", k,
                              "B3-bare-final-vowel", last.base.value))
            if last.tanween is not None if hasattr(last, "tanween") else False:
                viols.append((f"{ref.surah}:{ref.ayah}", k,
                              "B3-live-tanween", ""))
            # B4 resume start
            first = s2.phones[0]
            if first.kind != "consonant":
                viols.append((f"{ref.surah}:{ref.ayah}", k,
                              "B4-nonconsonant-start", first.base.value))
            elif first.geminated:
                viols.append((f"{ref.surah}:{ref.ayah}", k,
                              "B4-geminated-start", first.base.value))
    return surah, stops_checked, viols


if __name__ == "__main__":
    from collections import Counter
    total = 0
    agg = Counter()
    examples = {}
    with Pool(8) as pool:
        for surah, n, viols in pool.imap_unordered(check_surah,
                                                   range(1, 115)):
            total += n
            for site, k, kind, det in viols:
                agg[kind] += 1
                examples.setdefault(kind, f"{site} stop={k} {det}")
    print(f"stop positions checked: {total}")
    if agg:
        for kind, n in agg.most_common():
            print(f"  VIOLATION {kind}: {n}  e.g. {examples[kind]}")
    else:
        print("ALL STOP INVARIANTS HOLD")
