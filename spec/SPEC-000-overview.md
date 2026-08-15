# SPEC-000 — Overview and Method

Status: normative. Version: 0.1-draft (2026-08-15).

## What this project is

A clean-room, spec-first grapheme-to-phoneme engine for Quran recitation,
**Hafs 'an 'Asim via tariq al-Shatibiyyah only**, feeding a streaming zipformer
phoneme-CTC ASR system with "full tajweed tokens" (length-tagged letter-group
tokens), MFA lexica, and tajweed grading artifacts.

The spec directory is the product. Code implements the spec; tests enforce it;
anything not in the spec is not a behavior.

## Layering

1. **Input contract** (SPEC-001): pinned text editions, codepoint censuses,
   fail-closed loading.
2. **Orthographic decode** (SPEC-002): per-edition decoding of rasm + dabt into
   one shared token IR. Everything downstream is edition-independent; the
   editions become mutual oracles (cross-edition IR-equality invariant).
3. **Phonological derivation** (SPEC-1xx..9xx): ordered rule phases over typed
   IR — waqf segmentation first, then ibtida'/pausal forms, junction rules,
   noon/meem/idgham families, madd classification with precedence, qalqalah,
   tafkheem, Hafs one-offs, sifat projection.
4. **Representation** (SPEC-003): `Phone` records separating PRESCRIPTION
   (set-valued lengths: `allowed` = Shatibiyyah-legal, `scoring` = attested,
   `canonical` = deterministic default) from OBSERVATION (`realized_len`,
   filled only by forced alignment downstream). Full rule provenance chains and
   source-char coverage on every output.
5. **Exports** (sibling plan): token vocabulary, lexicon, rule index — outside
   this spec, behind `export_iface.py`.

## Method (the rigor rules)

- **TDD without exception**: no production code without a failing test first.
- **No hand-typed Arabic anywhere**: all Arabic codepoints live in generated
  `codepoints.py`; a structural test bans Arabic literals elsewhere.
- **Clean room**: `src/` never imports the reference-engine package or the `oracle/` quarantine;
  a structural test enforces it. Oracles (the reference engine `quran_transcript`, the local
  `quran-phones` wrapper, cpfair/quran-tajweed spans, the mushaf's own dabt
  layer, the editions against each other) are compared against, never copied.
- **Citations or CONVENTION tags** on every normative sentence. CONVENTION
  marks representation choices where disagreement with an oracle is not a
  correctness question.
- **Verdict-gated differentials**: every disagreement cluster gets a recorded
  verdict (our-bug / their-bug / legitimate-variant / representation-diff);
  nothing is averaged away. Agreement percentages are informational only.
- **Ambiguity is surfaced, never hidden**: free-choice madd lengths are sets;
  waqf position is an input; pausal variants are enumerated.

## Known trust boundaries (from the 2026-08-15 audit)

- muaalem "gold" labels are ~98% machine output of `quran_transcript` (same
  author) — drift-check corpus only, never truth.
- `qdat_bench` (HF) is a downstream-maintained subset of the original QDAT (IJASAT
  ~2021; three rules annotated "by expert", no protocol published). Its three
  original-provenance columns outrank its five unknown-provenance columns;
  the whole dataset is diagnostic-only, never a gate.
- The legacy "2.32% G2P ceiling" is a contaminated upper bound (machine gold +
  canonical fill-in + real reciter variance); to be re-measured decomposed.
