# SPEC-002 — Orthographic Layer: Clusters, Mark Taxonomy, Dabt Semantics

Status: normative, in progress. Version: 0.1-draft (2026-08-15).

## Cluster model

`cluster(text)` groups each non-mark character with its trailing run of mark
characters; spans tile the input exactly; `uncluster` is an exact inverse
(property-tested over all 6,236 ayat × both editions).

Mark membership is an explicit project decision (`cluster.MARKS`), not Unicode
category — the small waw/yeh (U+06E5/06E6, category Lm) are marks here because
they attach to a host letter's cluster orthographically.

## Segment carriers (corpus findings, 2026-08-15)

Some marks are phonological SEGMENTS with their own vowel slot. Validation is
therefore per-segment within a cluster: a segment-carrier mark resets both the
duplicate check and the vowel-slot budget.

| carrier | evidence site | structure |
|---|---|---|
| U+06E6 small yeh | 27:36 (Tanzil AND KFGQPC): NOON+KASRA+〈small yeh〉+FATHA | silah yaa carrying its own fatha (ءَاتَىٰنِۦَ, pronounced -niya in wasl) |
| U+0654 hamza above | Tanzil 2:72: REH+FATHA+SUPERSCRIPT ALEF+〈hamza〉+SUKUN | floating hamza segment with its own sukun (فَٱدَّٰرَٰٔتُمْ) |
| U+06E5 small waw, U+06E8 small noon, U+06E7 small high yeh, U+0655 hamza below | same principle; no counterexample in either census | included as carriers |

## Vowel-slot inventory (single occupant per segment)

FATHATAN, DAMMATAN, KASRATAN, FATHA, DAMMA, KASRA, SUKUN (U+0652),
KFGQPC sukun (U+06E1), and the three KFGQPC open-tanween candidates
(U+0657 inverted damma, U+065E fatha-two-dots, U+0656 subscript alef —
interpretation TO VERIFY during P1 decode; entered as slot marks because the
corpus accepts it corpus-wide).

## To be completed during P1 (decoder tables)

- Per-edition dabt vocabularies: Tanzil {06E2/06ED markers, unified tanween}
  vs KFGQPC {open-tanween forms, 0652-as-silent-circle, 06E1-as-sukun, pause
  marks 06D6–06DB, sajdah 06E9, rub-el-hizb 06DE + NBSP}.
- The KFGQPC 06DC ×8 vs Tanzil ×2 delta; KFGQPC 06EC ×2 (ishmam+tasheel?)
  vs Tanzil 06EB+06EC split.
- Deletion reason codes for every non-phonological mark.
