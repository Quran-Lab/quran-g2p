"""Khilaf sites: the second wajhs within Hafs 'an 'Asim min tariq al-Shatibiyyah, as PER-SITE choices.

Every topological khilaf (a different phone stream, not only a different madd length) is a HafsConfig knob; a site
is one (knob, ayah) pair, so the choice at 54:16 is independent of the choice at 54:18. The lattice builds the
flipped run once and splices it in for the site's words only (lattice.build_lattice); the frozen table
khilaf_sites.json (tools/build_khilaf_sites.py, corpus-wide diff of every knob) pins exactly which words each site
touches, and test_khilaf.py proves the flip changes nothing outside them.

Length khilaf ('ayn of كهيعص/حمعسق {4,6}, الم + ٱللَّه {2,6}, every free madd) is NOT here: it stays set-valued in
the phones' LengthSpecs and is measured, with the cross-site relations in madd_constraints.py.

Second-wajh register rows (the 17 «فيه وجهان» verdicts of the review) and where each lives:

  row   site                         handled as
  8     يَلْهَث ذَّٰلِكَ 7:176 izhar     EXCLUDED: the izhar wajh is Tayyibah-only; Shatibiyyah idgham qawlan wahidan
  32    فِرْقٍ 26:63 wasl tafkheem      knob firq_wasl_tafkheem
  33    وَنُذُرِ 54:16.. waqf tafkheem   knob nudhur_waqf_tafkheem (six sites, one per ayah)
  34    يَسْرِ 89:4 waqf tafkheem        knob yasr_waqf_tafkheem
  78    ضَعْف 30:54 damm                knob daaf_30_54_damm (one site: the three words of the ayah together)
  81    ٱلْمُصَۣيْطِرُونَ 52:37 seen      knob musaytirun_52_37_seen
  125   يسٓ 36:1 idgham                 EXCLUDED: idgham of the noon is Tayyibah-only (Shatibiyyah bayt 281: izhar)
  126   نٓ 68:1 idgham                  EXCLUDED: same as 125
  153   عَلَيْهُ ٱللَّهَ 48:10 damm      EXCLUDED: damm is the riwaya's single wajh; the note documents the general kasr rule
  163   مَالِيَهْ 69:28 haa al-sakt     covered by 197 (the haa al-sakt stands in both wajhs; only the wasl join differs)
  168   ءَآلْـَٰٔنَ 10:91               knob istifham_tasheel (each of the six sites separately)
  169   ءَآللَّهُ 10:59                 knob istifham_tasheel
  170   ءَآلذَّكَرَيْنِ 6:143          knob istifham_tasheel
  185   ءَاتَىٰنِۦَ 27:36 waqf hadhf    knob aataani_waqf_yaa
  189   الٓمٓ ٱللَّهُ 3:1-2 qasr         length set {2,6} on the meem-name madd (concat junction), measured
  197   مَالِيَهْ هَلَكَ 69:28-29 idgham knob maliyah_wasl_idgham (concat junction)
  199   the istifham trio              knob istifham_tasheel

Further second wajhs outside the 17 rows, also knobs: 12:11 ta'manna ikhtilas, 77:20 nakhluqkum naqis, 76:4
salasila ithbat at waqf, and the waqf raa of misr / al-qitr / asr. Deliberately NOT knob-sites: 88:22 بِمُصَيْطِرٍ
seen and 2:245 / 7:69 sad (single wajh for this tariq; flipping leaves it).
"""
from __future__ import annotations

from dataclasses import asdict

from .config import HafsConfig

#: knob -> (alternate value, sites (surah, ayah) the knob can touch, register rows, wajh tag)
KNOBS = {
    "firq_wasl_tafkheem": (True, [(26, 63)], (32,), "firq_tafkheem"),
    "nudhur_waqf_tafkheem": (True, [(54, a) for a in (16, 18, 21, 30, 37, 39)], (33,), "nudhur_tafkheem"),
    "yasr_waqf_tafkheem": (True, [(89, 4)], (34,), "yasr_tafkheem"),
    "daaf_30_54_damm": (True, [(30, 54)], (78,), "daaf_damm"),
    "musaytirun_52_37_seen": (True, [(52, 37)], (81,), "musaytirun_seen"),
    "istifham_tasheel": (True, [(6, 143), (6, 144), (10, 51), (10, 59), (10, 91), (27, 59)], (168, 169, 170, 199),
                         "istifham_tasheel"),
    "aataani_waqf_yaa": (False, [(27, 36)], (185,), "aataani_hadhf"),
    "salasila_waqf_alif": (True, [(76, 4)], (), "salasila_ithbat"),
    "taamanna_ikhtilas": (True, [(12, 11)], (), "taamanna_ikhtilas"),
    "nakhluqkum_naqis": (True, [(77, 20)], (), "nakhluqkum_naqis"),
    "misr_waqf_tafkheem": (False, [(10, 87), (12, 21), (12, 99), (43, 51)], (), "misr_tarqeeq"),
    "qitr_waqf_tafkheem": (True, [(34, 12)], (), "qitr_tafkheem"),
    "asr_waqf_tafkheem": (True, [(11, 81), (15, 65), (20, 77), (26, 52), (44, 23)], (), "asr_tafkheem"),
    "maliyah_wasl_idgham": (True, [(69, 28)], (197, 163), "maliyah_idgham"),   # junction 69:28 -> 69:29
}
JUNCTION_KNOBS = {"maliyah_wasl_idgham": ((69, 28), (69, 29))}
EXCLUDED_ROWS = {8: "Tayyibah-only izhar of yalhath dhalika 7:176", 125: "Tayyibah-only idgham of ya-sin 36:1",
                 126: "Tayyibah-only idgham of nun 68:1", 153: "single Hafs wajh (damm), 48:10"}


def flip(config: HafsConfig, **kw) -> HafsConfig:
    d = asdict(config)
    d.update(kw)
    return HafsConfig(**d)


_TABLE = None


def frozen_table():
    """The frozen site table: {knob: [[surah, ayah], ...]} (artifacts/khilaf_sites.json)."""
    global _TABLE
    if _TABLE is None:
        import json
        from pathlib import Path
        p = Path(__file__).resolve().parents[2] / "artifacts" / "khilaf_sites.json"
        _TABLE = json.loads(p.read_text(encoding="utf-8")) if p.exists() else {}
    return _TABLE


def knob_ayat(knob):
    alt, ayat, _, _ = KNOBS[knob]
    if ayat is None:
        ayat = [tuple(x) for x in frozen_table().get("sites", {}).get(knob, [])]
    return ayat


def sites_for(items, edition="tanzil"):
    """Candidate sites of a span: one per (knob, ayah) present. words = the candidate global words of that ayah (the
    lattice keeps only the words whose forms actually change)."""
    offsets, nwords, keys = [], [], []
    off = 0
    for ref, text in items:
        keys.append((ref.surah, ref.ayah))
        offsets.append(off)
        n = _n_words(ref, text, edition)
        nwords.append(n)
        off += n
    out = []
    for knob, (alt, _, _, tag) in KNOBS.items():
        ayat = set(map(tuple, knob_ayat(knob)))
        for i, key in enumerate(keys):
            if key not in ayat:
                continue
            words = set(range(offsets[i], offsets[i] + nwords[i]))
            if knob in JUNCTION_KNOBS:
                a, b = JUNCTION_KNOBS[knob]
                if not (i + 1 < len(keys) and keys[i] == a and keys[i + 1] == b):
                    continue
                words |= set(range(offsets[i + 1], offsets[i + 1] + nwords[i + 1]))
            out.append({"id": f"{knob}@{key[0]}:{key[1]}", "knob": knob, "ref": key, "words": words,
                        "wajh": tag, "base": "base",
                        "config": (lambda cfg, knob=knob, alt=alt: flip(cfg, **{knob: alt}))})
    return out


_NW = {}


def _n_words(ref, text, edition):
    k = (ref.surah, ref.ayah, edition, text)
    if k not in _NW:
        from .pipeline import run
        ctx = run(text, edition=edition, ref=ref)
        _NW[k] = max(s.word_index for s in ctx.segs) + 1
    return _NW[k]
