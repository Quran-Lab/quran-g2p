"""Pipeline driver: R000 codepoint audit -> clustering -> ordered rule phases.

The census loaded here is the frozen per-edition census from data/ — the same
file the audit tests pin. A codepoint outside it is an input-contract breach
and fails closed before any rule can misread it (R000, SPEC-001).
"""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from functools import lru_cache
from pathlib import Path

from .cluster import Cluster, cluster
from .config import HafsConfig
from .decode import decode
from .ir import RuleApp
from .ortho import OrthoSeg
from .textbank import AyahRef
from .rules.registry import PIPELINE
from .rules import p1_orthography  # noqa: F401  (registers P1 rules)

_REPO_DATA = Path(__file__).resolve().parents[2] / "data"


class UnknownCodepointError(Exception):
    """Input contains a codepoint outside the edition's frozen census (R000)."""


@lru_cache(maxsize=None)
def _census_keys(edition: str) -> frozenset[str]:
    path = _REPO_DATA / f"census-{edition}.json"
    return frozenset(json.loads(path.read_text(encoding="utf-8")))


@dataclass
class PipelineCtx:
    edition: str
    text: str
    clusters: list[Cluster]
    segs: list[OrthoSeg] = field(default_factory=list)
    ref: AyahRef | None = None
    config: HafsConfig = field(default_factory=HafsConfig)
    trace: list[RuleApp] = field(default_factory=list)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, PipelineCtx):
            return NotImplemented
        return (
            self.edition == other.edition
            and self.text == other.text
            and self.clusters == other.clusters
            and self.segs == other.segs
            and self.ref == other.ref
            and self.trace == other.trace
        )


def run(text: str, edition: str, ref: AyahRef | None = None,
        config: HafsConfig | None = None) -> PipelineCtx:
    # R000: codepoint audit, fail closed.
    census = _census_keys(edition)
    for i, ch in enumerate(text):
        if f"{ord(ch):04X}" not in census:
            raise UnknownCodepointError(
                f"U+{ord(ch):04X} at index {i} is not in the {edition!r} census"
            )
    # R001: grapheme clustering (validates mark stacks).
    ctx = PipelineCtx(edition=edition, text=text, clusters=cluster(text), ref=ref,
                      config=config or HafsConfig())
    # P1 decode: clusters -> OrthoSeg stream.
    ctx.segs = decode(ctx.clusters, edition, text).segs
    # Ordered rule phases.
    for rule_cls in PIPELINE:
        rule_cls().apply(ctx)
    return ctx
