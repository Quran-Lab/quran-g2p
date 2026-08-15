"""Rule registry: stable, append-only RuleIds and ordered phases.

The registry is what spec files, golden tests, provenance chains, and exports
all key off. Its discipline is tested: unique ids, naming pattern, phase
ordering monotonic in the pipeline, and (once golden tests exist) every rule
covered by at least one golden — that completeness test lands with the goldens.
"""
import re

from quran_g2p.rules.registry import PIPELINE, all_rule_ids


def test_rule_ids_unique():
    ids = all_rule_ids()
    assert len(ids) == len(set(ids))


def test_rule_ids_follow_naming_pattern():
    pat = re.compile(r"^R\d{3}[A-Z0-9_]*$")
    for rid in all_rule_ids():
        assert pat.match(rid), rid


def test_pipeline_phase_order_is_monotonic():
    phases = [rule.phase for rule in PIPELINE]
    assert phases == sorted(phases)


def test_every_rule_declares_spec():
    for rule in PIPELINE:
        assert rule.spec.startswith("SPEC-"), rule.rule_id
