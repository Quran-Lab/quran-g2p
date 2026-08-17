# Behavioral audit of the variant / waqf / junction paths

Corpus-scale sweeps behind the 2026-08-17 deep audit (each prints ALL
INVARIANTS HOLD on a healthy engine):

- `audit_variants.py`  - all 6,236 ayat x waqf variants: sukun==plain,
  ishmam phonetically inert (full-stream), rawm invariants (partial
  vowel, qalqalah off, no 6 in any free length), admissibility vs the
  raw text.
- `audit_stops.py`     - all 71,245 mid-ayah stop positions: prefix and
  suffix identity, legal pausal endings, legal resume starts (8-way
  parallel).
- `audit_junctions.py` - all 6,118 consecutive-ayah junctions:
  position-exact noon/tanween/meem junction behavior derived
  independently from the raw boundary letters (1,076 rule-firing
  junctions across iqlab/izhar/idgham/ikhfa/wiqaya classes).

The fast cross-sections of these sweeps live in
`tests/test_seeded_bugs_variants.py` as detectors, where a 9-mutant
drill (including the resurrected rawm-muttasil bug) must be fully
killed on every run.
