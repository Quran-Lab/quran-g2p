"""Cross-site madd constraints: the free madd lengths of ONE recitation are not independent.

Within one sitting the reciter keeps each free class at one length (taswiyah: al-Nashr 1:343-344; Hidayat al-Qari
1:288), and the classes are ordered:

  - munfasil and silah kubra are one class (the silah kubra follows the munfasil's length);
  - muttasil >= munfasil (the stronger cause is never shorter: الأقوى لا يكون أدنى من الأضعف);
  - muttasil at waqf on its own hamza (R185_MUTTASIL_WAQF) >= the wasl muttasil;
  - leen <= 'aarid (leen lil-sukun never exceeds the 'aarid of the same reciter);
  - the 'ayn of كهيعص / حمعسق {4,6} and الٓمٓ ٱللَّهُ {2,6} are their own one-site classes.

Rawm forms already carry their reduced sets in the LengthSpec ('aarid -> 2, muttasil loses the waqf 6); the
constraints act on the sets as found on the path. `assignments` enumerates the legal joint choices over the classes
present (route "shatibiyyah" uses `allowed`, route "scoring" uses the attested `scoring` sets, which is how a
Tayyibah route such as qasr al-munfasil 2 is admitted once the reciter profile has detected it).
"""
from __future__ import annotations

from itertools import product

#: rule id -> constraint class
CLASS_OF = {
    "R186_MUNFASIL": "munfasil", "R184_SILAH_KUBRA": "munfasil",
    "R185_MUTTASIL": "muttasil", "R185_MUTTASIL_WAQF": "muttasil_waqf",
    "R189_AARED": "aarid", "R190_LEEN": "leen", "R188_AIN_LEEN_LAZIM": "ain",
    "R135_MEEM_ALLAH": "alm_allah",
}
FREE_CLASSES = ("munfasil", "muttasil", "muttasil_waqf", "aarid", "leen", "ain", "alm_allah")
#: (shorter-or-equal, longer-or-equal)
ORDER = (("munfasil", "muttasil"), ("muttasil", "muttasil_waqf"), ("leen", "aarid"))


def madd_class(phone) -> str | None:
    """Constraint class of a free-length phone, from its provenance (the LAST class ruling wins: rawm keeps the
    class and only shrinks the set)."""
    if phone.length is None or phone.length.kind != "free":
        return None
    cls = None
    for app in phone.provenance:
        if app.rule_id in CLASS_OF:
            cls = CLASS_OF[app.rule_id]
    return cls


def sites(phones) -> list[tuple[int, str, frozenset, frozenset]]:
    """(phone index, class, allowed, scoring) for every free madd on a path."""
    out = []
    for i, p in enumerate(phones):
        c = madd_class(p)
        if c is not None:
            out.append((i, c, p.length.allowed, p.length.scoring))
    return out


def class_sets(phones, route="shatibiyyah") -> dict[str, frozenset]:
    """The legal set per class on this path: the intersection over its sites (a rawm site narrows its class)."""
    sets: dict[str, frozenset] = {}
    for _, c, allowed, scoring in sites(phones):
        s = allowed if route == "shatibiyyah" else scoring
        sets[c] = sets[c] & s if c in sets else frozenset(s)
    return sets


def legal(choice: dict) -> bool:
    for lo, hi in ORDER:
        if lo in choice and hi in choice and choice[lo] > choice[hi]:
            return False
    return True


def assignments(sets: dict[str, frozenset]) -> list[dict]:
    """Every legal joint length choice over the classes present."""
    classes = sorted(sets)
    out = []
    for vals in product(*(sorted(sets[c]) for c in classes)):
        ch = dict(zip(classes, vals))
        if legal(ch):
            out.append(ch)
    return out


def snap(measured: dict[str, list[float]], sets: dict[str, frozenset], prior: dict | None = None,
         sigma: float = 0.75) -> tuple[dict, float]:
    """MAP joint choice: measured raw counts per class (one value per site), Gaussian site noise sigma (counts),
    optional prior {class: {value: probability}} (the reciter profile). Returns (choice, margin), the margin being the
    cost gap to the best choice that differs in any class (a confidence for the joint snap)."""
    prior = prior or {}
    best = []
    for ch in assignments(sets):
        cost = 0.0
        for c, v in ch.items():
            for x in measured.get(c, ()):
                cost += (x - v) ** 2 / (2 * sigma ** 2)
            p = prior.get(c, {}).get(v)
            if p is not None:
                cost -= __import__("math").log(max(p, 1e-6))
        best.append((cost, ch))
    if not best:
        return {}, 0.0
    best.sort(key=lambda t: t[0])
    margin = best[1][0] - best[0][0] if len(best) > 1 else float("inf")
    return best[0][1], margin
