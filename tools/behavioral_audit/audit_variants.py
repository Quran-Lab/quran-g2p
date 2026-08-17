"""Sweep A: enumerate waqf variants for ALL 6,236 ayat and assert the
doctrine-derived invariants on every mode.

A1 sukun variant phones == plain phonemize output (identity)
A2 ishmam == sukun modulo the final tag (no phonetic difference)
A3 rawm: final = partial vowel (damm/kasra), pre-final letter loses
   qalqalah, and NO free length in the final word may keep 6
   (aared/leen collapse to 2; muttasil to {4,5})
A4 admissibility, independently derived from the RAW TEXT: no
   rawm/ishmam when the final wasl-haraka is fath-class or absent;
   ishmam only for damm-class
"""
import re
import sys
import unicodedata
from collections import Counter

from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))
from quran_g2p.phonemize import phonemize
from quran_g2p.textbank import AyahRef, TextBank
from quran_g2p.variants import enumerate_variants

TB = TextBank.load("tanzil")

FATH = {"\u064e", "\u064b"}          # fatha, fathatan
DAMM = {"\u064f", "\u064c"}          # damma, dammatan
KASR = {"\u0650", "\u064d"}          # kasra, kasratan


def final_wasl_haraka(word):
    """Last haraka mark in the final word, from raw text (independent of
    the engine's waqf tables)."""
    marks = [c for c in word if c in FATH | DAMM | KASR]
    # the haraka on the LAST consonant: scan from the end
    for i in range(len(word) - 1, -1, -1):
        c = word[i]
        if c in FATH:
            return "fath"
        if c in DAMM:
            return "damm"
        if c in KASR:
            return "kasr"
        if c in "\u06e4\u06e5\u06e6\u06e7\u0653\u0670":
            continue   # small letters / madd sign are haraka carriers
        if not unicodedata.combining(c) and c not in "\u0640":
            # base letter with no haraka after it -> sakin ending
            return None
    return None


def sig(p):
    return (p.base, p.kind, p.geminated, p.ghunna, p.qalqalah, p.tafkheem,
            None if p.length is None else (p.length.kind,
                                           tuple(sorted(p.length.allowed)),
                                           p.length.canonical))


viol = Counter()
examples = {}
checked = 0
for ref in TB.refs():
    text = TB.ayah(ref)
    plain = phonemize(text, edition="tanzil", ref=ref).segments[0].phones
    (variants,) = enumerate_variants(text, edition="tanzil", ref=ref)
    modes = {}
    for v in variants:
        modes.setdefault(v.mode, v)
    checked += 1

    def flag(k):
        viol[k] += 1
        examples.setdefault(k, f"{ref.surah}:{ref.ayah}")

    # A1 sukun == plain
    su = modes.get("sukun")
    if su is None:
        flag("no-sukun-variant")
        continue
    if [sig(p) for p in su.phones] != [sig(p) for p in plain]:
        flag("A1-sukun-differs-from-plain")

    # A2 ishmam == sukun modulo final tagging
    if "ishmam" in modes:
        ish = modes["ishmam"]
        if len(ish.phones) != len(su.phones):
            flag("A2-ishmam-length")
        elif [sig(p) for p in ish.phones] != [sig(p) for p in su.phones]:
            flag("A2-ishmam-phonetic-drift")

    # A3 rawm invariants
    if "rawm" in modes:
        rw = modes["rawm"]
        last = rw.phones[-1]
        if last.kind != "vowel" or last.pausal_role != "rawm":
            flag("A3-rawm-final-not-partial-vowel")
        if len(rw.phones) >= 2 and rw.phones[-2].qalqalah is not None:
            flag("A3-rawm-qalqalah-survives")
        w = rw.phones[-2].word_index if len(rw.phones) >= 2 else None
        for p in rw.phones:
            if p.word_index == w and p.length is not None \
                    and p.length.kind == "free" and 6 in p.length.allowed:
                flag("A3-rawm-keeps-6")

    # A4 raw-text admissibility
    h = final_wasl_haraka(text.split(" ")[-1])
    if h in (None, "fath"):
        if "rawm" in modes:
            flag("A4-rawm-on-" + ("sakin" if h is None else "fath"))
        if "ishmam" in modes:
            flag("A4-ishmam-on-" + ("sakin" if h is None else "fath"))
    if h == "kasr" and "ishmam" in modes:
        flag("A4-ishmam-on-kasr")

print(f"ayat checked: {checked}")
if viol:
    for k, n in viol.most_common():
        print(f"  {k}: {n}  e.g. {examples[k]}")
else:
    print("ALL INVARIANTS HOLD")
