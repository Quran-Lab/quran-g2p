# SPEC-001 — Input Contract: Editions, Pins, Censuses

Status: normative. Version: 0.1-draft (2026-08-15).

## Editions

| id | file | sha256 | source | role |
|---|---|---|---|---|
| `tanzil` | `data/tanzil-uthmani.txt` | `bf4f57b9…3312c8` | tanzil.net official download (Uthmani, no pause marks) | authoritative input |
| `kfgqpc` | `data/kfgqpc-hafsData_v18.json` | `5d8bb917…0ba140` | KFGQPC Hafs v18 via github thetruetruth/quran-data-kfgqpc | cross-check + richer dabt oracle |
| (reference-engine packaged text) | inside `quran_transcript` site-packages | not pinned here | Tanzil-lineage variant | oracle-quarantine only, cross-check #3 |

Loading is fail-closed: SHA-256 mismatch raises `PinnedTextError` (tested,
including a tamper test). Both editions load to exactly **6,236 ayat**.
KFGQPC `aya_text` carries a trailing NBSP + Arabic-Indic ayah number, stripped
at load (tested).

## Censuses (frozen; drift = hard error)

`data/census-tanzil.json` (62 distinct codepoints) and
`data/census-kfgqpc.json` (73 distinct codepoints) are frozen recomputable
snapshots; `verify_corpus_census` re-derives and compares exactly (tested,
including a drift test). `codepoints.py` is generated from the census union
(76 constants) by `tools/gen_codepoints.py`.

### Anchor counts agreeing across Tanzil and the reference-engine-reported census

| codepoint | meaning | count | sites |
|---|---|---|---|
| U+06E3 small low seen | seen-for-saad reading mark | 1 | 52:37 |
| U+06E8 small high noon | nun ikhtilas mark | 1 | 21:88 |
| U+06EA empty centre low stop | imala mark | 1 | 11:41 |
| U+06EB empty centre high stop | ishmam mark (Tanzil only) | 1 | 12:11 |
| U+06EC rounded high filled stop | tasheel mark (Tanzil ×1; KFGQPC ×2 — see deltas) | 1–2 | 41:44 (+12:11 in KFGQPC, to verify) |
| U+06DC small high seen | seen-over-saad | 2 (Tanzil) / 8 (KFGQPC, to verify) | 2:245, 7:69, … |
| U+06DF small high rounded zero | silent letter (sukun mustadeer) | 3,988 | — |
| U+06E0 small high upright rectangular zero | sukun mustateel (wasl-silent alif) | 66 | — |
| U+0653 maddah above | madd sign | 5,376 (Tanzil) / 5,652 (KFGQPC) | — |

## Inter-edition deltas (load-bearing; P1 decoders must own each)

1. **Pronounced sukun**: Tanzil U+0652 ×37,372 ↔ KFGQPC U+06E1 ×37,148
   (delta 224 to be explained during P1 — candidate: idgham/ikhfa letters that
   KFGQPC leaves bare vs Tanzil sukun conventions).
2. **Silent letters**: Tanzil U+06DF ×3,988 ↔ KFGQPC U+0652 ×3,988 (EXACT
   match — KFGQPC repurposes the plain-sukun glyph as the silent circle).
3. **Tanween split** (KFGQPC encodes tajweed state in the tanween form —
   richer within-text oracle):
   - izhar/pause forms: U+064B ×734, U+064C ×578, U+064D ×599
   - open (idgham/ikhfa) forms, interpretation TO VERIFY in P1: U+065E
     (fatha two dots) ×1,807, U+0657 (inverted damma) ×2,901, U+0656
     (subscript alef) ×1,935
   - Tanzil instead: unified U+064B/C/D ×8,893 total + markers U+06E2 ×510 /
     U+06ED ×99.
4. **Iqlab/dabt meem markers**: Tanzil 06E2×510 / 06ED×99; reference-engine-packaged text
   reportedly 06E2×2,445 / 06ED×4,807 — that packaged text is a HIGHER-dabt-density
   variant, not plain Tanzil. Differential adapter must not assume identical
   marker semantics.
5. **KFGQPC extras**: waqf pause marks U+06D6–06DB (~4,272 sites — future input
   to WaqfSpec sampling), sajdah U+06E9 ×15, rub-el-hizb U+06DE ×199 (+ paired
   NBSP ×199 retained in text — decoder deletes with reason ORNAMENT),
   hamza-below U+0655 ×14, small high madda U+06E4 ×26.
6. **Rasm encoding**: alef maksura U+0649 Tanzil ×6,603 vs KFGQPC ×2,913;
   yaa U+064A 18,334 vs 21,925 — different dotless-yaa conventions; the P1
   alif-maksura rule (R016) must be edition-aware.
7. **Ishmam mark**: U+06EB absent from KFGQPC (their 12:11 encoding to verify
   when implementing R220).

## Corpus findings incorporated into the loaders/decoders (2026-08-15)

1. **Tanzil embeds the basmala** in every surah-initial ayah except 1:1 and
   9:1; the loader strips it (rasm-skeleton match on the first word, exact on
   the rest). Two embedded basmalas carry cross-unit wasl dabt on their beh:
   **95:1 and 97:1** (preceding surahs end in ب — فَٱرْغَب, وَٱقْتَرِب —
   mutamathilayn idgham written on the basmala). The Tanzil census is
   computed post-strip.
2. **Tanzil writes consonant yaa dotless**: alef maksura with any vowel state
   is a consonant YEH (شَىْءٍ, هِىَ, أَىِّ) — explains maksura 6,603 vs
   KFGQPC 2,913.
3. **KFGQPC tatweel carries the previous letter's marks** (كـَلَّا kaf-fatha
   on the kasheeda, 33 kalla-class sites); tatweel is a transparent mark in
   the cluster model.
4. **KFGQPC iqlab** = single haraka + small meem (Tanzil: tanween + small
   meem); both canonicalize to Tanween(quality, IQLAB).
5. **KFGQPC hamza-seat + madda** (أٓ) ≡ Tanzil ءَا (hamza+fatha+alef).
6. **KFGQPC leen letters left bare before cross-word idgham** (عَصَوا۟ وَّ);
   bare-equals-assimilated extends to leen waw/yeh.
7. **Seat letters before combining hamza are silent** (KFGQPC تِلۡقَآيِٕ).
8. **Word-initial bare yeh** occurs exactly twice — the muqatta'at names in
   19:1 and 36:1 (R011 owns the spell-out).

## Cross-edition equality invariant — verdicted exceptions

`tests/test_cross_edition.py` enforces decoded-seg equality over all 6,236
ayat with tanween mode compared as tanween-vs-iqlab only (KFGQPC izhar/open
forms are a dabt witness for P6, not a P1 axis). Enumerated exceptions, each
verdict **legitimate-variant**:

| ref | difference | verdict note |
|---|---|---|
| 15:7 | لَّوْ مَا (Tanzil, split) vs لَوۡمَا (KFGQPC, joined) | word_index shift only; seg content identical |
| 27:20, 36:22 | مَا لِىَ vs مَالِيَ | same class |
| 17:7 | لِيَسُوٓءُوا hamza-seat rasm: Tanzil seen-u,madd-u,hamza-u,madd-u vs KFGQPC seen-u,hamza-u,madd-u | genuine rasm variant; phonetic resolution deferred to madd classification + differential + expert review; Tanzil (with madd) is the canonical Hafs reading |

## Design consequence (normative)

Each edition gets its own P1 decoder table into the SHARED token IR; phases
P2+ are edition-blind. **Cross-edition IR equality over all 6,236 ayat is a
corpus invariant** (modulo deltas explicitly listed here with verdicts).
Any inter-edition difference not derivable from this table is a build error.
