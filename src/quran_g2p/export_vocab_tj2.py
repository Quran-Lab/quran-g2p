"""tj2: the tj1 vocabulary closed over every LEGAL form and over the labeller's error grammar.

tj1 was built from the ayah-end canonical forms plus the scoring-set length closure, so a mid-ayah stop on a shadda
final (ٱلْحَقُّ -> حقّ), any rawm, the khilaf alternates and one junction sakt produced tokens it could not hold
(the v5 records builder dropped the shadda to fit them). tj2 keeps tj1's 233 tokens at their ids, appends:

  1. LEGAL: every token of every lattice form (all words x boundary states x waqf modes x khilaf wajhs x junctions
     between consecutive ayat and across the basmala), with every free length expanded over its scoring set;
  2. ERRORS: the closure the learner / mistake labels need: every madd stem x lengths 2..6; the bare (no-burst) qalqalah
     letters; the consonant x {fatha, damma, kasra} x {plain, shadda} grid (reh in both tafkheem states);

and puts the blank LAST. Rawm is the '=' marker after the haraka (audible: a reduced, whispered haraka); ishmam has no
marker (seen, not heard, so its audio is the sukun form's).

`tj1_to_tj2` maps old ids to new (identity for 0..232, blank 233 -> last) and gives each new token a PARENT token whose
output row initialises it when a tj1-trained head (b8's 239-row head included: its five 'X~' no-burst rows become the
bare tj2 qalqalah letters) is warm-started.
"""
from __future__ import annotations

import hashlib
import json
from collections import Counter
from pathlib import Path

from . import codepoints as cp
from .ir import Base
from .tokenlayer import RAWM, _CONS_CHAR, _MADD_CHAR, _QLQ, _VOWEL_CHAR

_BLANK = "<blk>"
VOCAB_ID = "tj2"
SCHEMA_VERSION = 2
ENGINE_VERSION = "0.1.0"
_QALQALAH = (cp.QAF, cp.TAH, cp.BEH, cp.JEEM, cp.DAL)


def read_tokens(path) -> list[str]:
    out = []
    for line in Path(path).read_text(encoding="utf-8").splitlines():
        if line.strip():
            tok, _ = line.rsplit(" ", 1)
            out.append(tok)
    return out


def legal_tokens(edition="tanzil", progress=False) -> Counter:
    """Every token of every legal form (the coverage sweep), with the number of forms using it."""
    from .lattice import build_lattice
    from .textbank import AyahRef, TextBank
    from .tokenlayer import phones_to_tokens
    tb = TextBank.load(edition)
    seen = Counter()

    def take(lat):
        groups = list(lat.forms.values()) + list(lat.site_forms.values())
        for fs in groups:
            for f in fs:
                phones = list(f.phones)
                toks = {t.text for t in phones_to_tokens(phones)}
                for i, p in enumerate(phones):
                    if p.length is not None and p.length.kind == "free":
                        for L in p.length.scoring:
                            ph = list(phones)
                            ph[i] = p.with_realized_len(L)
                            toks.update(t.text for t in phones_to_tokens(ph))
                for t in toks:
                    seen[t] += 1

    refs = list(tb.refs())
    for k, ref in enumerate(refs):
        take(build_lattice([(ref, tb.ayah(ref))], edition=edition))
        if progress and k % 1000 == 0:
            print("ayah", k, flush=True)
    for x, y in zip(refs, refs[1:]):
        group = [x, y] if (x.surah == y.surah or y.surah == 9) else [x, AyahRef(1, 1), y]
        take(build_lattice([(r, tb.ayah(r)) for r in group], edition=edition))
    return seen


def error_closure() -> set[str]:
    out = set()
    stems = [_MADD_CHAR[b] for b in _MADD_CHAR] + [cp.WAW, cp.YEH]
    for s in stems:
        for L in range(2, 7):
            out.add(f"{s}:{L}")
    for q in _QALQALAH:
        out.add(q)                            # sakin qalqalah letter without its burst
    vowels = [_VOWEL_CHAR[b] for b in _VOWEL_CHAR if b.value in ("fatha", "damma", "kasra")]
    plain_cons = [ch for b, ch in _CONS_CHAR.items()
                  if b.value not in ("noon_mukhfah", "meem_mukhfah", "hamza_musahhala", "damma_mukhtalasa")]
    for c in plain_cons:
        for v in vowels:
            out.add(c + v)
            if c != cp.HAMZA:
                out.add(c + cp.SHADDA + v)
    reh = cp.REH
    for v in vowels:
        out.add(reh + "^" + v)
        out.add(reh + cp.SHADDA + "^" + v)
    out.add(reh + "^")
    return out


def parent_of(tok: str, have: set[str]) -> str:
    """The existing token whose output row initialises `tok` (warm start)."""
    cands = []
    stem, _, ln = tok.partition(":")
    if stem == _CONS_CHAR[Base.DAMMA_MUKHTALASA]:
        # the ikhtilas damma of 12:11 sits between the two noons: a damma-bearing noon starts it
        cands += [cp.NOON + cp.DAMMA, cp.NOON + cp.SHADDA + cp.DAMMA]
    if RAWM in stem:
        cands.append(tok.replace(RAWM, ""))
    if ln:
        for L in (int(ln) - 1, int(ln) + 1, 4, 2):
            cands.append(f"{stem}:{L}")
    if tok in _QALQALAH:
        cands.append(tok + _QLQ)
    if cp.SHADDA in stem:
        no_sh = stem.replace(cp.SHADDA, "")
        cands += [no_sh, stem + cp.FATHA, no_sh + _QLQ]
    if "^" in stem:
        cands.append(stem.replace("^", ""))
    elif stem[:1] == cp.REH:
        cands.append(stem[:1] + "^" + stem[1:])
    for v in (cp.FATHA, cp.KASRA, cp.DAMMA):
        cands.append(stem[:1] + v)
        cands.append(stem[:1] + cp.SHADDA + v)
    cands += [stem[:1], stem[:1] + _QLQ]
    for c in cands:
        if c in have and c != tok:
            return c
    return next(t for t in sorted(have) if t[:1] == stem[:1]) if any(t[:1] == stem[:1] for t in have) \
        else sorted(have)[0]


def build_tj2(tj1_tokens_path, edition="tanzil", progress=False) -> dict:
    tj1 = [t for t in read_tokens(tj1_tokens_path) if t != _BLANK]
    seen = legal_tokens(edition, progress)
    legal_new = sorted(t for t in seen if t not in tj1)
    err_new = sorted(t for t in error_closure() if t not in tj1 and t not in seen)
    tokens = tj1 + legal_new + err_new
    have = set(tj1)
    parents = {}
    for t in legal_new + err_new:
        parents[t] = parent_of(t, have)
    return {"tokens": tokens, "tj1": tj1, "legal_new": legal_new, "error_new": err_new, "parents": parents,
            "legal_forms": dict(seen)}


def write_tj2(v: dict, out_dir: Path, b8_vocab_path=None) -> dict:
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    lines = [f"{t} {i}" for i, t in enumerate(v["tokens"])] + [f"{_BLANK} {len(v['tokens'])}"]
    blob = ("\n".join(lines) + "\n").encode("utf-8")
    (out_dir / "tokens.txt").write_bytes(blob)
    idx = {t: i for i, t in enumerate(v["tokens"])}
    blank2 = len(v["tokens"])
    mapping = {
        "from": "tj1", "to": VOCAB_ID,
        "tj1_size": len(v["tj1"]) + 1, "tj2_size": blank2 + 1,
        "old_to_new": {str(i): i for i in range(len(v["tj1"]))} | {str(len(v["tj1"])): blank2},
        "new_rows": {t: {"id": idx[t], "parent": v["parents"][t], "parent_tj1_id": v["tj1"].index(v["parents"][t]),
                         "kind": "legal" if t in v["legal_new"] else "error"}
                     for t in v["legal_new"] + v["error_new"]},
    }
    if b8_vocab_path:
        # b8's head: tj1 order for 0..232, five no-burst rows 'X~' at 233..237, blank 238
        raw = json.loads(Path(b8_vocab_path).read_text(encoding="utf-8"))
        b8 = {}
        for u, i in raw.items():
            if u == "<blank>":
                b8[str(i)] = blank2
            elif u.endswith("~") and u[:-1] in idx and u[:-1] in _QALQALAH:
                b8[str(i)] = idx[u[:-1]]
            elif u in idx:
                b8[str(i)] = idx[u]
        mapping["b8_to_new"] = b8
        mapping["b8_note"] = ("b8 rows 233..237 are the no-burst qalqalah units 'X~'; they initialise (and are the "
                              "labels of) the bare tj2 letters. Every other b8 row is the tj1 row of the same id.")
    (out_dir / "tj1_to_tj2.json").write_text(json.dumps(mapping, ensure_ascii=False, indent=1), encoding="utf-8")
    manifest = {
        "schema_version": SCHEMA_VERSION, "vocab_id": VOCAB_ID,
        "vocab_sha256": hashlib.sha256(blob).hexdigest(), "size": blank2 + 1, "blank_id": blank2,
        "engine_version": ENGINE_VERSION, "parent_vocab": "tj1",
        "counts": {"tj1": len(v["tj1"]), "legal_new": len(v["legal_new"]), "error_new": len(v["error_new"])},
        "markers": {"^": "tafkheem (reh, lam)", "~": "naqis idgham ghunna (waw, yeh)", RAWM: "rawm on the waqf haraka",
                    ":L": "madd / leen length in harakat"},
        "legal_form_counts": v["legal_forms"],
    }
    (out_dir / "vocab_manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=1),
                                                 encoding="utf-8")
    return manifest
