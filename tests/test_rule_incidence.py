"""The incidence gate: no registered ruling goes quietly dead.

`test_registry_complete.py` proves the register equals the engine as a set of
identifiers. It cannot see whether a rule still fires: an id that is present in
`src/`, cited, and covered by golden rows passes that gate whether it matches
the whole corpus or nothing at all.

So this gate measures. It counts every rule id over the corpus under one
declared reading protocol and holds the table frozen at
`tests/rule_incidence_frozen.json`, and it requires every id that fires nowhere
to say why in `tests/rule_incidence_reasons.json`. A silence with a stated
reason is a fact about the text or the protocol; a silence without one is a
rule that may have rotted, and the suite refuses it.

The counts themselves are frozen expectations, in the manner of
`test_stats_gate.py`: a change is a finding to investigate, never a tolerance
to widen.
"""
import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))

import export_incidence as inc  # noqa: E402

from quran_g2p.rules.registry import RULINGS  # noqa: E402

FROZEN = json.loads(inc.FROZEN.read_text(encoding="utf-8"))
REASONS = json.loads(inc.REASONS.read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def measured():
    counts, n_ayat = inc.measure()
    return counts, n_ayat


def test_frozen_table_covers_exactly_the_register():
    assert set(FROZEN["rules"]) == {r.id for r in RULINGS}


def test_protocol_is_recorded():
    # incidence without its reading protocol is not interpretable
    assert FROZEN["protocol"]["edition"] == inc.EDITION
    assert FROZEN["protocol"]["reading"] == inc.READING
    assert FROZEN["protocol"]["ayat"] == 6236


def test_counts_match_frozen(measured):
    counts, n_ayat = measured
    assert n_ayat == FROZEN["protocol"]["ayat"]
    live = {r.id: counts.get(r.id, {"phones": 0, "trace": 0, "ayahs": 0})
            for r in RULINGS}
    drifted = {rid: (FROZEN["rules"][rid], live[rid])
               for rid in live
               if {k: v for k, v in FROZEN["rules"][rid].items()
                   if k != "reason"} != live[rid]}
    assert not drifted, (
        "rule incidence moved; investigate before refreezing: "
        + ", ".join(sorted(drifted)))


def test_no_rule_fires_nowhere_without_a_stated_reason():
    silent = [rid for rid, e in FROZEN["rules"].items() if inc.is_silent(e)]
    unexplained = [rid for rid in silent if not REASONS.get(rid, "").strip()]
    assert not unexplained, (
        "these rules fire nowhere in the corpus and do not say why; a rule "
        "that has rotted looks exactly like this: " + ", ".join(unexplained))


def test_no_stale_reason_for_a_rule_that_does_fire():
    """A reason left behind after a rule came back to life is a lie in the file."""
    stale = [rid for rid in REASONS
             if rid in FROZEN["rules"] and not inc.is_silent(FROZEN["rules"][rid])]
    assert not stale, (
        "these rules now fire, so their silence reason is stale: "
        + ", ".join(sorted(stale)))


def test_every_reason_names_a_registered_rule():
    assert not set(REASONS) - {r.id for r in RULINGS}
