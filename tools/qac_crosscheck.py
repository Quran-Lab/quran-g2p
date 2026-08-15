"""QAC morphology cross-check (plan A3/P3): the fifth oracle.

The Quranic Arabic Corpus (Kais Dukes, corpus.quran.com, v0.4, pinned
sha256 a1d12923...) tags every word segment with POS. For every word the
rasm begins with hamzat al-wasl (Buckwalter '{'), the engine's ibtida'
haraka must agree with the morphology:

  Al+ prefix or REL pronoun  -> hamza + FATHA   (the article class)
  bare noun / proper noun    -> hamza + KASRA   (the seven-noun class)
  verb                       -> hamza + KASRA or DAMMA (third-letter rule)

Any disagreement is a build error to triage, never to average away.
"""
from __future__ import annotations

import hashlib
import re
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from quran_g2p.ir import Base                     # noqa: E402
from quran_g2p.phonemize import phonemize         # noqa: E402
from quran_g2p.textbank import AyahRef, TextBank  # noqa: E402

QAC = ROOT / "data" / "qac-morphology-0.4.txt"
QAC_SHA = "a1d12923815341face765083805d2148ed2d9f5cc3f7d6665219d887675d8c46"

LOC = re.compile(r"\((\d+):(\d+):(\d+):(\d+)\)")


def load_qac():
    raw = QAC.read_bytes()
    if hashlib.sha256(raw).hexdigest() != QAC_SHA:
        raise RuntimeError("QAC file drifted from its pin")
    words = defaultdict(list)  # (s,a,w) -> [(seg, form, tag, feats)]
    for line in raw.decode("utf-8").splitlines():
        if not line.startswith("("):
            continue
        loc, form, tag, feats = line.split("\t")
        s, a, w, g = map(int, LOC.match(loc).groups())
        words[(s, a, w)].append((g, form, tag, feats))
    return words


def classify(segments):
    """Map a wasl-initial word's QAC segments to the expected start class."""
    segments = sorted(segments)
    g, form, tag, feats = segments[0]
    if not form.startswith("{"):
        return None  # word does not begin with hamzat al-wasl
    if "PREFIX|Al+" in feats or tag == "DET":
        return "article"
    if tag in ("REL", "COND") and form.startswith("{l~"):
        return "article"  # al-mawsula (incl. conditional use): fath
    if form.startswith("{l~") or form.startswith("{ll"):
        # fused-article nouns QAC does not segment (الله، اللهم، اللات):
        # the initial IS the article, ibtida' takes fath
        return "article"
    if tag == "V" or "POS:V" in feats:
        return "verb"
    if tag in ("N", "PN") or "POS:N" in feats or "POS:PN" in feats:
        return "noun"
    return f"other:{tag}"


def engine_start(word_text):
    (seg,) = phonemize(word_text, edition="tanzil").segments
    ph = seg.phones
    if ph[0].base is not Base.HAMZA:
        return "no-hamza"
    return ph[1].base.value


EXPECT = {
    "article": {"fatha"},
    "noun": {"kasra"},
    "verb": {"kasra", "damma"},
}


def main() -> dict:
    qac = load_qac()
    tb = TextBank.load("tanzil")

    # word-count alignment guard: QAC and the pinned Tanzil must tokenize
    # identically, else (s,a,w) keys would not be comparable
    # QAC tokenizes بَعْدَ مَا as one word and إِلْ يَاسِينَ as one word;
    # the pinned Tanzil splits them. Word indices shift after the merge
    # point, so these four ayat are excluded from pairing.
    TOKENIZATION_VARIANTS = {(2, 181), (8, 6), (13, 37), (37, 130)}
    misaligned = []
    for ref in tb.refs():
        if (ref.surah, ref.ayah) in TOKENIZATION_VARIANTS:
            continue
        n_tz = len(tb.ayah(ref).split(" "))
        n_qac = max(w for (s, a, w) in qac if s == ref.surah and a == ref.ayah) \
            if any((ref.surah, ref.ayah) == (s, a) for (s, a, w) in qac) else 0
        if n_tz != n_qac:
            misaligned.append((f"{ref.surah}:{ref.ayah}", n_tz, n_qac))

    # classify every wasl-initial word occurrence; test unique (text, class)
    seen = {}
    for (s, a, w), segs in qac.items():
        if (s, a) in TOKENIZATION_VARIANTS:
            continue
        cls = classify(segs)
        if cls is None:
            continue
        text = TB_WORD(tb, s, a, w)
        if text is None or not text.startswith("ٱ"):
            continue  # QAC '{' inside a prefixed word; ibtida' starts earlier
        seen.setdefault((text, cls), (s, a, w))

    mismatches = []
    counts = defaultdict(int)
    for (text, cls), loc in sorted(seen.items(), key=lambda kv: kv[1]):
        counts[cls] += 1
        got = engine_start(text)
        want = EXPECT.get(cls)
        if want is None or got not in want:
            mismatches.append({"loc": f"{loc[0]}:{loc[1]}:{loc[2]}",
                               "word": text, "qac_class": cls,
                               "engine_start": got})
    return {"misaligned_ayat": misaligned, "unique_pairs": len(seen),
            "class_counts": dict(counts), "mismatches": mismatches}


def TB_WORD(tb, s, a, w):
    words = tb.ayah(AyahRef(s, a)).split(" ")
    return words[w - 1] if 1 <= w <= len(words) else None


if __name__ == "__main__":
    import json
    r = main()
    r_small = dict(r)
    r_small["misaligned_ayat"] = r["misaligned_ayat"][:10]
    r_small["mismatches"] = r["mismatches"][:20]
    print(json.dumps(r_small, ensure_ascii=False, indent=1))
    print("total misaligned:", len(r["misaligned_ayat"]),
          "| total mismatches:", len(r["mismatches"]))
