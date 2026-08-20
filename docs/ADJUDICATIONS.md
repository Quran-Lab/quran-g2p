# Adjudication record

Every خطأ verdict from the expert review is adjudicated here against the
cited texts, per the protocol stated in the README: the reviewer
(Shaikh Sami Almadani, credited at his own preference) rules from his
own talaqqi; disagreements are settled by the classical sources,
never by the maintainer's opinion. This file is the permanent public
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
covered by `idgham-yeh-naqis` (88:2). The reviewer was informed of the
adjudication outcome, his catch was credited to him verbatim in this
record, and the corrected row was returned to him with
`expert_reviewed: false` and its verdict cell cleared, so that row 116
receives a fresh, independent verdict on the new content rather than
inheriting any prior one. No other row's verdict was touched.

**What this was, and was not.** The defect was confined to one row's
human-facing label: a kamil-meem heading pasted over a naqis-yeh
example. It was **not** an engine error — the engine's output at 2:8
was, and had always been, the correct naqis-yeh reading, in agreement
with the reviewer and with the mushaf's dabt — and it was **not** a
wrong ruling in the register: the kamil/naqis division itself is stated
correctly in R141 and in the sibling rows. The register's rulings
remain unfalsified. The review's first خطأ is also its first proof of
independence: a reviewer who catches what the machines cannot is
exactly what he was engaged for.

## #2 — proactive label audit after #1 (2026-08-18)

Adjudication #1 exposed a defect *class*: a row's human-facing label
contradicting its own example, invisible to the machine gates because
labels are prose. Rather than wait for the reviewer to find the next
one, all 208 rows were audited through two independent nets: a
mechanical checker (quoted fragments must occur in the row's ayah;
idgham letter/kamil/naqis wording must agree with the expect block) and
an LLM coherence read of every label against its full ayah. Findings:

- **`meem-idgham-lahum-ma` (sheet row 137):** label carried authoring
  debris — «(لَهُم مَّا? — وَلَهُم عَذَابٌ... مَرَضٌ)», including a
  literal question mark and a non-idgham fragment. The true site,
  قُلُوبِهِم مَّرَضٌ, sat at the label's tail and is what the expect
  block always asserted. Label rewritten to the site alone.
- **`iqlab-tanween` (sheet row 131):** label carried frozen
  deliberation — «(سَمِيعٌ عَلِيمٌ؟ لا — سَمِيعٌ بـ...)» — and the row
  anchored 2:181, whose iqlab site is a *noon* (فَمَنۢ بَدَّلَهُ), not
  a tanween; the expect block passed through the wrong mechanism.
  Re-anchored to a true tanween site, 22:61 «سَمِيعٌۢ بَصِيرٌ», iqlab
  meem in the dabt, engine verified.
- **`junction-madd-shortening` (sheet row 172):** label called the
  واو الجماعة shortening «مد الصلة» — silah belongs exclusively to haa
  al-damir — and its cite was a placeholder. Relabeled to the classical
  statement, حذف حرف المد لالتقاء الساكنين, and cited to هداية القاري
  2:599 where that wording is verbatim. The registry name for
  R131_MADD_SHORTENING was aligned to the same nass.
- **`naqis-tah-basatta` / `-ahatt` / `-farrattum`:** expects now pin
  `geminated: false` on the teh, matching the naqis doctrine and the
  engine (previously unasserted).

All three mislabeled rows sat AHEAD of the reviewer's position (he was
at 129; the rows are 131, 137, 172), so no verdict was invalidated. The
class is now closed structurally: `tests/test_row_labels.py` runs the
mechanical checks as a permanent gate, self-checked against synthetic
broken rows — including a resurrected copy of the #1 defect — so the
detector cannot pass vacuously.

## #3 — spliced shahid in the unzur-damm cite (2026-08-18)

Found by the red-team pass, confirmed against the print. Row 68's cite
quoted الجزرية as «واكسره حال الكسر والفتح **وضم**» — but the print
reads «وَاكْسِرْهُ حَالَ الْكَسْرِ وَالْفَتْحِ وَفِي الْأَسْمَاءِ...»;
the وضم was spliced from the neighbouring hukm. The correct shahid for
damm is the *preceding* bayt, «وَابْدَأْ بِهَمْزِ الْوَصْلِ مِنْ فِعْلٍ
بِضَمْ إِنْ كَانَ ثَالِثٌ مِنَ الْفِعْلِ يُضَمْ», verified in the print
(bab hamz al-wasl, p. 22 of the pinned edition). The cite was corrected
in the golden row, the canonical CSV, and the live sheet (E69). The
ruling itself and the reviewer's صحيح verdict on it are unaffected: the
hukm (damm of hamzat al-wasl for damm-third verbs) was always right;
only the quoted line of verse was wrong.

## #4 — «نون الوقاية» terminology + the iltiqa' mechanics, row 171 (2026-08-18)

**Reviewer's two notes, verbatim in substance:** (1) «نون الوقاية» is
the grammarians' term for the noon between a verb and ياء المتكلم
(أكرمني، أعطاني), not for the tanween's noon at this junction; (2) at
wasl the iltiqa' al-sakinayn in «خَيْرًا ٱلْوَصِيَّةُ» is between the
tanween's noon and لام التعريف, because hamzat al-wasl drops — so the
accurate statement is «نون التنوين مكسورة لالتقاء الساكنين بينها وبين
لام التعريف».

**Adjudication: upheld on both counts.** A corpus survey found
«نون الوقاية» nowhere in هداية القاري، النشر، غاية المريد، or التمهيد —
the tajweed literature's own idiom is كسر التنوين للساكنين, stated
verbatim in النشر 2:315 («بِالنَّصْبِ وَالتَّنْوِينِ وَكَسْرِهِ
لِلسَّاكِنَيْنِ», a Hafs-relevant farsh entry). And the mechanics are
as the reviewer says: the dropped hamza is the orthographic trigger,
not a party to the clash; the second sakin is the letter after it.

**Resolution:** row 171's label now reads «كسر نون التنوين لالتقاء
الساكنين بينها وبين الساكن بعد همزة الوصل الساقطة وصلًا», its cite
carries the verbatim النشر 2:315 line, and the register entry
R131_NOON_WIQAYA was renamed to match (the frozen rule id itself is an
internal identifier and stays, per the append-only manifest). Engine
behavior was never in question — it emits the kasra'd noon at every
such junction, verified corpus-wide in the behavioral sweep.

**Note for the record:** the red-team pass (547 attacks) did not catch
this; the sanad-holder did. Istilah precision is exactly where the
human layer outperforms every machine layer, which is why he is in the
loop.

---

## 5. قلقلة كبرى vs أكبر on وَتَبَّ (111:1)

**Raised by:** the arbitrating professor of Qira'at, in the formal
tahkeem of the complete register.

**Verdict given:** خطأ on the row labelled «قلقلة كبرى وقفًا مع التشديد
(وَتَبَّ)», with the note that the register appears to adopt the
two-grade division of qalqalah while others divide it into three
(صغرى / كبرى / أكبر), «ولا مشاحة في الاصطلاح».

**Adjudication: the arbitrator is upheld.** The register does not use
the two-grade division; it uses three, and carries a dedicated ruling
for the third (`R202_QALQALAH_AKBAR`, sourced in the Jazariyyah's
«وبيّن مقلقلًا إن سكنا» chapter and the maratib literature). The engine
already assigns `qalqalah="akbar"` to the geminated beh of وَتَبَّ at
waqf, and the statement row on qalqalah grades states all three
correctly. The defect was in this row's label alone, which said كبرى
where the engine, the register entry, and the project's own statement
row all say أكبر: a prose slip that made the register look internally
inconsistent to a reader checking it, exactly as he read it.

**Resolution:** the label now reads «قلقلة أكبر وقفًا مع التشديد
(وَتَبَّ)». No engine change: its output at 111:1 was already أكبر and
is unchanged, as the frozen determinism hash confirms.

**Note for the record:** this is the fifth adjudication and the fifth
time the finding was a labelling defect rather than an engine error.
Two independent reviewers, with no contact between them, have now each
caught prose slips of this same class. That is the pattern the machine
layers cannot see and the human layer reliably can.

---

## 6. Tafkheem of the ikhfa ghunna: five letters or seven

**Raised by:** the arbitrating professor of Qira'at.

**Verdict given:** خطأ on the statement row «غنة النون المخفاة تتبع ما
بعدها — تُفخَّم عند خمسة أحرف فقط هي ص ض ط ظ ق»، with the note
«تُفخَّم عند سبعة أحرف».

**Adjudication: no change; the row stands as written, and the
difference is one of scope rather than of ruling.** The isti'la letters
are indeed seven (خ ص ض ط ظ غ ق), and the general principle is exactly
as he states: the ghunna follows what comes after it. The row, however,
is stated of النون المخفاة specifically, and the noon can only be
mukhfah before the fifteen ikhfa letters. Two of the seven isti'la
letters, خاء and غين, are letters of izhar halqi: the noon before them
is izhar and is never mukhfah, so those two positions cannot arise for
an ikhfa ghunna at all. Within ikhfa the reachable isti'la set is
therefore exactly the five named. هداية القاري 1:181-182 states the
mirror rule and enumerates that same five-letter set by istiqra'.

**Resolution:** the row is unchanged, and this entry records both the
objection and the reasoning so the scope distinction is explicit on the
record rather than implicit in the wording. The engine's own
implementation is correct by the same reachability: its isti'la table
carries all seven letters, and the ghunna-tafkheem rule fires only on a
mukhfah noon, which the upstream izhar rule guarantees never occurs
before خاء or غين.
