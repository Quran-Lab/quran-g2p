# Engine findings from the citation work

Two things the citation pages (`tools/locate_citations.py`) brought up that
belong to the engines, not to the citations. Neither is changed in this branch.
Counts are from the dataset quran-tajweed-phonetics at 6f4be62.

## 1. A noon sakinah merged into ra or lam carries the lam's rule id

Where a word ends in a noon sakinah and the next word begins with ra or lam
(مِّن رَّبِّهِمْ in 2:5, also 2:12 and 2:13), the merged letter carries
`R133_R160_IDGHAM_KAMIL`, the rule of the lam of al and of two like letters.
The ruling that applies is `R142_IDGHAM_BILA_GHUNNA`, and the register reviews
these places under it. The phones carry `R142` only after a tanween.

- Places: 338, every one of them. None carries `R142`.
- Found by: a geminate ra or lam that begins its word, after a written word
  that ends in noon whose noon is not sounded in the phones.
- The phones, the units and the lengths are right. Only the rule id is the
  general one.
- Why it matters now: an app that shows where the books state the rule of a
  shadda flag would cite the passage on the lam of al at these places.
- For the quran-g2p owners: attribute `R142_IDGHAM_BILA_GHUNNA` to the merged
  letter after a noon sakinah as after a tanween, then regenerate the dataset.

## 2. Four qalqalah sites where the reference prescribes no qalqalah

The tah before ta in بَسَطتَ (5:28), فَرَّطتُمْ (12:80), أَحَطتُ (27:22) and
فَرَّطتُ (39:56) is merged into the ta with its itbaq kept and no qalqalah
(`R161_NAQIS_TA_NO_QALQALAH`, an event in `rule_index.jsonl`; the phone has no
`qalqalah`).

- The feedback engine's qalqalah step takes as a site each of the five
  qalqalah letters with no vowel after it, so it checks these four tah and can
  flag "qalqalah missing" where the learner was right.
- The release table agrees with the step, not with the dataset: in
  `expected_tj3.jsonl.gz` the tah of 5:28 has `qlq_site` 1 and `qalqalah` 0, and
  the reference file's token flags take the site from the same rule.
- For the feedback engine and release owners: leave a letter out of the
  qalqalah sites where the reference prescribes no qalqalah (`qalqalah` 0 in
  the table, no `qalqalah` on the phone), in the engine page's step 12, in the
  site flag of the reference file and in the engine vectors.
