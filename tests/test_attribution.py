"""Attribution: every ruling that changes the recitation points at what it changed.

The incidence gate (`test_rule_incidence.py`) proves no registered ruling has
gone quietly dead. It cannot prove that a ruling which *does* fire is reachable
from the output it produced. A rule can fire thousands of times, be counted,
pass every oracle, and still leave no mark on the phones it made, in which case
nothing downstream can answer the only question provenance exists to answer:
**why is this phone the way it is?**

Three gates here, in increasing strength.

1. **The contract.** `RuleApp.effect` declares what an application did to the
   stream. An `emit` or a `modify` MUST appear, by object identity, in the
   provenance of a phone in the output. `delete` and `state` have nothing to
   point at by construction and are anchored by `trigger_span` alone.

2. **Totality.** A phone whose attributes deviate from a plain decode must
   carry a rule from the phase that owns that attribute. A ghunna with no P9
   rule behind it, or a qalqalah with no P11 rule, is an unexplained fact about
   the recitation, and the suite refuses it.

3. **Anchoring.** Every application's `trigger_span` must lie inside the ayah
   it was produced from, so the record can always be pointed back at the text.

Identity, not equality, is what the contract is checked with. Two equal-but-
distinct `RuleApp` objects would satisfy an equality check while describing one
application recorded twice and attached once, which is the exact defect this
gate exists to catch.
"""
import pytest

from quran_g2p.ir import Base
from quran_g2p.phonemize import phonemize
from quran_g2p.textbank import TextBank

EDITION = "tanzil"
EMIT = "EMIT"

#: Phone attribute -> the rule-id prefixes entitled to explain it. A deviation
#: from the plain decode is explained by the phase that owns the attribute.
ATTRIBUTE_OWNERS = {
    "ghunna": ("R141", "R142", "R143", "R144", "R150", "R151", "R170", "R140"),
    "qalqalah": ("R200", "R201", "R202"),
    "sakt_after": ("R132",),
}


@pytest.fixture(scope="module")
def corpus():
    tb = TextBank.load(EDITION)
    out = []
    for ref in tb.refs():
        out.append((ref, phonemize(tb.ayah(ref), edition=EDITION, ref=ref)))
    return out


def _attached_ids(result):
    return {id(a) for seg in result.segments for p in seg.phones
            for a in p.provenance}


def test_every_emit_and_modify_reaches_a_phone(corpus):
    """The contract. A ruling that changes the stream must say what it changed."""
    orphans = []
    for ref, result in corpus:
        attached = _attached_ids(result)
        for app in result.trace:
            if app.rule_id == EMIT or app.effect not in ("emit", "modify"):
                continue
            if id(app) not in attached:
                orphans.append((f"{ref.surah}:{ref.ayah}", app.rule_id,
                                app.effect, app.trigger_span))
    assert not orphans, (
        f"{len(orphans)} applications changed the recitation and point at no "
        f"phone; first five: {orphans[:5]}")


def test_delete_and_state_carry_a_position(corpus):
    """They cannot attach, so the span is the whole of their anchoring."""
    unanchored = []
    for ref, result in corpus:
        for app in result.trace:
            if app.effect not in ("delete", "state"):
                continue
            lo, hi = app.trigger_span
            if not (0 <= lo <= hi):
                unanchored.append((f"{ref.surah}:{ref.ayah}", app.rule_id,
                                   app.trigger_span))
    assert not unanchored, unanchored[:5]


def test_every_application_is_anchored_in_its_ayah(corpus):
    tb = TextBank.load(EDITION)
    bad = []
    for ref, result in corpus:
        n = len(tb.ayah(ref))
        for app in result.trace:
            lo, hi = app.trigger_span
            if not (0 <= lo <= hi <= n):
                bad.append((f"{ref.surah}:{ref.ayah}", app.rule_id,
                            app.trigger_span, n))
    assert not bad, bad[:5]


def test_no_deviating_attribute_is_unexplained(corpus):
    """Totality: a phone that deviates from a plain decode names the phase
    responsible. Gemination and length are deliberately out of scope here:
    gemination is written in the mushaf itself (shadda) and is therefore a fact
    about the text rather than a ruling over it, and every madd carries a
    length by construction of `Phone.__post_init__`."""
    unexplained = []
    for ref, result in corpus:
        for seg in result.segments:
            for p in seg.phones:
                prefixes = {a.rule_id[:4] for a in p.provenance
                            if a.rule_id != EMIT}
                for attr, owners in ATTRIBUTE_OWNERS.items():
                    value = getattr(p, attr)
                    if not value:          # None or False: no deviation
                        continue
                    if not prefixes & set(owners):
                        unexplained.append(
                            (f"{ref.surah}:{ref.ayah}", p.base.value, attr,
                             value, sorted(prefixes)))
    assert not unexplained, (
        f"{len(unexplained)} phones deviate from a plain decode with no rule "
        f"from the owning phase; first five: {unexplained[:5]}")


def test_tafkheem_on_an_emphatic_phone_is_explained(corpus):
    """Tafkheem has its own gate: it is set on far more phones than it is ruled
    on, because vowels and madds INHERIT it from their host consonant (R213).
    An inheriting phone carries no rule of its own, so the claim here is the
    narrower true one: a mofakham CONSONANT names its P12 ruling."""
    unexplained = []
    for ref, result in corpus:
        for seg in result.segments:
            for p in seg.phones:
                if p.kind != "consonant" or p.tafkheem == "moraqaq":
                    continue
                if not any(a.rule_id.startswith("R21") for a in p.provenance):
                    unexplained.append((f"{ref.surah}:{ref.ayah}",
                                        p.base.value, p.tafkheem))
    assert not unexplained, unexplained[:5]


def test_muqattaat_phones_name_the_rule_that_created_them(corpus):
    """20:1 is the whole case in one ayah: طه exists only because R011 spelled
    the letter names out. Before the contract existed, not one of its phones
    said so."""
    (_, result), = [(r, x) for r, x in corpus if (r.surah, r.ayah) == (20, 1)]
    phones = result.segments[0].phones
    assert phones, "20:1 produced no phones"
    for p in phones:
        assert any(a.rule_id == "R011_MUQATTAAT" for a in p.provenance), (
            f"{p.base.value} in 20:1 does not name R011_MUQATTAAT")


def test_idgham_kamil_marks_its_target_within_a_word_too(corpus):
    """The lam of ٱلرَّحْمَٰنِ assimilates into the reh exactly as مِن رَّبِّهِم does.
    Same-word applications were once recorded and never attached."""
    tb = TextBank.load(EDITION)
    from quran_g2p.textbank import AyahRef
    ref = AyahRef(1, 1)
    result = phonemize(tb.ayah(ref), edition=EDITION, ref=ref)
    marked = [p for p in result.segments[0].phones
              if any(a.rule_id == "R133_R160_IDGHAM_KAMIL" for a in p.provenance)]
    assert marked, "1:1 has lam shamsiyya and no phone names the ruling"
    assert all(p.geminated or p.base is Base.REH for p in marked)


# --- Specificity and ordering ---------------------------------------------
#
# The incidence gate catches a rule that fires NOWHERE. It is blind to a rule
# that fires, but where a more general rule eats cases that belong to a more
# specific one: the general rule's count stays healthy and nothing looks wrong.
# That is exactly how R141_IZHAR_MUTLAQ and R141_IDGHAM_GHUNNA_NAQIS sat at
# zero while the rulings they carry were being applied under another id.
#
# Two properties close it. Exclusivity: no two rules that compete for the same
# trigger may both claim one site. Specificity: where the general rule fired,
# the specific rule's own precondition must not hold.

#: Every ruling that competes for a sakin noon or a tanween.
P6_FAMILY = {
    "R140_IZHAR", "R140_IZHAR_HALQI", "R141_IDGHAM_GHUNNA",
    "R141_IDGHAM_GHUNNA_NAQIS", "R141_IZHAR_MUTLAQ",
    "R142_IDGHAM_BILA_GHUNNA", "R143_IQLAB", "R144_IKHFA",
}

#: R132_SAKT is registered in P5 (junction) and applied in the one-off phase,
#: so it legitimately lands after later-phase rules on the two ayat where a
#: sakt sits on a phone another rule already touched. The ruling is a junction
#: ruling and the implementation is late; both are deliberate, and moving
#: either would change what the engine emits. Recorded, not silently allowed.
ORDER_EXEMPT = {"R132_SAKT"}

PHASE_ORDER = {f"P{i}": i for i in range(1, 15)}


def _phase_ordinal(rule_id):
    from quran_g2p.rules.registry import PHASE_BY_PREFIX
    return PHASE_ORDER.get(PHASE_BY_PREFIX.get(rule_id[:3]), -1)


def test_no_two_competing_rules_claim_one_trigger(corpus):
    """Exclusivity. A sakin noon has exactly one ruling, never two."""
    clashes = []
    for ref, result in corpus:
        by_span = {}
        for a in result.trace:
            if a.rule_id in P6_FAMILY:
                by_span.setdefault(a.trigger_span, set()).add(a.rule_id)
        for span, rules in by_span.items():
            if len(rules) > 1:
                clashes.append((f"{ref.surah}:{ref.ayah}", span, sorted(rules)))
    assert not clashes, clashes[:5]


def test_provenance_reads_as_a_history(corpus):
    """A phone's provenance is in pipeline order, so it can be read as the
    sequence of things that happened to it rather than an unordered bag."""
    bad = []
    for ref, result in corpus:
        for seg in result.segments:
            for p in seg.phones:
                ids = [a.rule_id for a in p.provenance
                       if a.rule_id != EMIT and a.rule_id not in ORDER_EXEMPT]
                phases = [x for x in map(_phase_ordinal, ids) if x >= 0]
                if phases != sorted(phases):
                    bad.append((f"{ref.surah}:{ref.ayah}", p.base.value, ids))
    assert not bad, bad[:5]


def test_izhar_mutlaq_is_not_eaten_by_the_general_izhar(corpus):
    """Specificity guard, regression. A same-word noon before waw or yeh IS
    izhar mutlaq; the dabt gate must not resolve it as the general R140."""
    from quran_g2p.textbank import AyahRef
    tb = TextBank.load(EDITION)
    ref = AyahRef(2, 85)                       # ٱلدُّنْيَا
    result = phonemize(tb.ayah(ref), edition=EDITION, ref=ref)
    phones = result.segments[0].phones
    for i, p in enumerate(phones):
        if p.base is not Base.NOON or p.ghunna != "asl":
            continue
        nxt = phones[i + 1] if i + 1 < len(phones) else None
        same_word = nxt is not None and nxt.word_index == p.word_index
        if same_word and nxt.base in (Base.WAW, Base.YEH):
            cited = {a.rule_id for a in p.provenance}
            assert "R141_IZHAR_MUTLAQ" in cited, (
                f"2:85 noon before a same-word {nxt.base.value} cites {cited}")


def test_idgham_ghunna_is_kamil_or_naqis_by_target(corpus):
    """Specificity guard, regression. Into noon or meem the idgham is kamil and
    the target geminates; into waw or yeh it is naqis and it does not. The two
    must never be cited the other way round."""
    wrong = []
    for ref, result in corpus:
        for seg in result.segments:
            for p in seg.phones:
                cited = {a.rule_id for a in p.provenance}
                kamil = "R141_IDGHAM_GHUNNA" in cited
                naqis = "R141_IDGHAM_GHUNNA_NAQIS" in cited
                if not (kamil or naqis):
                    continue
                if kamil and p.base not in (Base.NOON, Base.MEEM):
                    wrong.append((f"{ref.surah}:{ref.ayah}", "kamil", p.base.value))
                if naqis and p.base in (Base.NOON, Base.MEEM):
                    wrong.append((f"{ref.surah}:{ref.ayah}", "naqis", p.base.value))
    assert not wrong, wrong[:5]


def test_the_two_channels_hold_the_same_register(corpus):
    """Nothing may exist in the trace that the phones and the recorded events
    together cannot account for. This is what lets `rule_index.jsonl` be built
    from provenance plus delete/state events and still be complete."""
    for ref, result in corpus:
        traced = {a.rule_id for a in result.trace if a.rule_id != EMIT}
        attached = {a.rule_id for seg in result.segments for p in seg.phones
                    for a in p.provenance if a.rule_id != EMIT}
        eventful = {a.rule_id for a in result.trace
                    if a.effect in ("delete", "state") and a.rule_id != EMIT}
        missing = traced - attached - eventful
        assert not missing, f"{ref.surah}:{ref.ayah}: {sorted(missing)}"
