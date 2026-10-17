"""Khilaf sites as per-site choices (quran_g2p.khilaf) and the frozen variant set.

- the frozen site table (artifacts/khilaf_sites.json, tools/build_khilaf_sites.py) equals the declared sites of every
  knob, and its hash is pinned;
- a site's alternate wajh changes only the site's words;
- two sites of the same knob in one span are chosen independently;
- every one of the 17 second-wajh register rows is a knob site, a set-valued length, or a stated exclusion;
- the corpus-wide variant set (every word, boundary state, waqf mode and site wajh, as tokens with their length sets)
  hashes to a frozen value.
"""
import hashlib
import json
from pathlib import Path

from quran_g2p import khilaf as KH
from quran_g2p.lattice import IBTIDA, WAQF, WASL, build_lattice
from quran_g2p.textbank import AyahRef, TextBank
from quran_g2p.tokenlayer import phones_to_tokens

TB = TextBank.load("tanzil")
ROOT = Path(__file__).parents[1]
SITE_TABLE_SHA = "50bd15f88bc97457988ad999ac366fb5d81d1b7a72b527753477de5a95116f82"
VARIANT_SET_SHA = "00a0f8e57b0724a6c1be4efec44fcf4b0182dfd89a51e87f948caa3060c0c85b"


def items_of(*refs):
    return [(AyahRef(*r), TB.ayah(AyahRef(*r))) for r in refs]


def table():
    return json.loads((ROOT / "artifacts" / "khilaf_sites.json").read_text(encoding="utf-8"))


def test_frozen_table_matches_declared_sites():
    t = table()
    for knob, (alt, declared, rows, tag) in KH.KNOBS.items():
        assert sorted(map(list, declared)) == t["sites"][knob], knob
    blob = json.dumps({"sites": t["sites"], "words": t["words"]}, ensure_ascii=False, sort_keys=True)
    assert hashlib.sha256(blob.encode()).hexdigest() == t["sha256"] == SITE_TABLE_SHA


def test_site_changes_only_its_words():
    for knob, words in table()["words"].items():
        for key, ws in words.items():
            s, a = map(int, key.split(":"))
            refs = [(s, a), (s, a + 1)] if knob in KH.JUNCTION_KNOBS else [(s, a)]
            lat = build_lattice(items_of(*refs))
            (site,) = [x for x in lat.sites if x.startswith(knob + "@")]
            assert lat.sites[site]["words"] == ws, (knob, key)
            for (sid, w, l, r) in lat.site_forms:
                assert w in ws


def test_two_sites_of_one_knob_are_independent():
    # 6:143 and 6:144 each carry an istifham site: base at one, tasheel at the other
    lat = build_lattice(items_of((6, 143), (6, 144)))
    sites = sorted(lat.sites)
    assert len(sites) == 2 and all(s.startswith("istifham_tasheel@") for s in sites)
    base = lat.path([])
    mixed = lat.path([], choice={sites[0]: "istifham_tasheel", sites[1]: "base"})
    both = lat.path([], choice={sites[0]: "istifham_tasheel", sites[1]: "istifham_tasheel"})
    w0 = lat.sites[sites[0]]["words"]
    w1 = lat.sites[sites[1]]["words"]
    def byw(ph):
        d = {}
        for p in ph:
            d.setdefault(p.word_index, []).append(p)
        return d

    def diff(x, y):
        bx, by = byw(x), byw(y)
        return {w for w in set(bx) | set(by) if bx.get(w) != by.get(w)}
    assert diff(base, mixed) and diff(base, mixed) <= set(w0)
    assert diff(mixed, both) and diff(mixed, both) <= set(w1)


def test_junction_site_maliyah():
    lat = build_lattice(items_of((69, 28), (69, 29)))
    (site,) = list(lat.sites)
    sakt = lat.path([])
    idgham = lat.path([], choice={site: "maliyah_idgham"})
    assert any(p.sakt_after for p in sakt)
    assert not any(p.sakt_after for p in idgham) and any(p.geminated for p in idgham)
    # with a stop at the junction there is no junction and no site choice to make
    stop = lat.path([lat.word_item.index(1) - 1], choice={site: "maliyah_idgham"})
    assert stop == lat.path([lat.word_item.index(1) - 1])


def test_register_rows_all_accounted():
    rows = {8, 32, 33, 34, 78, 81, 125, 126, 153, 163, 168, 169, 170, 185, 189, 197, 199}
    covered = {r for (_, _, rs, _) in KH.KNOBS.values() for r in rs}
    length_rows = {189}          # الٓمٓ ٱللَّهُ: LengthSpec {2, 6} on the junction (test_concat)
    assert rows == covered | length_rows | set(KH.EXCLUDED_ROWS), rows - (covered | length_rows | set(KH.EXCLUDED_ROWS))


def variant_set_hash():
    h = hashlib.sha256()
    for ref in TB.refs():
        lat = build_lattice([(ref, TB.ayah(ref))])
        rows = []
        for key in sorted(lat.forms):
            for f in lat.forms[key]:
                rows.append([list(key), f.mode, None, [t.text for t in phones_to_tokens(list(f.phones))],
                             [sorted(p.length.scoring) for p in f.phones if p.length and p.length.kind == "free"]])
        for key in sorted(lat.site_forms):
            for f in lat.site_forms[key]:
                rows.append([list(key[1:]), f.mode, key[0], [t.text for t in phones_to_tokens(list(f.phones))],
                             [sorted(p.length.scoring) for p in f.phones if p.length and p.length.kind == "free"]])
        h.update(json.dumps([ref.surah, ref.ayah, rows], ensure_ascii=False).encode("utf-8"))
    return h.hexdigest()


def test_variant_set_hash_frozen():
    assert variant_set_hash() == VARIANT_SET_SHA
