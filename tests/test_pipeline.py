"""Pipeline driver: R000 codepoint audit -> clustering -> ordered rule phases.

With no rules registered yet, run() must still: reject codepoints outside the
edition's frozen census (fail-closed), produce the cluster stream, and carry
an empty trace. Determinism (same input -> identical output) is asserted here
at the skeleton level and becomes a corpus invariant later.
"""
import pytest

from quran_g2p import codepoints as cp
from quran_g2p.pipeline import UnknownCodepointError, run
from quran_g2p.textbank import AyahRef, TextBank


def test_run_clusters_real_ayah():
    tb = TextBank.load("tanzil")
    ctx = run(tb.ayah(AyahRef(1, 1)), edition="tanzil")
    assert len(ctx.clusters) > 10
    assert ctx.trace == []
    assert ctx.edition == "tanzil"


def test_run_rejects_codepoint_outside_edition_census():
    # LATIN 'x' is in no census; a KFGQPC-only codepoint must also fail under tanzil.
    with pytest.raises(UnknownCodepointError):
        run("x", edition="tanzil")
    with pytest.raises(UnknownCodepointError):
        run(cp.BEH + cp.SMALL_HIGH_DOTLESS_HEAD_OF_KHAH, edition="tanzil")


def test_run_is_deterministic():
    tb = TextBank.load("kfgqpc")
    text = tb.ayah(AyahRef(2, 255))
    assert run(text, edition="kfgqpc") == run(text, edition="kfgqpc")
