# Text sources and acknowledgements

All inputs are vendored and pinned by SHA-256 in `data/`; loaders fail
closed on any drift.

- **Tanzil Uthmani** from the official distribution at
  [tanzil.net](https://tanzil.net): the authoritative input text. The file
  retains the Tanzil copyright notice, and is redistributed under the
  Tanzil terms (verbatim text, notice intact).
- **KFGQPC Hafs data v18** (King Fahd Glorious Quran Printing Complex):
  cross-check edition and dabt oracle.
- **[quran-tajweed](https://github.com/cpfair/quran-tajweed)** tajweed
  span annotations (Dar al-Maarifah-derived), with the project's own
  pinned base text: the independent trigger-span oracle.
- **[quran-transcript](https://github.com/obadx/quran-transcript)**
  ([on Hugging Face](https://huggingface.co/obadx)): the pioneering open
  tajweed phonetizer. This engine was built clean-room from the
  classical sources and shares none of its code, but quran-transcript
  served as the differential baseline for our validation: a
  character-level comparison across all 6,236 ayat, on which the two
  independent implementations agree at 98.9%. Every divergence carries
  a sourced verdict in `tests/verdicts/`. That a volunteer-built system
  stood at this level against a specification built directly from the
  books is a testament to its author's care.
- **The Quranic Arabic Corpus** morphology v0.4 by Kais Dukes
  ([corpus.quran.com](https://corpus.quran.com)), vendored verbatim with
  its GPL copyright block intact and pinned by SHA-256: the POS oracle
  for the hamzat al-wasl word classes (see the validation table).
- **Shaikh Sami Almadani**, hafiz and holder of a written ijazah in
  Hafs 'an 'Asim with a connected sanad, who reviewed all 208 entries
  of the rulings register from his own talaqqi, ruling by ruling. His
  catches, documented second wujuh, and adjudicated corrections are
  part of the public record; the register is stronger in his wording
  than it was in ours.
