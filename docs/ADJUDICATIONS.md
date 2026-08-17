# Adjudication record

Every خطأ verdict from the expert review is adjudicated here against the
cited texts, per the protocol stated in the README: the reviewer rules
from his own talaqqi; disagreements are settled by the classical sources,
never by the maintainers' opinion. This file is the permanent public
record of those adjudications.

## #1 — row 116, `idgham-meem-kamil` (2026-08-18)

**Reviewer verdict:** خطأ. His correction, verbatim:
«إدغام ناقص بغنة في الياء؛ لأن النون الساكنة أُدغمت في الياء مع بقاء
صفة الغنة.»

**What the row said:** «إدغام كامل بغنة في الميم (مَن يَقُولُ...)» —
a *kamil-in-meem* label wrapped around a **yeh** example (2:8).

**Adjudication: the reviewer is upheld.** The idgham of noon sakinah
into ي is ناقص, not كامل, and the target letter at 2:8 is the yeh:

- **The nass:** التحفة separates إدغام بغنة (ينمو) into the complete
  idgham of ن and م and the incomplete idgham of و and ي; النشر 2:22-23
  states the naqis/kamil division explicitly for the two pairs.
- **The mushaf's own dabt** (Tanzil, KFGQPC): kamil sites carry a
  shadda on the swallowing letter, naqis sites do not —
  «لَن نَّصْبِرَ» (2:61) shadda present; «مِن مَّآءٍ» (86:6) shadda
  present; «مَن يَقُولُ» (2:8) **no shadda**.
- **The engine** agrees and always did: at 2:8 it produces yeh with
  `ghunna=idgham, geminated=false` (naqis); at 86:6 it produces meem
  with `geminated=true` and full mushaddad ghunna (kamil).

**Root cause:** an authoring slip when the idgham example series was
written — the kamil-meem row received the yeh example's text. The
machine gates could not see it: the row's `expect` block (and the
engine) asserted the *correct* naqis-yeh behavior, so every test
passed; only the human-facing Arabic label was wrong. Catching
label-level defects is precisely the human layer's jurisdiction, and it
worked.

**Resolution:** the row is restored to its intended kamil-meem example,
«مِن مَّآءٍ دَافِقٍ» (86:6), with the expect block pinning
`meem, geminated, mushaddad ghunna`. The naqis-yeh example remains
covered by `idgham-yeh-naqis` (88:2). The corrected row returns to the
reviewer with `expert_reviewed: false` for a fresh verdict.

**Score-keeping note:** the register's *rulings* remain unfalsified;
the defect was in one row's example pairing, not in any hukm or in
engine behavior. The review's first خطأ is also its first proof of
independence: a reviewer who catches what the machines cannot is
exactly what he was engaged for.
