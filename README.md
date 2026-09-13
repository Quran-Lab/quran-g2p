<p align="center">
  <img src="assets/banner.png" alt="quran-g2p" width="100%">
</p>

<p align="center">
  <img src="https://img.shields.io/badge/tests-564-brightgreen" alt="tests">
  <img src="https://img.shields.io/badge/expert%20review-208%2F208%20%C2%B7%200%20%D8%AE%D8%B7%D8%A3-0b3d2e" alt="review complete">
  <img src="https://img.shields.io/badge/riwaya-Hafs%20%CA%BFan%20%CA%BFAsim%20(al--Shatibiyyah)-0b3d2e" alt="riwaya">
  <img src="https://img.shields.io/badge/license-Quran--Lab%20NPL--1.2-8a6d00" alt="license">
</p>

**Text in, tajweed-attributed phones out.** A specification-first
grapheme-to-phoneme engine for Quranic recitation in the riwaya of Hafs ʿan
ʿAsim via tariq al-Shatibiyyah, built clean-room from the classical books.

Every rule is cited to a printed page and ruled on entry by entry by **Shaikh
Sami Almadani**: hafiz, holder of a written ijazah in Hafs ʿan ʿAsim with a
sanad connected to the Prophet ﷺ, certified by the Prophet's Mosque program in
Madinah. The register was then sealed twice by professors of Qira'at at **Umm
al-Qura University in Makkah**. Where the tradition transmits more than one
wajh, the engine carries the choice as an explicit cited knob, never a silent
default.

Built and maintained by **Quran Lab**, a waqf building open technology in the
service of the Quran.

```python
from quran_g2p.textbank import TextBank, AyahRef
from quran_g2p.phonemize import phonemize
from quran_g2p.tokenlayer import phones_to_tokens

tb = TextBank.load("tanzil")
ref = AyahRef(1, 1)
phones = phonemize(tb.ayah(ref), edition="tanzil", ref=ref).segments[0].phones

[p.base.value for p in phones[:6]]
# ['beh', 'kasra', 'seen', 'meem', 'kasra', 'lam']

[t.text for t in phones_to_tokens(phones)]
# ['بِ', 'س', 'مِ', 'لَّ', 'ا:2', 'هِ', 'رّ^َ', 'ح', 'مَ', 'ا:2', 'نِ', 'رّ^َ', 'حِ', 'ۦ:4', 'م']
```

Each phone carries its rule provenance, tafkheem rank, ghunna grade, qalqalah
class, and a **set-valued** length prescription (`allowed`, `scoring`,
`canonical`). The realized length is a separate slot that only forced alignment
may fill: a prescription is not an observation, and the engine never pretends
otherwise.

## Ruled on, entry by entry, by a connected sanad

Every one of the **208 entries** in the rulings register was ruled on
independently, from the reviewer's own talaqqi rather than from our sources.
Each verdict is صحيح, خطأ or فيه وجهان, with a correction and a reason required
for any خطأ.

### Shaikh Sami Almadani

| qualification | detail |
|---|---|
| **Ijazah** | written **ijazah in Hafs ʿan ʿAsim via tariq al-Shatibiyyah** (1434 / 2013), carrying the authorization to transmit («وقد أجزته أن يقرئ غيره كما قرأ») and a **connected sanad (الإسناد المتصل) to the Prophet ﷺ** |
| **Hifz** | **hafiz of the entire Quran**, board-examined by Wifaq al-Madaris al-Salafiyyah, grade **mumtaz**, 1443 / 2022 |
| **Tajweed** | full-Quran certificate, **mumtaz, 377/400**, on the classical curriculum: al-Muqaddimah al-Jazariyyah, Tuhfat al-Atfal, Jamal al-Qur'an, Fawa'id Makkiyyah, Taysir al-Tajweed |
| **Madinah** | certified by the **Prophet's Mosque Qur'an program** in Madinah (10 ajza', 96.94%); Shari'ah student at the **Islamic University of Madinah** |

<p align="center">
  <strong>His verdict on the register: 191 confirmed &middot; 0 judged wrong &middot; 17 documenting a second transmitted wajh</strong>
</p>

The seventeen are agreements in substance that document a second transmitted
wajh. Scans of the credentials are on file with the maintainer. He is named
here at his own preference.

### The credential was tested, not taken on trust

Before engagement he sat a blind screening: ten rulings, three of them carrying
deliberately planted errors dressed in the register's own citation format.
**All three caught. Zero false alarms on the seven true rulings.** The same
screening has since failed other candidates. A filter everyone passes proves
nothing, so the fails are part of what the pass means.

### Then sealed twice, at the top of the discipline

The complete register underwent formal scholarly arbitration (تحكيم علمي) by
**two serving professors at the Department of Qira'at, Umm al-Qura University
in Makkah**, engaged separately and each blind to the other and to the first
reviewer. The first ruled on all 208 entries «وفق ما تلقيته وقرأته على أساتذتي
ومشايخي» (according to what he received and read before his teachers and
shaykhs) and confirmed the register. The second examined every row of the full
instrument, caught every planted error in his copy and refuted each with the
classical nass cited back at us, and returned some forty written notes, **not
one of which overturned a phonetic ruling**. Both are credited by rank alone,
at their own request.

**Three unbroken chains have now examined every ruling independently, with no
contact between them. All three reached the same answer, and a fourth
examination is under way.** Every disagreement at every layer was adjudicated
against the cited classical texts, on the public record.

<p align="center">
  <img src="assets/review-status.svg" alt="Expert review: 208 of 208 rulings reviewed, 191 confirmed, 17 two-wajh, 0 judged wrong" width="680">
</p>

→ **[The full review ladder](docs/REVIEW.md)** · [adjudications](docs/ADJUDICATIONS.md) · [how a ruling gets here](docs/METHOD.md)

### And the machine half

| # | claim | evidence |
|---|---|---|
| **1** | the engine implements the register | 5 independent corpus oracles, 564 tests, a 25-mutant seeded-bug drill at 100% kill |
| **2** | the register matches the transmitted riwaya | the review above: **208 / 208** |
| **3** | the register holds at the top of the discipline | two Umm al-Qura arbitrations, both confirming in full |

## Validation

Over all 6,236 ayat. The first five are independent oracles; the last two are
gates the engine must survive against itself.

| check | result |
|---|---|
| **Trigger-span dataset** (Dar al-Maarifah-derived; 60,057 annotations, 18 categories) | **60,056 / 60,057**. The one exception is an error in *their* file (17:7, read off the bare rasm); the engine refuses to reproduce it |
| **KFGQPC dabt witnesses** (~8,900 tanween sites) | **100%** agreement with the written izhar, open-tanween and iqlab forms |
| **Cross-edition phone equality** (Tanzil vs KFGQPC) | **6,236 / 6,236 identical**, no exceptions |
| **QAC morphology** (Kais Dukes, pinned sha256) | ~2,000 hamzat-al-wasl word/class pairs, **zero disagreements** |
| **Differential vs quran-transcript** (char-level) | 98.9% ayah-exact; **every** residual carries a recorded verdict |
| **Variant-path audit** | all waqf variants, 71,245 mid-ayah stops, 6,118 ayah junctions; 9-mutant drill, 100% kill |
| **Rule incidence** | 62 rules, and any rule that fires nowhere must say why or the suite fails ([docs](docs/INCIDENCE.md)) |

## What is in the box

| path | contents |
|---|---|
| `src/quran_g2p/` | the engine: pinned text loading, orthographic decode, 14 rule phases, typed phone IR carrying full provenance |
| `spec/` | the normative specification, every rule with its classical basis |
| `docs/RULINGS-REGISTER.md` | 62 rulings, each bound to its citation and its review rows. The engine refuses to import if a rule lacks either |
| `artifacts/tokenizer_tj1/` | 234-token lexicon with the `~` ghunna axis, ayah tokens, set-valued rule index, dual-format labels, warm-start bijection |
| `artifacts/spans/` | the same rulings as character offsets: 138,461 spans over all 6,236 ayat, edition SHA-256 in the manifest, for consumers that cannot run Python |
| `tests/` | 564 tests: 208 expert-reviewed golden rows, corpus invariants, oracle gates, seeded-bug drills, frozen determinism hash |
| `tests/verdicts/` | every disagreement with quran-transcript, verdicted with citations |

## Design commitments

- **Prescription is not observation.** Free-choice durations (munfasil, ʿaared,
  leen, ghunna) are sets, not numbers. The sources demand it: no early book
  quantifies ghunna, sakt is «لطيفة» and not a count (al-Nashr 1:240), and the
  free madds are transmitted as ranges.
- **The mushaf's own pointing is an oracle.** Two independently pinned editions
  decode into one shared representation, and their dabt layers (open-tanween
  forms, sukun conventions, iqlab meems, sakt seens) are asserted against
  corpus-wide.
- **Nothing enters on a model's word.** No hand-typed Arabic in code, no imports
  from the quarantined reference adapter (both structurally enforced), and a
  frozen corpus hash that turns every behavioral change into a reviewed,
  documented event.

**Scope of authority.** The engine rules on text, not on people. Certifying
reciters remains the sanad's work, and the Quran is still learned at the mouths
of scholars; this is built to serve that transmission, not to sit above it.

## Documentation

| document | what is in it |
|---|---|
| [REVIEW.md](docs/REVIEW.md) | the three chains, the credentials, the blind screenings |
| [ADJUDICATIONS.md](docs/ADJUDICATIONS.md) | every disagreement, resolved against the cited texts |
| [RULINGS-REGISTER.md](docs/RULINGS-REGISTER.md) | the generated register: rule → ruling → sources → review rows |
| [NOTABLE-RULINGS.md](docs/NOTABLE-RULINGS.md) | the contested sites, where an implementation usually goes wrong |
| [SCOPE.md](docs/SCOPE.md) | the chapter-by-chapter sweep of the manuals: what is covered, and what is out of scope and why |
| [METHOD.md](docs/METHOD.md) · [CITATION-AUDIT.md](docs/CITATION-AUDIT.md) | how a ruling gets in, and the page-by-page check that it is where we say it is |
| [INCIDENCE.md](docs/INCIDENCE.md) | which rules fire, and what a silence is allowed to mean |
| [BIBLIOGRAPHY.md](docs/BIBLIOGRAPHY.md) · [SOURCES.md](docs/SOURCES.md) | the works cited, and the vendored texts with their terms |

## Development

```bash
git clone https://github.com/Quran-Lab/quran-g2p
cd quran-g2p
pip install -e .
python -m pytest tests/   # 564 tests, no GPU needed
```

## License

**Quran-Lab No-Profit License, Version 1.2 (NPL-1.2)**: free to use, run, copy
and adapt. The work itself is never for sale, so you may not charge for it, for
access to it, or for any feature it powers. What you earn from your own
teaching, services or labour is your own; this is a condition on the work, not a
ruling on anyone's livelihood. See [LICENSE](LICENSE). The vendored texts in
`data/` remain under their own upstream terms ([SOURCES.md](docs/SOURCES.md)).

## Citation

```bibtex
@software{quran_g2p,
  author = {{Quran Lab}},
  title  = {quran-g2p: a specification-first tajweed phonemizer for
            Hafs ʿan ʿAsim (tariq al-Shatibiyyah)},
  year   = {2026},
  url    = {https://github.com/Quran-Lab/quran-g2p}
}
```
