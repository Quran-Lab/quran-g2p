# Rule incidence: what actually fires, and what is entitled to be silent

`tests/test_registry_complete.py` proves the register and the engine are the
same set of identifiers: every id used in `src/` is registered, every
registered id is still used in `src/`, each carries a citation and golden
rows, and the manifest is append-only. That is a gate on *names*.

It cannot see whether a rule still fires. An id that sits in `src/`, cited and
covered, passes it whether the rule matches the whole corpus or nothing at
all, because nothing in the suite ever counted. A rule that has quietly
stopped matching looks exactly like a rule whose configuration the mushaf
happens never to present, and until now the repository had no way to tell the
two apart.

`tests/test_rule_incidence.py` counts.

## What is measured

`tools/export_incidence.py` reads every rule id off both channels a `RuleApp`
can reach: the provenance attached to a phone the rule changed, and the result
trace. Both are needed. A ruling whose content is that something does **not**
happen has no phone to hang off and reports itself only in the trace, so
counting provenance alone would make every such rule look dead. They are kept
apart in the table, and a rule is silent only when both are zero.

Incidence is meaningless without the reading it was measured under, so the
protocol is part of the frozen artifact:

> per-ayah, `WaqfSpec.ayah_end()`, default `HafsConfig()`; no
> `phonemize_concat`, no non-default wajh knobs.

The table lives at `tests/rule_incidence_frozen.json` and is generated. The
reasons live at `tests/rule_incidence_reasons.json` and are written by hand.
That is the only hand-edited half.

```sh
python tools/export_incidence.py            # rewrite the frozen table
python tools/export_incidence.py --check    # report drift, write nothing
```

## The rule

A zero is not a failure. A zero **without a stated reason** is.

Every id that fires nowhere must say why, and the gate refuses the table until
it does. A reason is a fact about the text, about the edition's dabt, or about
the protocol above. It is never a ruling, so nothing in that file is the
reviewer's business. The gate also rejects a reason left behind after a rule
comes back to life, because a stale reason is a false statement sitting in the
repository looking like a true one.

## Where it stands

**62 rules. 48 fire. 14 do not, and all fourteen say why.**

The heaviest are `R180_TABEEI` (6,005 ayat), `R210_ISTILA` (5,245),
`R120_ISKAN` (4,782, trace-only) and `R130_WASL_ELISION` (4,749). The
lightest are the one-site rulings: `R202_QALQALAH_AKBAR`, `R220_ISHMAM`,
`R221_IMALA` and `R222_TASHEEL` each fire on exactly one ayah.

The fourteen silences fall into four classes.

| class | rules | why |
|---|---|---|
| second wajh, off by default | `R012B_DAAF_DAMM`, `R014B_ISTIFHAM_TASHEEL`, `R190B_SALASILA_ITHBAT`, `R190C_AATAANI_HADHF` | the config knob that selects them defaults to the preferred wajh |
| variant enumeration | `R123_RAWM`, `R123_ISHMAM`, `R220B_TAAMANNA_IKHTILAS` | emitted by `quran_g2p.variants`, which `phonemize()` does not call |
| ayah-to-ayah junction | `R132_MALIYAH_SAKT`, `R135_MEEM_ALLAH`, `R136_BASMALA_JOINS` | the junction does not exist in a per-ayah reading; the first two were verified to fire under `phonemize_concat` at 69:28-29 and 3:1-2, and the third is a structural refusal that a successful reading never carries |
| trigger absent from the text | `R013_ELIDED_WAW_LIYASUU`, `R110_BADAL_IBTIDA`, `R141_IDGHAM_GHUNNA_NAQIS`, `R141_IZHAR_MUTLAQ` | see below |

The fourth class is the only one where the absence had to be proved rather
than read off a config default, so each was checked against the text directly,
independently of the engine.

- **`R013_ELIDED_WAW_LIYASUU`** is not silent at all. It fires at 17:7 under
  the `kfgqpc` rasm and not under `tanzil`, whose text does not present the
  elided waw. It is silent in this table only because the frozen protocol
  reads `tanzil`.
- **`R110_BADAL_IBTIDA`** governs a sakin hamza after hamzat al-wasl at the
  start of a breath group. No ayah begins with that sequence in either pinned
  edition, 0 of 6,236 in both, so a per-ayah reading never opens on one. The
  sites the ruling governs are all mid-ayah, where the hamzat al-wasl elides.

## Two unreachable branches, found and fixed

The gate's first run found two registered ids that fired nowhere because a
neighbouring rule reached the case first. Neither was an output defect: the
recitation was correct in both, and only the cited id was wrong. Both are now
corrected in `_p6_p7_noon_meem`.

**`R141_IZHAR_MUTLAQ`.** In دنيا، بنيان، صنوان، قنوان the noon carries a
**marked** sukun (125 occurrences in `tanzil`, none bare), and the dabt gate
treats a marked sukun as the mushaf's general izhar witness, so it resolved
these as `R140_IZHAR` before the izhar-mutlaq branch was reached. But the
mushaf points those noons precisely *because* the ruling is izhar mutlaq, so
the gate now cites the specific ruling when the target is a same-word waw or
yeh. **125 phones moved from `R140_IZHAR` to `R141_IZHAR_MUTLAQ`**, across 119
ayat.

**`R141_IDGHAM_GHUNNA_NAQIS`.** Idgham bi-ghunna is kamil into noon and meem
and naqis into waw and yeh, and the engine already knew: the branch computed
`kamil` and geminated only the kamil targets. Only the cited id did not say
so, and the id that should have carried the naqis case sat on a segment-stage
trigger (a bare-sukun noon before a **shadda'd** waw or yeh) that occurs 0
times in either pinned edition. The phone stage now cites by target.
**2,430 phones moved from `R141_IDGHAM_GHUNNA` to
`R141_IDGHAM_GHUNNA_NAQIS`**, across 1,729 ayat.

Nothing was created or lost in either move: the totals are conserved and no
phone changed. `R140_IZHAR` went 1,717 to 1,592 and `R141_IDGHAM_GHUNNA` 3,649
to 1,219, and the two ids that fired nowhere now fire 125 and 2,430 times.
`artifacts/tokenizer_tj1/ayah_tokens.jsonl` is byte-identical in its body, so
the token labels are untouched; `rule_index.jsonl` and the span export carry
the new ids.

The unreachable segment-stage branch is left in place. It is harmless, its
comment documents the dabt case it was written for, and the id it cites is now
alive by the phone-stage path.

## The gate has discrimination

Two seeded mutations were run against it. Freezing a live rule as dead
(`R144_IKHFA`, 0/0/0) failed two tests: the count check and the unexplained
silence check. Removing one silent rule's reason failed the silence check
alone. A gate that cannot fail is the defect it is meant to catch.
