"""Per-word legal-variant lattice (Phase III; plan A2 VariantPolicy, the wajh lattice).

A recitation of a text span is fixed by the text EXCEPT for what the reciter chooses: where to stop (waqf) and
restart (ibtida'), how to stop (sukun / rawm / ishmam), the second wajh at a khilaf site, and the free madd lengths.
Enumerating whole-span variants is infeasible (2:282 has 127 word boundaries, 2^127 stop sets), but a word's phones
depend only on the state of its own two boundaries (stop locality, tested in test_lattice.py for single, adjacent
and random multi-stop sets, inside an ayah and across ayat). So the lattice stores, for every word w:

    forms[w][(L, R)]   L in {"wasl", "ibtida"} (is there a stop before w?), R in {"wasl", "waqf"} (after w?)

each a list of WordForm (the waqf modes when R == "waqf"), and any recitation path is the concatenation of one form
per word whose boundary states agree: R(w) == "waqf" iff L(w+1) == "ibtida".  Four phonemize runs per stop pattern
fill every (word, state) slot: no stops, every boundary a stop, even boundaries, odd boundaries.

Khilaf sites (khilaf.py) are per (knob, ayah): the knob's flipped run is spliced in for that site's words only, so two
sites of the same knob in one span are chosen independently. Free madd lengths stay set-valued in each phone's
LengthSpec; madd_constraints.py states the cross-site relations (taswiyah, muttasil >= munfasil, leen <= aared).

Spans may cross ayat (items in recitation order, concat semantics) and may carry CONTEXT items outside the labelled
word range (open edges): with a context item before the range the first labelled word may be in wasl from it.
"""
from __future__ import annotations

from dataclasses import dataclass, field

from .config import HafsConfig
from .ir import Phone
from .textbank import AyahRef
from .waqf import WaqfSpec

WASL, IBTIDA, WAQF = "wasl", "ibtida", "waqf"
STATES = ((WASL, WASL), (WASL, WAQF), (IBTIDA, WASL), (IBTIDA, WAQF))


@dataclass(frozen=True)
class WordForm:
    word: int                      # global word index (the merged stream's)
    left: str                      # "wasl" | "ibtida"
    right: str                     # "wasl" | "waqf"
    mode: str                      # "plain" (R wasl) | "sukun" | "rawm" | "ishmam"
    phones: tuple[Phone, ...]
    site: str | None = None        # khilaf site id when this form is a site's alternate wajh
    wajh: str | None = None        # that wajh's tag


@dataclass
class WordLattice:
    items: list                    # [(AyahRef, text)]
    edition: str
    config: HafsConfig
    n_words: int
    lo: int                        # labelled word range [lo, hi] (global indices)
    hi: int
    word_item: list                # global word -> item index
    text_word: list                # global word -> (item index, whitespace word index in that ayah)
    stoppable: list                # boundary k (after word k) may carry a stop
    forms: dict = field(default_factory=dict)      # (w, L, R) -> [WordForm] (base wajh)
    site_forms: dict = field(default_factory=dict)  # (site, w, L, R) -> [WordForm] (alternate wajh)
    sites: dict = field(default_factory=dict)       # site id -> {"knob", "ref", "words", "wajh", "base"}

    # --- path API -------------------------------------------------------------------------------------------------
    def left_states(self, w):
        if w == 0:
            return (IBTIDA,)
        if not self.stoppable[w - 1]:
            return (WASL,)
        return (WASL, IBTIDA)

    def right_states(self, w):
        if w == self.n_words - 1:
            return (WAQF,)
        if not self.stoppable[w]:
            return (WASL,)
        return (WASL, WAQF)

    def word_forms(self, w, left, right, choice=None):
        """Forms of word w under boundary states and a site choice ({site: wajh}); the alternate wajh replaces the base
        forms only for that site's words."""
        choice = choice or {}
        for site, wajh in choice.items():
            if wajh != self.sites[site]["base"] and (site, w, left, right) in self.site_forms:
                return self.site_forms[(site, w, left, right)]
        return self.forms[(w, left, right)]

    def path(self, stops, modes=None, choice=None) -> list[Phone]:
        """Phones of the labelled range for a stop set (global boundary indices), per-stop waqf modes ({word: mode},
        default sukun) and a site choice."""
        stops = set(stops)
        modes = modes or {}
        out = []
        for w in range(self.lo, self.hi + 1):
            left = IBTIDA if (w == 0 or (w - 1) in stops) else WASL
            right = WAQF if (w == self.n_words - 1 or w in stops) else WASL
            fs = self.word_forms(w, left, right, choice)
            want = modes.get(w, "sukun") if right == WAQF else "plain"
            f = next((f for f in fs if f.mode == want), None)
            if f is None:
                raise KeyError(f"no {want} form for word {w} ({left},{right})")
            out.extend(f.phones)
        return out

    def site_ids(self):
        return sorted(self.sites)


def _run(items, edition, config, stops):
    from .concat import phonemize_concat
    from .phonemize import phonemize
    if len(items) == 1:
        ref, text = items[0]
        return phonemize(text, edition=edition, ref=ref, config=config, waqf=WaqfSpec(tuple(stops)))
    return phonemize_concat(items, edition=edition, config=config, waqf=WaqfSpec(tuple(stops)))


def _word_maps(items, edition, config):
    """global word -> item, and -> whitespace word of its ayah (muqatta'at letter names share one text word)."""
    from .pipeline import run
    word_item, text_word = [], []
    for ii, (ref, text) in enumerate(items):
        ctx = run(text, edition=edition, ref=ref, config=config)
        spaces = [i for i, ch in enumerate(text) if ch == " "]
        firsts = {}
        for seg in ctx.segs:
            firsts.setdefault(seg.word_index, seg.span[0])
        for w in range(max(firsts) + 1):
            start = firsts.get(w, 0)
            word_item.append(ii)
            text_word.append((ii, sum(1 for s in spaces if s < start)))
    return word_item, text_word


def _patterns(n):
    b = list(range(n - 1))
    return {"none": [], "all": b, "even": [k for k in b if k % 2 == 0], "odd": [k for k in b if k % 2 == 1]}


def _state_of(w, stops, n):
    left = IBTIDA if (w == 0 or (w - 1) in stops) else WASL
    right = WAQF if (w == n - 1 or w in stops) else WASL
    return left, right


def _fill(items, edition, config, n, lo, hi, want_variants=True):
    """(w, L, R) -> [WordForm] for every word in [lo, hi] from the four stop patterns."""
    from .variants import segment_waqf_variants
    forms = {}
    for name, stops in _patterns(n).items():
        sset = set(stops)
        res = _run(items, edition, config, stops)
        for seg in res.segments:
            byw = {}
            for p in seg.phones:
                byw.setdefault(p.word_index, []).append(p)
            if not byw:
                continue
            last = max(byw)
            for w, ph in byw.items():
                if not (lo <= w <= hi):
                    continue
                left, right = _state_of(w, sset, n)
                if (w, left, right) in forms:
                    continue
                if right == WASL:
                    forms[(w, left, right)] = [WordForm(w, left, right, "plain", tuple(ph))]
                    continue
                assert w == last, (w, last)
                vs = segment_waqf_variants(seg.phones, res.trace, config) if want_variants else []
                out = [WordForm(w, left, right, "sukun", tuple(ph))]
                for v in vs:
                    tail = tuple(p for p in v.phones if p.word_index == w)
                    out.append(WordForm(w, left, right, v.mode, tail))
                forms[(w, left, right)] = out
    return forms


def build_lattice(items: list[tuple[AyahRef, str]], edition: str = "tanzil", config: HafsConfig | None = None,
                  word_range: tuple[int, int] | None = None, khilaf: bool = True,
                  variants: bool = True) -> WordLattice:
    """Lattice of a span. items: consecutive ayat in recitation order (one item = one ayah); word_range: the labelled
    global words (default all; words outside are context for open edges)."""
    config = config or HafsConfig()
    word_item, text_word = _word_maps(items, edition, config)
    n = len(word_item)
    lo, hi = word_range if word_range else (0, n - 1)
    # a stop may fall only between whitespace words (never between the letter names of one muqatta'at word)
    stoppable = [text_word[k] != text_word[k + 1] for k in range(n - 1)]
    lat = WordLattice(items=list(items), edition=edition, config=config, n_words=n, lo=lo, hi=hi,
                      word_item=word_item, text_word=text_word, stoppable=stoppable)
    lat.forms = _fill(items, edition, config, n, lo, hi, variants)
    if khilaf:
        from .khilaf import sites_for
        for site in sites_for(items, edition):
            alt_cfg = site["config"](config)
            alt = _fill(items, edition, alt_cfg, n, lo, hi, variants)
            words = []
            for (w, left, right), fs in alt.items():
                if w not in site["words"]:
                    continue
                base = lat.forms[(w, left, right)]
                if [f.phones for f in fs] != [f.phones for f in base]:
                    lat.site_forms[(site["id"], w, left, right)] = [
                        WordForm(f.word, f.left, f.right, f.mode, f.phones, site["id"], site["wajh"]) for f in fs]
                    words.append(w)
            if words:
                lat.sites[site["id"]] = {"knob": site["knob"], "ref": site["ref"], "words": sorted(set(words)),
                                         "wajh": site["wajh"], "base": site["base"]}
    return lat
