<p align="center">
  <img src="assets/banner.png" alt="quran-g2p" width="100%">
</p>

<p align="center">
  <img src="https://img.shields.io/badge/tests-497%20passing-brightgreen" alt="tests">
  <img src="https://img.shields.io/badge/riwaya-Hafs%20%CA%BFan%20%CA%BFAsim%20(al--Shatibiyyah)-0b3d2e" alt="riwaya">
  <img src="https://img.shields.io/badge/license-Quran--Lab%20NPL--1.1-8a6d00" alt="license">
</p>

A clean-room, specification-first grapheme-to-phoneme engine for Quranic
recitation in the riwaya of **Hafs ʿan ʿAsim via tariq al-Shatibiyyah**. It
produces fully tajweed-attributed phone streams, a length-tagged tajweed
token lexicon, and training and grading artifacts for speech systems.

Every rule is implemented from the classical sources cited below, validated
against four independent oracles over the complete corpus, and guarded by a
structural test suite. Where the tradition transmits more than one wajh, the
engine carries the choice as an explicit, cited configuration knob, never a
silent default.

Built and maintained by **Quran Lab**, a waqf (non-profit endowment)
building open technology in the service of the Quran.

## What is in the box

| artifact | contents |
|---|---|
| `src/quran_g2p/` | the engine: pinned text loading, orthographic decode, 14 rule phases, typed phone IR with full provenance |
| `spec/` | the normative specification, every rule with its classical basis |
| `artifacts/tokenizer_tj1/` | `tokens.txt` (234 tokens including the `~` ghunna axis, blank last, hash-manifested), `vocab_manifest.json`, `ayah_tokens.jsonl`, `rule_index.jsonl` (set-valued prescriptions), `quran_labels_v1.jsonl` (dual-format labels), `bijection_old250.json` (warm-start map) |
| `tests/` | 497 tests: golden ayat (177 reviewable YAML rows in `tests/goldens/`), corpus invariants, oracle gates, a 25-mutant seeded-bug drill, frozen determinism hash |
| `tests/verdicts/` | the differential triage record: every disagreement with the reference implementation, verdicted with citations |

## Quick start

```bash
git clone https://github.com/Muno459/quran-g2p
cd quran-g2p
pip install -e .
python -m pytest tests/   # 497 tests, no GPU needed
```

```python
from quran_g2p.textbank import TextBank, AyahRef
from quran_g2p.phonemize import phonemize
from quran_g2p.tokenlayer import phones_to_tokens

tb = TextBank.load("tanzil")
ref = AyahRef(1, 1)
result = phonemize(tb.ayah(ref), edition="tanzil", ref=ref)
phones = result.segments[0].phones

print([p.base.value for p in phones[:6]])
# ['beh', 'kasra', 'seen', 'meem', 'kasra', 'lam']
print([t.text for t in phones_to_tokens(phones)])
# ['بِ', 'س', 'مِ', 'لَّ', 'ا:2', 'هِ', 'رّ^َ', 'ح', 'مَ', 'ا:2', 'نِ', 'رّ^َ', 'حِ', 'ۦ:4', 'م']
```

Every phone carries its rule provenance, tafkheem rank, ghunna grade,
qalqalah class, and a set-valued length prescription (`allowed`,
`scoring`, `canonical`) whose realized value is left for forced alignment
to fill.

## Design commitments

- **Prescription is not observation.** Free-choice durations (munfasil,
  ʿaared, leen, ghunna) are represented as sets: `allowed` is the
  Shatibiyyah-legal range, `scoring` the attested superset, `canonical` a
  deterministic default. The realized length is a separate slot only
  forced alignment may fill. The sources themselves demand this: no early
  book quantifies ghunna, sakt is «لطيفة» not a count (al-Nashr 1:240),
  and the free madds are transmitted as ranges.
- **The mushaf's own pointing is an oracle.** Two independently pinned
  text editions (Tanzil, KFGQPC) decode through per-edition tables into
  one shared representation; their dabt layers (open-tanween forms, sukun
  conventions, iqlab meems, sakt seens) are asserted against, corpus-wide.
- **No hand-typed Arabic in code** (a structural test enforces it), no
  imports from the quarantined reference adapter (likewise enforced), and
  a frozen corpus hash that turns every behavioral change into a reviewed,
  documented event.

## Validation

Over all 6,236 ayat:

| oracle | result |
|---|---|
| **Trigger-span dataset** (independent, Dar al-Maarifah-derived; 60,057 annotations across 18 rule categories) | the engine matches **every correct annotation** (60,056 of 60,057). The one it refuses is an error in the dataset itself: at 17:7 the annotation reads the bare rasm as tabee'i, while the rasm literature states the recitation restores the elided waw and the madd is muttasil (al-Hujja 5:85; al-Muhkam 1:168). Matching it would mean reproducing a documented mistake |
| **KFGQPC dabt witnesses** (~8,900 tanween sites) | **100% agreement** between derived rules and the written izhar, open-tanween, and iqlab forms |
| **Cross-edition phone equality** (Tanzil vs KFGQPC) | **6,236/6,236 identical, no exceptions** (the last rasm variant, 17:7, resolved by the rasm literature; see the register) |
| **Reference-engine differential** (char-level, whole corpus) | 98.9% ayah-exact; **every** remaining cluster carries a recorded verdict, including six classes where the classical sources rule against the reference implementation |
| **QAC morphology cross-check** (the Quranic Arabic Corpus, Kais Dukes; pinned sha256) | every hamzat-al-wasl word class-checked against the POS tags: **~2,000 unique word/class pairs, zero disagreements** (the oracle caught and fixed one ibtida' bug on first contact) |
| **Seeded-bug drill** | 25 hand-designed mutants, 100% kill rate |
| **Determinism** | frozen corpus hash; every intentional change logged with its ruling |

## Rulings register (site → ruling → sources)

| site / topic | ruling implemented | sources |
|---|---|---|
| 2:72 فَادَّارَأْتُمْ | the third written alif is the hamza's chair (سرج الهمزة), never pronounced: fa-ddā-**ra'**-tum, plain fatha on the reh; the only madd is the dal's tafāʿul alif (2) | دليل الحيران 1:415؛ ورد الطائف 1:230؛ لطائف الإشارات 2:216، 3:216؛ المدخل لدراسة القرآن 1:339؛ هداية القاري 1:280 |
| 27:1 طسٓ تِلْكَ | ikhfa of سين's noon at the taa; **بالإجماع** | حجة القراءات 1:521-522؛ العنوان 1:142؛ الوجيز للأهوازي 1:83-84؛ الوافي 1:136-137؛ المحتسب 1:241 |
| 36:1، 68:1 يس/ن + الواو | izhar؛ the **only** Shatibiyyah wajh (idgham exists solely via non-Shatibiyyah turuq) | الشاطبية بيت 281؛ فتح الوصيد 1:444-445؛ هداية القاري 1:294؛ السبعة 1:537-539؛ النشر 2:17-18؛ مشكل إعراب القرآن 2:598-599؛ إبراز المعاني 1:198 |
| عَيْن (19:1، 42:2) | مد لين لازم حرفي مخفف; Shatibiyyah wajhan {4,6}, **ishbāʿ 6 muqaddam**; qasr is Tayyibah-only | الشاطبية بيت 177؛ إبراز المعاني 1:122؛ سراج القارئ 1:60؛ فتح الوصيد 1:336؛ النشر 1:348-349؛ شرح الطيبة 1:75-76؛ النويري 1:399-402؛ هداية القاري 1:343 |
| the four sakts (18:1، 36:52، 75:27، 83:14) | **lazim in wasl** for this tariq; breathless, «لطيفة», sub-waqf duration (the 2-count is a later teaching convention); عِوَجَا keeps its ʿiwad-alif even in wasl | الشاطبية بيتا 830-831؛ الوافي 1:310؛ سراج القارئ 1:277؛ إبراز المعاني 1:565-566؛ النشر 1:240-241؛ هداية القاري 1:408-409؛ غاية المريد 1:234-235 |
| 69:28→29 مَالِيَهْ هَلَكَ (wasl) | izhar **with sakt** muqaddam (الجمهور); idgham the second wajh | النشر 2:21-22؛ هداية القاري 1:236-237؛ فتح الوصيد 1:434-435؛ غيث النفع 1:601-602؛ إبراز المعاني 1:193-194 |
| Anfal → Tawba junction | three wajhs by free choice; waqf / sakt / wasl with **iqlab**، all without basmala | الشاطبية (باب البسملة)؛ غيث النفع 1:270؛ البدور الزاهرة 1:133؛ مباحث في علم القراءات 1:111 |
| general pre-hamza sakt | **not of this tariq** (سماعي; Tayyibah-path feature) | النشر؛ الإتقان 1:299 |
| فِرْقٍ 26:63 (wasl) | wajhan jayyidan; **tarqeeq** the later tarjih («المأخوذ به المعوَّل عليه») | الشاطبية (باب الراءات)؛ فتح الوصيد 1:526؛ سراج القارئ 1:120 |
| مِصْرَ ×4 (waqf) / الْقِطْرِ 34:12 (waqf) | wajhan each; **مصر tafkheem، القطر tarqeeq**، «نظرًا للوصل وعملًا بالأصل» | النشر 2:105؛ النويري 2:33؛ غيث النفع 1:481؛ هداية القاري 1:130-132 |
| وَنُذُرِ ×6، يَسْرِ، أَسْرِ/فَأَسْرِ ×5 (waqf) | wajhan; **tarqeeq muqaddam** in all (deleted yaa / kasrat al-bināʾ); the article plural النُّذُر is outside the khilaf | النشر 2:110-111؛ هداية القاري 1:132-133؛ الميزان 1:105-106 |
| بِشَرَرٍ | **not** a Hafs khilaf (al-Azraq's) | النشر 2:98-99 |
| يَلْهَث ذَّٰلِكَ 7:176، ٱرْكَب مَّعَنَا 11:42 | kamil idgham, **single wajh** (Hafs among الباقين) | الشاطبية بيت 284؛ سراج القارئ 1:100-101؛ إبراز المعاني 1:199-200؛ فتح الوصيد 1:448 |
| نَخْلُقكُّم 77:20 | idgham; **kamil** fixed for this tariq by tahrir (al-Nashr validates both, kamil «أصح قياسًا») | النشر 1:221، 2:19-20؛ غيث النفع 1:614-615؛ هداية القاري 1:254-255؛ فريدة الدهر 1:444-445 |
| يَبْصُۜطُ 2:245، بَصْۜطَةً 7:69 | **seen**, single wajh (the Shatibiyyah's «الوجهان» rhymes to Khallad/Ibn Dhakwan) | الشاطبية بيتا 514-515؛ سراج القارئ 1:163؛ هداية القاري 2:577 |
| ٱلْمُصَۣيْطِرُونَ 52:37 | wajhan; **saad muqaddam** | التيسير 203-204؛ النشر 2:377-378؛ هداية القاري 2:579 |
| بِمُصَيْطِرٍ 88:22 | **saad**, single wajh from this tariq | النشر (حاصل الطريق)؛ النويري 1:310؛ لطائف الإشارات 9:266-267 |
| ضَعْف 30:54 ×3 | wajhan; **fath muqaddam** (the riwaya from ʿAsim); damm = Hafs' own ikhtiyar | الشاطبية بيتا 722-723؛ التيسير 174-176؛ تحبير التيسير 506؛ سراج القارئ 1:235 |
| الٓمٓ + اللَّهُ (3:1→2 wasl) | meem takes fatha; jalala wasl-hamza drops; مِيم madd = ishbāʿ 6 (preferred) or qasr 2; no tawassut | السبعة 1:199؛ غيث النفع 1:129-130؛ القول السديد 1:111-112؛ الميسر 1:50؛ النويري 2:231 |
| basmala junctions | three permitted joins, the fourth forbidden («فلا تقفنَّ الدهر فيها»)؛ basmala belongs to what follows; shurrāḥ prefer stop-then-join; mid-surah starts: takhyeer | الشاطبية أبيات 106-107؛ التيسير 1:17-18؛ النشر 1:263، 1:265؛ فتح الوصيد 1:276-277؛ سراج القارئ 1:29-31؛ الوافي 1:49-50؛ هداية القاري 2:568، 2:593-594؛ غيث النفع 1:34 |
| the harakah as time-unit | madd durations are PROPORTIONAL to the same recitation's harakat («يتناسب المد والتحريك»؛ the engine's self-calibrating alignment is this nass, mechanized); tabeeʿi is the unit, per vowel quality; absolute times vary with tempo; the counts are talaqqi-approximations | الدر النثير 2:216-217؛ جمال القراء 648-649؛ النشر 1:316-317، 1:326؛ الإقناع 158-159؛ العميد 82-83؛ الميزان 166-168؛ فتح رب البرية 74-76؛ الكامل للهذلي 421-422؛ معجم علوم القرآن 1:127 |
| qalqalah | a colorless BURST, never a vowel («وحسبانهم أن القلقلة حركة، وليس كذلك»؛ with the burst-color khilaf recorded as unresolved); three grades sughra/kubra/akbar | النشر 1:203، 1:216؛ الزيادة والإحسان 3:239-241؛ الميزان 1:79-81؛ هداية القاري 1:84-87؛ بغية المستفيد 1:50-52؛ غاية المريد 1:146؛ الروضة الندية 1:28-29؛ العميد 1:66 |
| rawm & ishmām (waqf variants) | rawm = partial haraka (damm/kasr classes only; ʿaared → qasr 2); ishmām = post-iskan lip-rounding, visual, damm only (ʿaared → 2/4/6) | الشاطبية أبيات 368-373؛ النشر 2:121؛ التيسير 58-59؛ هداية القاري 2:510-515؛ الإتحاف 1:135-136؛ غاية المريد 1:181-184؛ العميد 1:102؛ القول السديد 1:128 |
| 17:7 لِيَسُوءُوا | the rasm elides one of the two waws; recitation restores the first (li-yasūʾū, «همزة بين واوين»), muttasil on it; the engine restores it where an edition prints the bare rasm | الحجة للقراء السبعة 5:85؛ المحكم في نقط المصاحف 1:168-169؛ النقط 1:141-142؛ دليل الحيران 1:227-228، 1:405-406؛ معاني القراءات للأزهري 2:87؛ فريدة الدهر 3:256؛ هداية القاري 1:280-281 |
| the six istifhām+wasl sites (6:143-144، 10:51/91، 10:59، 27:59) | wajhan: **ibdāl** (pure alif, lazim 6) muqaddam «فللكل ذا أولى» / tashīl bayna-bayna with no madd (config knob) | الشاطبية أبيات 192-194؛ سراج القارئ 1:66-67؛ فتح الوصيد 1:350؛ الوافي 1:87؛ النشر 1:377-378؛ التيسير (ط. الشغدلي) 1:378-380؛ الدر النثير 4:240-241 |
| hamzat al-wasl classes | article → fath; the seven Quranic nouns → kasra; verbs by the third-letter haraka; exactly **five** ʿarida-damma verbs (امشوا ابنوا اقضوا امضوا ائتوا) → kasra; ٱؤْـ/ٱئْـ ibtidāʾ → badal madd | المقدمة الجزرية 101-103؛ هداية القاري 2:482، 2:488؛ الروضة الندية 1:126-127؛ فتح الأقفال 1:162؛ الميزان 1:234 |
| hāʾ al-kināya | silah between two voweled letters, none after sakin; silah drops at waqf («الصلة تسقط في الوقف»); the Hafs farsh: يرضه 39:7 qasr؛ فيه مهانا 25:69 the sole silah-after-sakin؛ أرجه 7:111/26:36 وفألقه 27:28 iskan؛ يتقه 24:52 qaf-sukun+qasr؛ أنسانيه 18:63 وعليه الله 48:10 damm؛ rawm/ishmām on the pronoun hāʾ: **tafsīl** (Ibn al-Jazari's «أعدل المذاهب»)؛ none after damm/wāw/kasr/yāʾ, open after fath/alif/sakin sahih; يتقه keeps rawm, يرضه keeps all three; hāʾ as-sakt takes neither, ever | الشاطبية أبيات 158-168؛ التيسير 1:29-30؛ سراج القارئ 1:45-48، 1:125؛ فتح الوصيد 1:317-318؛ إبراز المعاني 1:105-106، 1:109-110؛ الوافي 1:67-72؛ الهادي شرح الطيبة 1:161، 1:166؛ غاية المريد 1:293؛ النشر 1:305-306، 2:124-125؛ شرح الطيبة لابن الجزري 1:142؛ الإتحاف 1:135-136؛ غيث النفع 1:86-87؛ هداية القاري 1:322، 1:327-328، 1:359؛ الكنز 1:334؛ الإقناع 1:244؛ لطائف الإشارات 9:75 |
| ghunna | maraatib are qualitative (الجعبري: أكمل/أزيد/أوفى); **no early source quantifies its duration**، the 2-count is talaqqi-transmitted and equal across the top ranks; the mukhfah's ghunna follows the next letter's tafkheem at ص ض ط ظ ق | لطائف الإشارات 1:350-351، 1:366-367؛ الميزان 1:123-124 (المرعشي عبر نهاية القول المفيد 125-126)؛ هداية القاري 1:67، 1:181-183، 1:187؛ تنبيه الغافلين 1:78؛ النويري 1:257؛ النشر 1:213، 2:25 |
| tafkheem ranks & inheritance | the classical five maraatib carried on every emphatic phone; the ALIF follows what precedes it («لا توصف بتفخيم ولا ترقيق بل تابعة لما قبلها»؛ and the always-raqiq claim is a refuted wahm)؛ the GHUNNA follows what follows it, mofakham at exactly ص ض ط ظ ق | النشر 1:215-216؛ هداية القاري 1:118، 1:181-182؛ غاية المريد 1:158-159؛ العميد 1:130؛ لطائف الإشارات 1:366-367 |
| the seven alifs (أنا×61، لكنا، الظنونا، الرسولا، السبيلا، سلاسلا، قواريرا الأولى) | dropped in wasl, realized at waqf (tabeeʿi 2); قواريرا الثانية never realized; سلاسلا waqf wajhan؛ the printed round-zero dabt selects HADHF (taqdim disputed: الضباع/العميد hadhf vs هداية القاري ithbat); آتاني 27:36 wasl = yaa maftuha, waqf wajhan; ithbat muqaddam (هداية القاري 2:545; the 1:290-295 hadhf-wujub lists are Tayyiba-tahrir, not this tariq); أيه ×3 waqf bil-haa for Hafs اتباعًا للرسم | الشاطبية «وحق صحاب قصر وصل الظنون...» + بيت 429؛ التيسير 1:177-178، 1:217-218؛ السبعة 1:519، 1:664-665؛ جامع البيان 4:1678-1679؛ سراج القارئ 1:325-326؛ حجة القراءات 1:142، 1:416-417، 1:572-574؛ الحجة للفارسي 5:144-146؛ جمال القراء 1:747-748؛ النشر 2:347-348؛ طيبة النشر (سلاسلا)؛ النويري 2:603؛ تحبير التيسير 1:599؛ هداية القاري 2:526؛ العميد 1:160-161؛ صريح النص للضباع 25؛ إبراز المعاني 1:309-310؛ الدر النثير 4:197؛ فتح رب البرية 1:122؛ هداية القاري 2:545، 1:290-295؛ النشر 2:142، 2:332؛ سراج القارئ 129-131 (ط. الشاملة)؛ غيث النفع 531، 568؛ الإتحاف 410؛ الشاطبية بيت 382؛ الوافي 1:182؛ الوجيز في علم التجويد 1:55-56 |
| sifat matrix | the Jazariyya's full seventeen, bayt-verified set-for-set (bayts 20-26); count khilaf recorded (17 jumhur / 14 البركوي +ghunna / 16 السخاوي +هوائي); idhlaq/ismat kept though «لا دخل لهما في تجويد الحروف» | المقدمة الجزرية أبيات 20-26 (1:59-61)؛ النويري 1:237-238؛ هداية القاري 1:78، 1:83، 1:93؛ الوجيز في علم التجويد 1:10-11؛ معجم علوم القرآن 1:175 |
| tāʾ al-taʾnīth at waqf | not written with tāʾ → waqf hāʾ (the R122 rule, with the مناة-bil-hāʾ report rejected as ghalat); WRITTEN with open tāʾ (ياأبت، هيهات، مرضات، لات، اللات، ذات...) → Hafs stops bil-tāʾ اتباعًا للرسم; open-tāʾ waqf keeps rawm/ishmām | النشر 2:126، 2:131-133 |
| ikhtilas/tasheel hasr | tasheel = 41:44 ONLY («لم تُسهَّل في رواية حفص إلا همزة واحدة»)؛ ikhtilas/rawm = تأمنا 12:11 ONLY (ishmam per the printed dabt = canonical; ikhtilas muqaddam per المرصفي = variant) | معجم علوم القرآن 1:93؛ هداية القاري 1:259-261، 2:577؛ فريدة الدهر 1:161، 4:336؛ الدر النثير 4:219 |
| one-off events | imala 11:41؛ tasheel 41:44؛ ishmam 12:11؛ naql 49:11؛ site-implemented with the mushaf marks as witnesses | (rasm witnesses + the farsh literature above) |

## Bibliography

Classical metins and their commentaries:

- **حرز الأماني ووجه التهاني (متن الشاطبية)**، الإمام الشاطبي. Cited: أبيات 106-107، 158-159، 164-168، 177، 192-194، 276، 281، 284، 514-515، 722-723، 830-831؛ باب الراءات؛ باب البسملة.
- **المقدمة الجزرية**، ابن الجزري. Cited: أبيات 101-103؛ «وبين الإطباق من أحطت…»، أبيات 20-26 (1:59-61).
- **طيبة النشر**، ابن الجزري. Cited: أبيات 114-115، 172.
- **تحفة الأطفال**، الجمزوري (متون طالب العلم 1:35).
- **فتح الوصيد في شرح القصيد**، السخاوي. Cited: 1:317-324، 1:336، 1:434-435، 1:444-445، 1:448، 1:526.
- **إبراز المعاني من حرز الأماني**، أبو شامة المقدسي. Cited: 1:105-106، 1:109-110، 1:122، 1:193-194، 1:198، 1:199-200، 1:565-566، 1:750، 1:309-310.
- **سراج القارئ المبتدي**، ابن القاصح. Cited: 1:29-31، 1:45-48، 1:60، 1:100-101، 1:120، 1:163، 1:235، 1:277، 1:325-326.
- **الوافي في شرح الشاطبية**، عبد الفتاح القاضي. Cited: 1:67-72، 1:136-137، 1:310، 1:222-223.
- **شرح طيبة النشر**، ابن الجزري (لابنه). Cited: 1:37، 1:75-76، 1:142.
- **شرح طيبة النشر**، النويري. Cited: 1:257، 1:310، 1:399-402، 1:485، 2:33، 2:231، 2:603، 1:237-238.
- **الهادي شرح طيبة النشر**، 1:161، 1:166، 2:12.

Ibn al-Jazari and the qira'at canon:

- **النشر في القراءات العشر**، ابن الجزري. Cited: 1:203، 1:213، 1:263، 1:265، 1:305-306، 1:316-317، 1:326، 1:377-378، 2:124-125، 1:215، 1:221، 1:240-241، 1:348-349، 2:17-18، 2:19-20، 2:21-22، 2:25، 2:98-99، 2:105، 2:110-111، 2:377-378، 2:347-348.
- **التمهيد في علم التجويد**، ابن الجزري. Cited: 1:47، 1:161.
- **تحبير التيسير**، ابن الجزري. Cited: 506، 1:599.
- **التيسير في القراءات السبع**، أبو عمرو الداني. Cited: 1:17-18، 1:29-30، 58-59، 174-176، 203-204، 1:177-178، 1:217-218.
- **السبعة في القراءات**، ابن مجاهد. Cited: 1:199، 1:405، 1:519، 1:537-539، 1:664-665.
- **العنوان في القراءات السبع**، ابن خلف المقرئ. Cited: 1:142.
- **الوجيز في شرح قراءات القرأة الثمانية**، الأهوازي. Cited: 1:83-84.
- **حجة القراءات**، ابن زنجلة. Cited: 1:142، 1:416-417، 1:521-522، 1:572-574.
- **المحتسب**، ابن جني. Cited: 1:241.
- **الإقناع في القراءات السبع**، ابن الباذش. Cited: 1:101، 1:244.
- **الكنز في القراءات العشر**، الواسطي. Cited: 1:334.
- **جامع البيان في القراءات السبع**، الداني. Cited: 4:1678-1679.
- **جمال القراء وكمال الإقراء**، السخاوي. Cited: 1:747-748 (وأيضًا 648-649).
- **صريح النص في الكلمات المختلف فيها عن حفص**، الضباع. Cited: 25.
- **التجريد لبغية المريد**، ابن الفحام. Cited: 1:116.
- **البدور الزاهرة**، القاضي. Cited: 1:34، 1:133.
- **إتحاف فضلاء البشر**، البنا الدمياطي. Cited: 1:46، 1:48، 1:135-136.
- **لطائف الإشارات لفنون القراءات**، القسطلاني. Cited: 1:350-351، 1:366-367، 2:216، 3:216، 9:75، 9:266-267.
- **غيث النفع في القراءات السبع**، الصفاقسي. Cited: 1:129-130، 1:270، 1:481، 1:522، 1:601-602، 1:614-615، 1:86-87.
- **تنبيه الغافلين**، الصفاقسي. Cited: 1:78.
- **فريدة الدهر في تأصيل وجمع القراءات**، محمد إبراهيم محمد سالم. Cited: 1:161، 1:444-445، 3:364، 4:336.

Rasm and orthography:

- **دليل الحيران على مورد الظمآن**، المارغني. Cited: 1:415.
- **ورد الطائف في شرح روضة الطرائف في رسم المصحف**، 1:230.
- **المصاحف**، ابن أبي داود. Cited: 1:337.
- **مشكل إعراب القرآن**، مكي بن أبي طالب. Cited: 2:598-599.
- **المدخل لدراسة القرآن الكريم**، 1:339.
- **صبح الأعشى**، القلقشندي. Cited: 3:191.

Tajwid manuals (later masters):

- **هداية القاري إلى تجويد كلام الباري**، عبد الفتاح المرصفي. Cited: 1:67، 1:130-133، 1:359، 1:181-183، 1:187، 1:236-237، 1:254-255، 1:280، 1:294، 1:343، 1:408-409، 2:482، 2:488، 2:577-579، 1:322، 1:327-328، 2:526، 1:78، 1:83، 1:93، 1:259-261، 1:118، 1:181-182.
- **نهاية القول المفيد**، محمد مكي نصر. Cited: 125-126 (ناقلًا نص المرعشي في جهد المقل؛ لا تُنسب صفحة مباشرة لجهد المقل دون تحقق من الطبعة).
- **الميزان في أحكام تجويد القرآن**، فريال زكريا العبد. Cited: 1:105-106، 1:123-124، 1:220، 1:234.
- **القول السديد في علم التجويد**، Cited: 1:96، 1:99، 1:111-112، 1:200، 1:202.
- **غاية المريد في علم التجويد**، عطية قابل نصر. Cited: 1:49، 1:100، 1:164، 1:234-235، 1:280-284، 1:293، 1:158-159.
- **العميد في علم التجويد**، محمود علي بسة. Cited: 1:13، 1:66، 1:102، 1:105، 1:120، 1:160-161 (وأيضًا 82-83)، 1:130.
- **الروضة الندية شرح متن الجزرية**، Cited: 1:51، 1:126-127.
- **فتح رب البرية شرح المقدمة الجزرية**، Cited: 1:56، 1:69، 1:112، 1:122 (وأيضًا 74-76).
- **فتح الأقفال بشرح لامية الأفعال**، Cited: 1:162.
- **الوجيز في علم التجويد**، Cited: 1:37، 1:59، 1:10-11.
- **معلم التجويد**، 1:90؛ **قواعد التجويد على رواية حفص**، 1:118؛ **فن الإلقاء**، 1:156؛ **شذا العرف في فن الصرف**، 1:120؛ **تعجيل الندى بشرح قطر الندى**، 1:288.

Reference works and journals:

- **الإتقان في علوم القرآن**، السيوطي. Cited: 1:299.
- **المحكم في نقط المصاحف**، الداني. Cited: 1:168-169؛ **النقط**، الداني. Cited: 1:141-142؛ **الحجة للقراء السبعة**، أبو علي الفارسي. Cited: 5:85؛ **معاني القراءات**، الأزهري. Cited: 2:87؛ **الدر النثير والعذب النمير**، المالقي. Cited: 4:219، 4:240-241؛ **الهبات السنية العلية**، Cited: 1:365-366؛ **الزيادة والإحسان في علوم القرآن**، ابن عقيلة. Cited: 3:239-241؛ **بغية المستفيد**، ابن بلبان. Cited: 1:50-52؛ **المختصر المفيد**، الحمصي. Cited: 1:644؛ **تيسير أحكام التجويد**، Cited: 1:23-25؛ **ظاهرة المد في الأداء القرآني**، Cited: 1:406؛ **لسان العرب**، Cited: 1:95-96؛ **أضواء البيان**، Cited: 3:484؛ **إعراب القرآن الكريم**، Cited: 2:1244؛ **الشمعة المضية**، Cited: 1:209؛ **كيف تقرأ برواية قالون**، Cited: 1:82؛ **معلم التجويد**، Cited: 1:142؛ **الوجيز في علم التجويد**، Cited: 1:38؛ **مجموعة مهمة في التجويد والقراءات**، Cited: 1:202.
- **معجم علوم القرآن**، 1:93، 1:154-155، 1:166، 1:175، 1:260؛ **المحرر في علوم القرآن**، 1:290؛ **مباحث في علم القراءات مع بيان أصول رواية حفص**، 1:92، 1:111؛ **صفحات في علوم القراءات**، 1:279؛ **الموسوعة القرآنية المتخصصة**، 1:405؛ **الموسوعة القرآنية**، 7:15؛ **الميسر في القراءات الأربع عشرة**، 1:50؛ **القراءات بروايتي ورش وحفص**، 1:184؛ مجلة الجامعة الإسلامية بالمدينة؛ 43:417؛ مجلة جامعة أم القرى؛ 7:200.

## Text sources and acknowledgements

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
- **The Quranic Arabic Corpus** morphology v0.4 by Kais Dukes
  ([corpus.quran.com](https://corpus.quran.com)), vendored verbatim with
  its GPL copyright block intact and pinned by SHA-256: the POS oracle
  for the hamzat al-wasl word classes (see the validation table).

## Status

The engine is feature-complete and green (497 tests): the core rule
pipeline, mid-ayah waqf and resume segmentation with the full waqf farsh,
tagged waqf-variant enumeration (rawm/ishmam and the transmitted site
wajhs), the wasl concat phase across ayah and surah boundaries, the token
layer, and the warm-start bijection. In progress downstream: the
alignment-based realized-length pipeline (with a blind fixed-madd
recovery gate before any corpus relabeling) and the ASR integration.

A human expert review pass over the golden set and the rulings register is
the final release gate. The machine validation above is necessary, not
sufficient, and the maintainers hold the tradition's own standard, التلقي,
above any engine, including this one.

## License

The code, specification, and artifacts are released under the
**Quran-Lab No-Profit License, Version 1.1 (NPL-1.1)**: free to use, run,
copy, and adapt for non-profit purposes; no profit may be obtained from
it or from derivatives (see `LICENSE` for the exact terms). The vendored
texts in `data/` remain under their own upstream terms as noted above.

## Citation

```bibtex
@software{quran_g2p,
  author = {{Quran Lab}},
  title  = {quran-g2p: a specification-first tajweed phonemizer for
            Hafs ʿan ʿAsim (tariq al-Shatibiyyah)},
  year   = {2026},
  url    = {https://github.com/Muno459/quran-g2p}
}
```
