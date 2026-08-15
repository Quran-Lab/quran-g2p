"""Ordered rule pipeline and the append-only RuleId registry.

RuleIds are stable public identifiers: spec files, golden tests, provenance
chains, verdicts, and export artifacts all reference them. NEVER rename or
reuse an id; retired rules keep their id with a tombstone comment.
"""
from __future__ import annotations

from .base import Rule

#: Ordered pipeline. Populated phase by phase as rules land (P1 first).
PIPELINE: list[type] = []


def all_rule_ids() -> list[str]:
    return [rule.rule_id for rule in PIPELINE]


def register(rule_cls: type) -> type:
    """Class decorator: append a rule to the pipeline in declaration order."""
    if not isinstance(rule_cls, type):
        raise TypeError("register expects a class")
    for attr in ("rule_id", "spec", "phase"):
        if not hasattr(rule_cls, attr):
            raise TypeError(f"{rule_cls.__name__} missing {attr}")
    if rule_cls.rule_id in all_rule_ids():
        raise ValueError(f"duplicate rule_id {rule_cls.rule_id}")
    if PIPELINE and rule_cls.phase < PIPELINE[-1].phase:
        raise ValueError(
            f"{rule_cls.rule_id} phase {rule_cls.phase} declared after phase {PIPELINE[-1].phase}"
        )
    PIPELINE.append(rule_cls)
    return rule_cls
