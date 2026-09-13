# Attribution: why every phone is the way it is

Provenance exists to answer one question. Point at any phone the engine emits
and ask *why is it like that*, and the answer should be a list of rulings, each
with a citation and a review row behind it. If the answer is empty, the engine
is right by accident as far as anyone reading it can tell.

The incidence gate ([INCIDENCE.md](INCIDENCE.md)) proves no registered ruling
has gone quietly dead. It cannot prove that a ruling which *does* fire is
reachable from the output it produced. A rule can fire thousands of times, be
counted, pass every oracle, and still leave no mark on the phones it made.

Six thousand eight hundred and forty-four applications were doing exactly that.

## The contract

Every `RuleApp` now declares what it did to the stream, in a field with no
default, so a new rule cannot be written without deciding:

| effect | meaning | must attach to a phone |
|---|---|---|
| `emit` | caused phone(s) to exist | **yes** |
| `modify` | changed an existing phone's attributes | **yes** |
| `delete` | caused phone(s) not to exist | no, nothing to point at |
| `state` | ruled that something does not apply here | no, nothing to point at |

`tests/test_attribution.py` enforces it: every `emit` and `modify` application
must appear, **by object identity**, in the provenance of a phone in the
output. Identity and not equality, because two equal-but-distinct `RuleApp`
objects would satisfy an equality check while describing one application
recorded twice and attached once, which is one of the defects this found.

## What it found

Eight rules, 6,844 applications, changing the recitation and pointing at
nothing:

| rule | unattached | of total |
|---|---|---|
| `R133_R160_IDGHAM_KAMIL` | 5,326 | 6,958 |
| `R121_MADD_EWAD` | 911 | 911 |
| `R110_WASL_START` | 231 | 231 |
| `R112_STRIP_INITIAL_SHADDA` | 176 | 176 |
| `R122_TAA_MARBUTA_WAQF` | 122 | 122 |
| `R131_NOON_WIQAYA` | 46 | 46 |
| `R011_MUQATTAAT` | 30 | 30 |
| `R012_SEEN_SAD` | 2 | 2 |

Two causes, both structural rather than careless.

**The segment stage runs before any phone exists.** P1, P3 and P4 rules act on
segments, so there was nothing for them to attach to at the time they fired,
and the trace was the only place they could go. They now register against the
source span they act on, and `_emit` hands those applications to the phones it
produces from that span. Provenance flows segment to phone.

**Same-word idgham was marking nothing.** `R133_R160_IDGHAM_KAMIL` marked its
target only across a word boundary, so مِن رَّبِّهِم was attributed and the lam
shamsiyya of ٱلرَّحْمَٰنِ was not, though it is the same ruling. 76% of that rule's
applications were invisible. The target is now marked either way.

The clearest single case was 20:1. طه exists *only* because R011 spells the
letter names out, and not one of its phones said so; the alif cited
`R180_TABEEI`, a downstream generic. R011 now records one application per
letter it spells, keyed to that letter, because a single ayah-level record
cannot reach phones sitting at as many source spans as there are letters.

**All 6,844 now attach.** The remaining six unattached rules are `delete` and
`state`, which have nothing to point at by construction: an elided hamzat
al-wasl, a haraka removed at waqf, a taa that does not qalqalah.

## Where it stands

**62 rules. 44 attach to phones. 6 are delete or state. 12 are silent, each
with a stated reason.**

## The other gates

**Totality.** A phone that deviates from a plain decode must carry a rule from
the phase that owns the deviation. A ghunna with no P9 ruling behind it or a
qalqalah with no P11 ruling is an unexplained fact about the recitation.
Gemination and length are deliberately out of scope: the shadda is written in
the mushaf, so gemination is a fact about the text rather than a ruling over
it, and every madd carries a length by construction.

Tafkheem gets its own narrower gate, because vowels and madds *inherit* it from
their host consonant (R213) and so carry no ruling of their own. The claim
made is the true one: a mofakham **consonant** names its P12 ruling.

**Exclusivity.** No two rules that compete for the same trigger may both claim
one site. Every sakin noon and every tanween has exactly one ruling. Measured
over the corpus: **zero clashes**.

**Specificity.** The incidence gate catches a rule that fires *nowhere*. It is
blind to a rule that fires while a more general rule eats cases belonging to a
more specific one, because the general rule's count stays healthy and nothing
looks wrong. That is precisely how `R141_IZHAR_MUTLAQ` sat at zero while its
ruling was applied under `R140_IZHAR`. Two regression guards now hold the pair
that bit, and the pair that bit beside it: a same-word noon before waw or yeh
must cite izhar mutlaq, and idgham with ghunna must be cited kamil into noon
and meem and naqis into waw and yeh, never the other way round.

**Ordering.** A phone's provenance is in pipeline order, so it reads as a
history rather than a bag. One documented exemption: `R132_SAKT` is registered
in P5 as a junction ruling and applied in the one-off phase, so on the two ayat
where a sakt lands on a phone a later rule already touched, it arrives out of
order. The ruling is a junction ruling and the implementation is late; both are
deliberate, and moving either would change what the engine emits. Recorded
rather than silently allowed.

**Both channels hold the same register.** Nothing exists in the trace that the
phones and the recorded events together cannot account for. This is what lets
`rule_index.jsonl` be complete.

## What changed in the artifacts

`artifacts/tokenizer_tj1/rule_index.jsonl` read phone provenance only, so it
carried **37 of 50** live rules and silently dropped pausal iskan across 4,782
ayat. It now carries **50 of 50**: the attached rules on their phones, and the
`delete` and `state` rulings as a per-ayah `events` array with the span each
acted on. **22,982 events** that no consumer could previously see.

Token labels are untouched. `ayah_tokens.jsonl` is byte-identical in its body;
the rulings moved, not the recitation.

## The gates have discrimination

Four seeded mutations, each caught by the gate meant to catch it:

| mutation | caught by |
|---|---|
| same-word idgham stops marking its target | the contract, and the idgham regression guard |
| qalqalah set with no ruling behind it | totality |
| the general izhar swallows izhar mutlaq | the specificity guard |
| kamil and naqis cited the wrong way round | the kamil/naqis guard |

## What is not claimed

The trace records *that* a rule applied and *what kind* of change it made. It
does not record the payload, the before and after values, so the phone stream
cannot be **replayed** from the record alone. Replay is the one property that
would make attribution provably rather than demonstrably complete, and it would
mean carrying a before/after on every application. That is a real cost in a
trace that already runs to tens of thousands of entries per surah, and it is
not paid here. What is proved is narrower and still worth stating: every ruling
that changes the recitation names the phone it changed, every deviation names
the ruling that caused it, and no ruling is shadowed by a more general one.
