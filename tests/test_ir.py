"""Phone IR: the prescription/observation split, provenance, and coverage.

These types are the engine's output contract (SPEC-003). The invariants tested
here are the ones later phases lean on: set-valued prescriptions with a legal
canonical, observation slot empty at construction, madd phones always carrying
a LengthSpec, and coverage that tiles the source exactly.
"""
import pytest

from quran_g2p.ir import (
    Base,
    CoverageError,
    CoverageMap,
    DeleteReason,
    LengthSpec,
    Phone,
    RuleApp,
)


def lspec_free(allowed, canonical, scoring=None):
    return LengthSpec(
        kind="free",
        allowed=frozenset(allowed),
        canonical=canonical,
        scoring=frozenset(scoring if scoring is not None else allowed),
    )


def test_lengthspec_fixed_must_have_single_allowed():
    ok = LengthSpec(kind="fixed", allowed=frozenset({2}), canonical=2, scoring=frozenset({2}))
    assert ok.canonical == 2
    with pytest.raises(ValueError):
        LengthSpec(kind="fixed", allowed=frozenset({2, 4}), canonical=2, scoring=frozenset({2, 4}))


def test_lengthspec_canonical_must_be_allowed():
    with pytest.raises(ValueError):
        lspec_free({4, 5}, canonical=6)


def test_lengthspec_allowed_must_be_subset_of_scoring():
    with pytest.raises(ValueError):
        LengthSpec(kind="free", allowed=frozenset({4, 5}), canonical=4, scoring=frozenset({4}))
    ok = LengthSpec(kind="free", allowed=frozenset({4, 5}), canonical=4, scoring=frozenset({2, 3, 4, 5, 6}))
    assert 2 in ok.scoring and 2 not in ok.allowed


def _phone(**kw):
    defaults = dict(
        base=Base.NOON,
        kind="consonant",
        geminated=False,
        length=None,
        ghunna=None,
        qalqalah=None,
        tafkheem="moraqaq",
        sakt_after=False,
        pausal_role=None,
        provenance=(),
        src_span=(0, 1),
        word_index=0,
    )
    defaults.update(kw)
    return Phone(**defaults)


def test_madd_phone_requires_lengthspec():
    with pytest.raises(ValueError):
        _phone(base=Base.ALEF_MADD, kind="madd", length=None)
    p = _phone(base=Base.ALEF_MADD, kind="madd", length=lspec_free({4, 5}, 4))
    assert p.length.canonical == 4


def test_realized_len_is_always_none_at_construction():
    p = _phone()
    assert p.realized_len is None
    with pytest.raises(TypeError):
        Phone(  # realized_len is not a constructor parameter at all
            base=Base.NOON, kind="consonant", geminated=False, length=None,
            ghunna=None, qalqalah=None, tafkheem="moraqaq", sakt_after=False,
            pausal_role=None, provenance=(), src_span=(0, 1), word_index=0,
            realized_len=2.0,
        )


def test_phone_is_immutable():
    p = _phone()
    with pytest.raises(Exception):
        p.geminated = True


def test_provenance_chain_preserved_in_order():
    r1 = RuleApp(rule_id="R143_IQLAB", spec="SPEC-143", trigger_span=(3, 5))
    r2 = RuleApp(rule_id="R170_GHUNNA", spec="SPEC-170", trigger_span=(3, 5))
    p = _phone(provenance=(r1, r2))
    assert [r.rule_id for r in p.provenance] == ["R143_IQLAB", "R170_GHUNNA"]


def test_coverage_tiles_source_exactly():
    cov = CoverageMap(text_len=4)
    cov.consume(0, phone_index=0)
    cov.consume(1, phone_index=0)
    cov.delete(2, DeleteReason.SILENT_CIRCLE, rule_id="R013")
    with pytest.raises(CoverageError):
        cov.verify_complete()  # index 3 untouched
    cov.consume(3, phone_index=1)
    cov.verify_complete()


def test_coverage_rejects_double_claims():
    cov = CoverageMap(text_len=2)
    cov.consume(0, phone_index=0)
    with pytest.raises(CoverageError):
        cov.delete(0, DeleteReason.KASHEEDA, rule_id="R010")
