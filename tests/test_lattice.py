"""The per-word lattice (Phase III wajh lattice): stop locality, junctions, waqf modes, open edges.

Any recitation path through the lattice (one form per word, boundary states agreeing) must equal what phonemize /
phonemize_concat produce for that stop set, phone for phone in every field the token layer and the labeller read.
tools/audit_lattice.py runs the same checks over the whole corpus (55,920 single-ayah stop sets and 37,409 junction
stop sets at the last run, 0 mismatches); this file holds the fast cross-sections.
"""
import random

import pytest

from quran_g2p.concat import phonemize_concat
from quran_g2p.ir import Base
from quran_g2p.lattice import IBTIDA, WAQF, WASL, build_lattice
from quran_g2p.phonemize import phonemize
from quran_g2p.textbank import AyahRef, TextBank
from quran_g2p.tokenlayer import RAWM, phones_to_tokens
from quran_g2p.waqf import WaqfSpec

TB = TextBank.load("tanzil")

SAMPLE = [(1, 7), (2, 1), (2, 26), (2, 185), (2, 255), (2, 282), (3, 7), (11, 42), (12, 11), (18, 1), (19, 1),
          (24, 52), (27, 36), (30, 54), (36, 52), (54, 16), (75, 27), (76, 4), (77, 20), (83, 14), (89, 4),
          (96, 15), (112, 1)]
PAIRS = [((2, 2), (2, 3)), ((3, 1), (3, 2)), ((8, 75), (9, 1)), ((18, 1), (18, 2)), ((69, 28), (69, 29)),
         ((112, 1), (112, 2)), ((15, 1), (15, 2)), ((6, 143), (6, 144))]


def sig(p):
    return (p.base, p.kind, p.geminated, p.ghunna, p.qalqalah, p.tafkheem, p.tafkheem_rank, p.sakt_after,
            p.pausal_role, p.length, p.word_index)


def items_of(*refs):
    return [(AyahRef(*r), TB.ayah(AyahRef(*r))) for r in refs]


def stop_sets(lat, seed):
    rng = random.Random(seed)
    ks = [k for k in range(lat.n_words - 1) if lat.stoppable[k]]
    out = [[], ks]
    for p in (0.2, 0.5, 0.8):
        out.append([k for k in ks if rng.random() < p])
    for i in range(len(ks) - 1):
        out.append([ks[i], ks[i + 1]])          # adjacent stops: a one-word breath group
    return out


@pytest.mark.parametrize("s,a", SAMPLE, ids=[f"{s}:{a}" for s, a in SAMPLE])
def test_path_equals_phonemize(s, a):
    (ref, text), = items_of((s, a))
    lat = build_lattice([(ref, text)])
    for st in stop_sets(lat, s * 1000 + a):
        want = [sig(p) for seg in phonemize(text, edition="tanzil", ref=ref, waqf=WaqfSpec(tuple(st))).segments
                for p in seg.phones]
        assert [sig(p) for p in lat.path(st)] == want, (s, a, st)


@pytest.mark.parametrize("x,y", PAIRS, ids=[f"{x[0]}:{x[1]}+{y[0]}:{y[1]}" for x, y in PAIRS])
def test_junction_path_equals_concat(x, y):
    items = items_of(x, y)
    lat = build_lattice(items)
    n1 = lat.word_item.index(1)
    for st in stop_sets(lat, x[1]):
        want = [sig(p) for seg in phonemize_concat(items, edition="tanzil", waqf=WaqfSpec(tuple(st))).segments
                for p in seg.phones]
        assert [sig(p) for p in lat.path(st)] == want, (x, y, st)
        if n1 - 1 in st:
            # a stop at the ayah boundary = the two ayat read independently
            ind = []
            for i, (r, tx) in enumerate(items):
                lo = 0 if i == 0 else n1
                hi = n1 - 1 if i == 0 else lat.n_words - 1
                loc = tuple(k - lo for k in st if lo <= k < hi)
                for seg in phonemize(tx, edition="tanzil", ref=r, waqf=WaqfSpec(loc)).segments:
                    ind += [sig(p)[:-1] + (p.word_index + lo,) for p in seg.phones]
            assert ind == want, (x, y, st)


def test_boundary_states_and_stoppable():
    lat = build_lattice(items_of((19, 1), (19, 2)))
    # كهيعص is ONE text word of five letter names: no stop between the names
    assert lat.stoppable[:4] == [False] * 4 and lat.stoppable[4]
    assert lat.left_states(0) == (IBTIDA,)
    assert lat.right_states(lat.n_words - 1) == (WAQF,)
    assert set(lat.right_states(4)) == {WASL, WAQF}


def test_waqf_modes_follow_isharah():
    # 1:1 al-rahim (kasr): sukun + rawm; 112:1 ahad (damm tanween): sukun + rawm + ishmam; 1:2 (fath): sukun only
    for (s, a), modes in (((1, 1), {"sukun", "rawm"}), ((112, 1), {"sukun", "rawm", "ishmam"}),
                          ((1, 2), {"sukun"})):
        lat = build_lattice(items_of((s, a)))
        w = lat.n_words - 1
        got = {f.mode for f in lat.forms[(w, WASL, WAQF)]}
        assert got == modes, (s, a, got)
    # ishmam is seen, not heard: its tokens are the sukun form's
    lat = build_lattice(items_of((112, 1)))
    fs = {f.mode: f for f in lat.forms[(lat.n_words - 1, WASL, WAQF)]}
    tok = lambda f: [t.text for t in phones_to_tokens(list(f.phones))]
    assert tok(fs["ishmam"]) == tok(fs["sukun"])
    assert tok(fs["rawm"])[-1].endswith(RAWM)


def test_mid_ayah_waqf_modes():
    # a stop after 2:255 word 0 (ٱللَّهُ, damm): rawm and ishmam legal there too
    lat = build_lattice(items_of((2, 255)))
    assert {f.mode for f in lat.forms[(0, IBTIDA, WAQF)]} == {"sukun", "rawm", "ishmam"}


def test_rawm_on_kasra_raa_is_muraqqaq():
    for ref in ((89, 1), (97, 5)):
        lat = build_lattice(items_of(ref))
        w = lat.n_words - 1
        left = IBTIDA if w == 0 else WASL
        rawm = next(f for f in lat.forms[(w, left, WAQF)] if f.mode == "rawm")
        raa = [p for p in rawm.phones if p.base is Base.REH][-1]
        assert raa.tafkheem == "moraqaq" and raa.tafkheem_rank is None, ref
        toks = [t.text for t in phones_to_tokens(list(rawm.phones))]
        assert toks[-1] == "رِ" + RAWM, toks    # raa + kasra + rawm, no '^'


def test_yasr_matcher_does_not_catch_al_yusr():
    # ٱلْيُسْرَ 2:185 at waqf: sakin raa, sakin seen, damm before: tafkheem on the general rule, knob or not
    from quran_g2p.config import HafsConfig
    from quran_g2p.khilaf import flip
    (ref, text), = items_of((2, 185))
    for cfg in (HafsConfig(), flip(HafsConfig(), yasr_waqf_tafkheem=True)):
        seg = phonemize(text, edition="tanzil", ref=ref, config=cfg, waqf=WaqfSpec((30,))).segments[0]
        assert seg.phones[-1].base is Base.REH and seg.phones[-1].tafkheem == "mofakham"


def test_qitr_knob_matches():
    from quran_g2p.config import HafsConfig
    from quran_g2p.khilaf import flip
    (ref, text), = items_of((34, 12))
    levels = []
    for cfg in (HafsConfig(), flip(HafsConfig(), qitr_waqf_tafkheem=True)):
        seg = phonemize(text, edition="tanzil", ref=ref, config=cfg, waqf=WaqfSpec((9,))).segments[0]
        levels.append(seg.phones[-1].tafkheem)
    assert levels == ["moraqaq", "mofakham"]


def test_open_edge_range():
    # the second ayah alone as the labelled range, the first as wasl context: paths over the range equal the slice
    items = items_of((112, 1), (112, 2))
    full = build_lattice(items)
    n1 = full.word_item.index(1)
    part = build_lattice(items, word_range=(n1, full.n_words - 1))
    assert set(part.left_states(n1)) == {WASL, IBTIDA}
    for st in ([], [n1 - 1]):
        a = [sig(p) for p in full.path(st) if p.word_index >= n1]
        b = [sig(p) for p in part.path(st)]
        assert a == b, st


def test_taamanna_site_is_word_five_only():
    # with a stop after word 6 the second breath group holds وَإِنَّا (word 8, geminated noon): neither the
    # ishmam ruling nor the ikhtilas wajh may touch it
    from quran_g2p.config import HafsConfig
    from quran_g2p.khilaf import flip
    (ref, text), = items_of((12, 11))
    for cfg in (HafsConfig(), flip(HafsConfig(), taamanna_ikhtilas=True)):
        res = phonemize(text, edition="tanzil", ref=ref, config=cfg, waqf=WaqfSpec((6,)))
        seg2 = res.segments[1].phones
        noon = [p for p in seg2 if p.base is Base.NOON and p.geminated and p.word_index == 8]
        assert noon, "wa-inna keeps its geminated noon"
        assert not any(a.rule_id.startswith("R220") for a in noon[0].provenance)
