"""Rule protocol: pure transformations over the typed stream.

A rule is a class with three class-level declarations (rule_id, spec, phase)
and an `apply` that transforms a PipelineCtx. Rules never see raw strings —
they pattern-match typed clusters/segments/phones. String regex is banned in
src/ (the oracle's central fragility; see SPEC-000).
"""
from __future__ import annotations

from typing import ClassVar, Protocol, runtime_checkable


@runtime_checkable
class Rule(Protocol):
    rule_id: ClassVar[str]
    spec: ClassVar[str]
    phase: ClassVar[int]

    def apply(self, ctx: "PipelineCtx") -> None:  # noqa: F821 (defined in pipeline.py)
        ...
