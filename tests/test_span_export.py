"""The span export is a re-serialisation, and has to stay one.

`tools/export_spans.py` republishes the engine's rulings as character offsets
into a pinned edition, for consumers that cannot run Python. The risk with any
second copy of the truth is that it drifts from the first and nobody notices,
so this gate holds it to four things:

  * the manifest's digest is the edition pin the engine itself enforces, since
    offsets into a different text are different numbers;
  * every rule id in the file is a registered ruling;
  * every span lies inside its ayah;
  * a sample of ayat, recomputed from the engine, equals the file exactly.

The sample is deterministic (every 137th ayah, a stride coprime with the
corpus), not random: a gate that tests something different on each run cannot
be reasoned about when it fails.
"""
import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

import export_spans as ex  # noqa: E402

from quran_g2p.rules.registry import RULINGS  # noqa: E402
from quran_g2p.textbank import AyahRef, TextBank, _PINS  # noqa: E402

EDITION = "tanzil"
SPANS = ROOT / "artifacts" / "spans" / f"spans-{EDITION}.jsonl"
STRIDE = 137


@pytest.fixture(scope="module")
def exported():
    lines = SPANS.read_text(encoding="utf-8").splitlines()
    manifest = json.loads(lines[0])["manifest"]
    rows = {(r["surah"], r["ayah"]): r["spans"]
            for r in (json.loads(ln) for ln in lines[1:])}
    return manifest, rows


def test_manifest_pins_the_edition(exported):
    manifest, _ = exported
    assert manifest["edition"] == EDITION
    assert manifest["edition_sha256"] == _PINS[EDITION][1]
    assert manifest["reading"] == ex.READING


def test_every_ayah_is_present_even_with_no_spans(exported):
    """Absent and empty must stay distinguishable for a consumer."""
    manifest, rows = exported
    tb = TextBank.load(EDITION)
    assert set(rows) == {(r.surah, r.ayah) for r in tb.refs()}
    assert manifest["ayat"] == len(rows) == 6236
    assert manifest["ayat_without_spans"] == sum(1 for v in rows.values() if not v)


def test_only_registered_rules_appear(exported):
    _, rows = exported
    used = {s["rule"] for spans in rows.values() for s in spans}
    assert not used - {r.id for r in RULINGS}


def test_every_span_lies_inside_its_ayah(exported):
    _, rows = exported
    tb = TextBank.load(EDITION)
    bad = []
    for (surah, ayah), spans in rows.items():
        n = len(tb.ayah(AyahRef(surah, ayah)))
        for s in spans:
            if not 0 <= s["start"] <= s["end"] <= n:
                bad.append((surah, ayah, s))
    assert not bad, bad[:5]


def test_sample_matches_the_engine(exported):
    _, rows = exported
    tb = TextBank.load(EDITION)
    refs = sorted(tb.refs(), key=lambda r: (r.surah, r.ayah))[::STRIDE]
    assert len(refs) > 40
    for ref in refs:
        fresh = ex.spans_for_ayah(tb.ayah(ref), ref, EDITION)
        assert fresh == rows[(ref.surah, ref.ayah)], f"{ref} drifted"
