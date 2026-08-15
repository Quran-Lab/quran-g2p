# SPEC-011/012/110/120s/130s/150s/160s/170/200s/210s/220s — Structural & Attribute Rules (consolidated)

Status: normative, consolidated pending per-family expansion. Each section
follows the template: basis → trigger → delta → sites → tests.

## SPEC-011 — الحروف المقطعة (R011, P1)
Basis: recitation tradition (التلقي); names per القراءة المتواترة; ʿayn:
SOURCED — Shatibiyyah wajhan {4,6} with ISHBA' 6 muqaddam (see addendum),
canonical 6.
Trigger: (surah, ayah) ∈ the 30-entry table, word 0 letters identity-checked.
Delta: letters -> name segs (each name its own recitation word); madda
witnesses carried (name madd or 'ayn ConsSeg). Name-final sukun = MARKED
(izhar default at يس/ن junctions per Shatibiyyah; R012-class knob later).
Sites: 29 openings + 42:2. Tests: tests/test_muqattaat.py.

## SPEC-012 — السين والصاد (R012, P1)
Basis: Shatibiyyah farsh: يبصط 2:245 و بصطة 7:69 بالسين للحفص من طريق
الشاطبية (mashhur); المصيطرون 52:37 بالصاد مقدم والسين جائز; بمصيطر 88:22
بالصاد. Witness: small seen (Tanzil 06DC/06E3; KFGQPC 06DC).
Delta: SAD -> SEEN where knob true. Tests: tests/test_special_words.py.

## SPEC-110 — همزة الوصل ابتداءً (R110, P3)
Basis: al-Jazariyyah «وَابْدَأْ بِهَمْزِ الْوَصْلِ مِنْ فِعْلٍ بِضَمْ / إِنْ
كَانَ ثَالِثٌ مِنَ الْفِعْلِ يُضَمْ / وَاكْسِرْهُ حَالَ الْكَسْرِ وَالْفَتْحِ»;
article -> fatha. Implementation: article detect (wasla+lam); verbs by
third-slot haraka (gemination occupies two slots; hamza is slot 1); damma
'arida list (امشوا اقضوا ابنوا ائتوا) is word-list gated — none ayah-initial;
lands with resume-anywhere P2. Noun set (اسم ابن ابنت امرئ امرأت اثنين
اثنتين) -> kasra — subsumed by the default-kasra branch until the word-class
table lands. Tests: corpus totality + 1:6 golden.

## SPEC-120..122 — أحكام الوقف (R120/121/122, P4)
Basis: al-Jazariyyah باب الوقف; iskan the mashhur (rawm/ishmam variant
enumeration deferred to VariantPolicy). 'Iwad: tanween-fath -> fatha + alef
(2) at waqf; seat silent in wasl. Taa marbuta -> haa sakin. Tests:
tests/test_phones_core.py (112:1/112:4), tests/test_madd.py.

## SPEC-130..134 — الوصل والالتقاء (R130/131/133/134, P5)
R130 wasl elision (mid-segment hamzat wasl deleted). R131 iltiqa' al-sakinayn:
madd shortened before exposed sakin (قَالُوا ٱدْعُ); tanween -> noon al-wiqaya
with kasra (عُزَيْرٌ ٱبْنُ class); written connective harakat asserted from
dabt, never synthesized. R133 lam shamsiyya via the bare-before-shadda dabt
gate (kamil idgham, article lam consumed); qamariyya lam carries marked sukun
(izhar) — both flow from the dabt uniformly. R134 lam al-jalala: implicit
alif {2} inserted after the geminated lam of الله/لله; tafkheem by preceding
vowel (R212). Basis: Tuhfa/Jazariyyah + rasm convention. Tests:
tests/test_phones_core.py (1:1, 112:1), tests/test_noon_rules.py (1:6, 2:180).

## SPEC-150/152 — أحكام الميم الساكنة (R150/R152, P7)
Basis: Tuhfa باب الميم الساكنة: ikhfa shafawi before ب; idgham mithlayn
before م (dabt-marked, seg-level); izhar before the rest («وَاحْذَرْ لَدَى
وَاوٍ وَفَا أَنْ تَخْتَفِي» — warning only, no phonetic change). Delta:
MEEM -> MEEM_MUKHFAH + ghunna before ب. Tests: 1:7 izhar; iqlab/ikhfa sites.

## SPEC-160/161 — الإدغام العام (R160/R161, P8 + seg-level)
Mutamathilayn saghir: dabt-marked sites via bare-before-shadda; unmarked
junctions (letter-name chains) via the phone-level pass; sakt blocks; madd
letters never merge (قَالُوا۟ وَ…). Mutajanisayn: kamil sites dabt-marked;
naqis-ط (بَسَطتَ 5:28, أَحَطتُ 27:22, فَرَّطتُمْ 12:80): tah kept, qalqalah
suppressed, itbaq retained (R161 note in P11). Mutaqaribayn ق↔ك (77:20:
kamil — tahrir-fixed for this tariq, فريدة الدهر 1:444 «ألم نخلقكم
بالإدغام الكامل»; al-Nashr 1:221 validates both wajhs, kamil «أصح قياسًا»),
ل↔ر (dabt-marked; sakt-blocked at 83:14). يلهث ذلك (7:176) and اركب معنا
(11:42): kamil idgham SINGLE WAJH for Hafs — he is among الباقين of
Shatibiyya bayt 284 (سراج القارئ 1:100-101; إبراز المعاني 1:199-200).

## SPEC-170 — الغنة (R170, P9)
Geminated ن/م -> ghunna mushaddadah (أكمل ما تكون). Duration is a DURATION —
prescription classes are CONVENTION; realized length comes from alignment.

## SPEC-200..202 — القلقلة (R200-202, P11)
Basis: Tuhfa «قَلْقَلَةٌ قُطْبُ جَدٍ»; sughra mid-word sakin, kubra at waqf,
akbar on geminated waqf (وَتَبَّ). Suppressed under assimilation (deleted
letters) and naqis-ط.

## SPEC-210..214 — التفخيم والترقيق (R210-214, P12)
Isti'la «خُصَّ ضَغْطٍ قِظْ» mofakham (with kasra: low_mofakham — CONVENTION,
oracle-comparable 3-level scheme). Reh table per al-Jazariyyah باب الراءات:
voweled by its own haraka; sakin by the preceding (kasra 'arida keeps
tafkheem; same-word isti'la after -> tafkheem: قِرْطَاس مِرْصَاد فِرْقَة
إِرْصَاد, فرق khilaf knob pending); pausal by pre-pausal context (yaa sakin
-> tarqeeq). Lam al-jalala by preceding vowel. Vowels/madds inherit their
host consonant. Ikhfa carrier assumes the trigger letter's tafkheem.
Khilaf-word knobs (فرق القطر مصر نذر يسر) land with config expansion.

## SPEC-220..222 + SPEC-132 — أحداث حفص المفردة (P13)
Sakt (Shatibiyyah for Hafs): 18:1, 36:52, 75:27, 83:14 obligatory; 69:28-29
transmitted on wasl. KFGQPC witnesses all five with small seen. v1 implements
the three mid-ayah sites; ayah-boundary sakts (18:1→2, 69:28→29) land with
concat/waqf support. Ishmam 12:11 (attribute event; rawm variant via
VariantPolicy later). Imala 11:41 (the mark occupies the vowel slot:
FATHA_IMALA inserted + ALEF_IMALA + reh moraqaq). Tasheel 41:44
(HAMZA_MUSAHHALA + fatha replacing the marked seat). Naql 49:11: carried by
the rasm/dabt (kasra written on the lam) — no special handling needed,
asserted by corpus totality. نخلقكم 77:20: kamil via dabt (qaf bare + kaf
shadda). Tests: tests/test_oneoffs.py.

## SPEC-011 addendum — sourced rulings (2026-08-15)

**Letter-name junctions carry the noon-sakinah rules** (ijma'-level for the
ikhfa sites): طسٓ تِلْكَ = ikhfa of سين's noon at the taa — حجة القراءات
1:521 («مخفاة عند التاء غير مدغمة إجماعًا»), العنوان 1:142, الوجيز 1:83,
الوافي 1:136. Principle: المحتسب 1:241 (عين صاد، عين سين قاف).

**يس/ن izhar before waw is the ONLY Shatibiyyah wajh for Hafs** — الشاطبية
بيت 281 «ويَاسِينَ أَظْهِرْ عن فتىً حقُّه بدا ونونَ», فتح الوصيد 1:444,
الوافي 1:136, هداية القاري 1:294 («وجوب الأخذ بوجه الإظهار»), السبعة 1:537.
Idgham for Hafs exists only via عمرو بن الصباح/زرعان in النشر 2:17 — a
non-Shatibiyyah tariq; never offered inside this engine's default config.
Ta'lil: نية الوقف/الانفصال الحكمي — مشكل إعراب القرآن 2:598, إبراز المعاني
1:198.

**عَيْن of كهيعص/حمعسق — SOURCED (canonical flipped 4→6, 2026-08-15):**
Shatibiyyah allows tawassut 4 and ishba' 6 ONLY; **ishba' muqaddam** —
الشاطبية بيت 177 «وَمُدَّ لَهُ عِنْدَ الْفَوَاتِحِ مُشْبِعًا / وَفِي عَيْنٍ
الْوَجْهَانِ وَالطُّولُ فُضِّلَا» (متن الشاطبية 1:14); إبراز المعاني 1:122
(«الوجهان» = التوسط والطول، لا القصر); سراج القارئ 1:60; فتح الوصيد 1:336
(«وإنما فُضِّل الطول لأنه قياس مذهبهم»); هداية القاري 1:343 («الإشباع هو
الأفضل والمقدم في الأداء... وإذا قرئ بالإشباع فالمد من قبيل المد اللازم
الحرفي المخفف، وإذا قرئ بالتوسط فمن قبيل مد اللين»). Qasr = Tayyibah only
(طيبة النشر بيت 172 «فالثلاثة لهم»; شرح الطيبة 1:75; النشر 1:348 — the
three madhahib incl. متأخري العراقيين قاطبة for qasr). Classification: مد
لين لازم حرفي مخفف (النويري 1:399 «اللازم غير المشدد عين... خاصة»; the
ikhfa of its noon does NOT make it muthaqqal — muthaqqal = idgham only).
Both sites (19:1, 42:2) identical. Engine: allowed {4,6}, canonical
madd_ain_len=6, scoring {2,4,6}.

**الٓمٓ + اللَّهُ (3:1→2) wasl wajh table** (for the concat phase; v1's
ayah-end waqf on 3:1 = lazim 6, already correct): meem takes FATHA (السبعة
1:199; 'illa: النويري على الطيبة 2:231 — تخلص من الساكنين واختير الفتح),
jalala wasl-hamza drops, and the مِيم yaa-madd has TWO wajhs — ishba' 6
(الاعتداد بالسكون الأصلي, «وهو المفضل» القول السديد 1:111) or qasr 2
(الاعتداد بالحركة العارضة) — NO tawassut (غيث النفع 1:129, الميسر 1:50).
Canonical for the future concat config: 6.

## SPEC-132 addendum — sakt rulings sourced (2026-08-15)

**The four sakts are LAZIM in wasl for Hafs/Shatibiyyah** (wasl without sakt
is not a wajh of this tariq; the khilaf belongs to Tayyibah paths only) —
الشاطبية بيتا 830-831 «وسكتةُ حفصٍ دونَ قطعٍ لطيفةٌ / على ألفِ التنوينِ في
عِوَجًا بَلا * وفي نونِ مَنْ راقٍ ومَرْقَدِنا ولا / مِ بَلْ رانَ» (متن
1:66); الوافي 1:310; سراج القارئ 1:277; إبراز المعاني 1:565 («دون قطع نفس؛
لأنه في وقفه واصل»). Sites: 18:1→2 (on the 'IWAD ALIF — the tanween
becomes alif even in wasl: 'iwajaa + sakt + qayyiman; concat engine must
NOT restore tanween), 36:52 (alif of مرقدنا), 75:27 (noon of من — izhar
enforced), 83:14 (lam of بل — izhar enforced).

**Sakt duration**: the transmitted description is «سكتة لطيفة، دون زمن
الوقف، من غير تنفس» (النشر 1:240-241 — and it notes the imams' wordings
imply VARIATION in length); the ~2-haraka quantification is a later-manual
convention (هداية القاري 1:408-409 «بقدر حركتين»; غاية المريد 1:234).
Engineering consequence: sakt length is a DURATION for the alignment stage
to measure (convention prior 2, scoring {1,2,3}); prescription is the
breathless pause itself, not a count.

**ماليه هلك (69:28→29) wasl wajhan** (concat phase): (1) MUQADDAM — izhar
WITH the latif sakt on the sakt-haa (هداية القاري 1:236-237 «وهو الأرجح
والمقدم في الأداء وعليه الجمهور»; النشر 2:21-22 quoting الداني «لزمه أن
يقف على الهاء... وقفة لطيفة في حال الوصل من غير قطع» + ابن الجزري «وهو
الصواب»; فتح الوصيد 1:434; غيث النفع 1:601); (2) idgham of the two haas
without sakt (the Shatibiyya's general mathalayn rule, bayt 276, with this
site debated because the first haa is haa al-sakt).

**Anfal→Tawba junction** (concat phase): three wajhs by free choice, ALL
without basmala — waqf (with breath) / sakt / WASL with IQLAB of the
tanween at براءة's ba ('aliimum-baraa'atun) — الشاطبية «ومهما تصلها أو
بدأت براءةً...لستَ مبسملا»; غيث النفع 1:270 (explicitly affirms sakt's
validity); البدور الزاهرة 1:133.

**No general pre-hamza sakt for Hafs/Shatibiyyah**: sakt is سماعي —
«مقيد بالسماع والنقل» (النشر; الإتقان 1:299); the general saakin-before-
hamza sakt is a Tayyibah-path feature. The engine's absence of it is
therefore sourced, not an omission.

## SPEC-210 addendum — the raa khilaf table, sourced (2026-08-15)

Master summary (هداية القاري 1:133): eleven two-wajh waqf raa'at — TEN with
tarqeeq muqaddam, ONE (مصر) with tafkheem muqaddam.

| word | sites | wasl | waqf (sukun mahd) | 'illa |
|---|---|---|---|---|
| فِرْقٍ | 26:63 | wajhan; TARQEEQ tarjih («المأخوذ به المعول عليه»; الداني: «الوجهان جيدان» — فتح الوصيد 1:526, سراج القارئ 1:120; الشاطبية «وخلفهم بفرق جرى») | tafkheem mashhur (qaf's kasra vanishes) | maksur isti'la weakened between two kasras |
| مِصْرَ | 12:21, 12:99, 43:51, 10:87 (مِصْرًا 2:61 excluded — munawwan, alif waqf, tafkheem) | tafkheem only (fatha) | wajhan; TAFKHEEM muqaddam (النشر 2:105 «وأختار في مصر التفخيم») | sad = hajiz hasin musta'li |
| الْقِطْرِ | 34:12 | tarqeeq only (kasra) | wajhan; TARQEEQ muqaddam (النشر: «وفي القطر الترقيق نظرًا للوصل وعملًا بالأصل»; غيث النفع 1:481) | wasl-regard + asl |
| وَنُذُرِ | 54:16,18,21,30,37,39 | tarqeeq (kasra) | wajhan; TARQEEQ muqaddam | deleted yaa of نُذُرِي (takhfeef); النُّذُر article-forms are OUTSIDE the khilaf (general tafkheem after damma) |
| يَسْرِ | 89:4 | tarqeeq | wajhan; tarqeeq AWLAA (النشر 2:110-111) | deleted yaa (takhfeef) |
| أَسْرِ/فَأَسْرِ | 20:77, 26:52, 11:81, 15:65, 44:23 | tarqeeq | wajhan; TARQEEQ muqaddam | yaa deleted lil-BINAA (amr mu'tall); «فرقًا بين كسرة الإعراب وكسرة البناء» النشر 2:110 |

Rawm at waqf follows the wasl ruling everywhere (معجم علوم القرآن 1:155).
بِشَرَرٍ is NOT a Hafs khilaf (that is al-Azraq's — النشر 2:98-99): Hafs
recites first reh mofakham (fatha), second moraqaq (kasra), waqf tafkheem.
Engine: firq_wasl_tafkheem=False (weakened-maksur-isti'la branch),
nudhur/yasr/asr waqf knobs default tarqeeq, misr True, qitr False.

## SPEC-170/214 addendum — ghunna doctrine sourced (2026-08-15)

**Maraatib al-ghunna** (grading layer's rank axis): the five-rank teaching
order — mushaddad > mudgham-naqis > mukhfa(+iqlab) > sakin-muzhar >
mutaharrik — is the later-masters' formalization (هداية القاري 1:187 «الأول
هو الأشهر والمعول عليه»); its classical root is comparative, not numeric:
الجعبري via لطائف الإشارات 1:350-351 «وهي في الساكن أكمل من المتحرك، وفي
المخفي أزيد من المظهر، وفي المدغم أوفى من المخفي» (also تنبيه الغافلين
1:78). Engine mapping: mushaddadah/idgham/ikhfa/asl + voweled=None.

**Ghunna duration — the decisive nass** (المرعشي via الميزان 1:123-124 و
نهاية القول المفيد): «لم أر في مؤلَّف تقدير امتداد الغنة في هذه المراتب...
والذي نقلناه عن مشايخنا... أن الغنة لا تزيد ولا تنقص عن مقدار حركتين
كالمد الطبيعي». So: (1) NO early source quantifies ghunna — the 2-count is
talaqqi-transmitted approximation, tempo-relative (النشر 1:213 رياضة
الألسن; الداني «ليس بين التجويد وتركه إلا رياضة القارئ»); (2) the COMPLETE
ghunna's duration is EQUAL across mushaddad/mudgham/mukhfa — ranks differ
in kamal, not measured time (against some modern shuruh making mushaddad
longest). This is the third doctrinal confirmation (after free-choice madd
and sakt) that duration belongs to MEASUREMENT: the engine's
LengthSpec(fixed {2}, scoring {1,2,3}) + alignment-realized design is
required by the sources, not merely convenient. Grading: rank = categorical
(from ghunna kind), length = measured.

**R214 ikhfa-tafkheem now sourced**: the ghunna of the mukhfah follows the
NEXT letter in tafkheem/tarqeeq at exactly FIVE letters ص ض ط ظ ق —
هداية القاري 1:181-183 («وبالاستقراء والتتبع... عند خمسة أحرف»; السمنودي
«وتتبع ما قبلها الألفُ والعكس في الغنِّ أُلِفْ»; السلسبيل الشافي «وفخِّم
الغنة إن تلاها حروف الاستعلاء لا سواها»), with the honest historical note:
no explicit early nass (مكي/الداني/النشر describe the mukhfah shifting
toward the next letter's makhraj — هداية القاري 1:67 — the tafkheem wording
is later). Engine's isti'la set includes غ خ but they are halqi-izhar
letters no mukhfah ever precedes — behaviorally the five-letter rule.

## SPEC-123 addendum — rawm & ishmam legality table, sourced (2026-08-15)

For the VariantPolicy waqf enumeration (P2-full):

**Rawm** («إسماع المحرك واقفًا بصوت خفي» — الشاطبية بيت 368; النشر 2:121
«النطق ببعض الحركة»; التيسير 58-59 «يدركه الأعمى بحاسة سمعه»): the
retained part is LESS than the dropped part; the "one-third" figure is a
later teaching approximation — «كل ذلك لا يضبط إلا بالمشافهة» (غاية
المريد 1:181-183; هداية القاري 2:510-511) — the FOURTH confirmation that
durations are measured, not prescribed. LEGAL on: marfu'/madmum and
majrur/maksur with LAZIMA haraka (i'rab or binaa) — الشاطبية أبيات
370-372. ILLEGAL on: fath/nasb (القراء خلافًا لسيبويه), 'arida harakat
(naql/iltiqa — they revert at waqf), tanween-fath ('iwad instead), taa
marbuta (the waqf-haa was never voweled — بيت 373; سراج القارئ 1:126-127),
meem al-jam'. Tanween damm/kasr: tanween drops, rawm runs on the base
haraka. Taa MAFTUHA words waqf on the taa itself -> rawm/ishmam by its
haraka (إتحاف 1:135-136). Effect on 'aared madd: rawm = wasl-like.

**Ishmam** («إطباق الشفاه بُعيد ما يُسكَّن لا صوت» — بيت 369): lip-rounding
IMMEDIATELY AFTER the iskan — «الفاء للتعقيب، فلو تراخى فإسكان مجرد»
(القسطلاني في الإتحاف 1:135) — with a gap for the breath (هداية القاري
2:511-512). VISUAL not auditory («يرى بالعين ولا يسمع بالأذن... لا يأخذه
الأعمى عن الأعمى») — hence represented as an ATTRIBUTE EVENT, not a phone
(consistent with the engine's 12:11 handling). LEGAL on damm/raf' ONLY.
Timing distinction: waqf-ishmam is post-iskan; the ishmam of تَأْمَنَّا
12:11 is CONCURRENT with the idgham sukun (غاية المريد 1:183-184) — the
two events are different rules and stay distinct in the engine.

## SPEC-200 addendum — qalqalah kayfiyya & maraatib, sourced (2026-08-15)

**Qalqalah is NOT a vowel** — the decisive nass: النشر 1:203 «وحسبانهم أن
القلقلة حركة، وليس كذلك؛ فقد قال الخليل: القلقلة شدة الصياح»; الزيادة
والإحسان 3:239-241; الميزان 1:80-81 warns that tilting it into any of the
three harakat «أدى إلى فساد المعنى». The BURST-COLOR question is an
UNRESOLVED khilaf among the later masters: follows-the-PRECEDING haraka
(هداية القاري 1:86-87 — «المشهور وعليه الجمهور، وانظر جهد المقل وشرحه»)
vs toward-FATH always (العميد 1:66; الروضة الندية 1:28-29 «عليه العمل»)
vs follows-the-next (weakest; refuted for waqf position). ENGINE
CONSEQUENCE: qalqalah stays a colorless burst ATTRIBUTE (no vowel-color
prescription); the grading layer may MEASURE burst spectral tilt as a
descriptive feature only. Sifat preserved through the burst: ط mofakham
+itbaq, ق mofakham, ب ج د muraqqaq (النشر 1:216 on guarding the baa's
tarqeeq with its shidda/jahr). Letter-strength orderings (ط>ق>rest per
itbaq/isti'la; المرعشي via تبصرة المريد: ط ثم ج ثم الباقية) are
descriptive, not prescriptive.

**Maraatib**: the engine's three grades are sourced — sughra (connected
sakin), kubra (waqf, mukhaffaf), AKBAR (waqf, mushaddad) — هداية القاري
1:84-85; بغية المستفيد 1:50-52 («فكأنك تقلقل مرتين»); السمنودي «كبيرةٌ
حيث لدى الوقف أتت / أكبرُ حيث عند وقف شُدِّدت» (غاية المريد 1:146). The
two-grade taxonomy (المختصر المفيد 1:644; تيسير أحكام التجويد 1:23-25)
and the objection to isolating the mushaddad (أيمن سويد via الميزان 1:79)
are recorded; the root doctrine is just الجزرية «وبيِّنْ مقلقلًا إن سكنا
وإن يكن في الوقف كان أبينا».

## SPEC-123 completion — rawm/ishmam × 'aared madd (2026-08-15)

Rawm = wasl-like: the 'aared madd takes QASR 2 ONLY. Ishmam rides the
sukun: 2/4/6 all run. Wajh arithmetic for the variant enumerator: maksur
ending = 4 awjuh (sukun×3 + rawm·2); madmum ending = 7 awjuh (sukun×3 +
ishmam×3 + rawm·2) — العميد 1:102; القول السديد 1:128; ظاهرة المد في
الأداء القرآني 1:406; فتح رب البرية 1:114. OPEN THREAD for the expert
pass: rawm/ishmam in haa al-damir (the khilaf answer was cut; not
asserted).

## SPEC-004b — the harakah as time-unit: the alignment doctrine (2026-08-15)

THE foundational nusus for the S3/S4 duration pipeline:

1. **Proportionality is prescribed** — al-Maliqi, الدر النثير 2:216-217:
   «يتناسب المد والتحريك، ولو أن المسرع بالحركات أطال المد، والمسكن
   للحركات قصر المد، لأدى ذلك إلى تشتت اللفظ وتنافر الحروف». Madd
   durations MUST be proportional to the same performance's haraka
   durations — this IS the self-calibration ratio method.
2. **Tabee'i is the unit** — al-Sakhawi, جمال القراء 648-649: the tabee'i
   is «مقدار الألف», the hamz/sukun madd «ضعفي مدهن» (its double), AND
   the unit is per vowel QUALITY: «مقدار ياء إن كان ياء، ومقدار واو إن
   كان واوًا» → the aligner may calibrate a/i/u units separately.
3. **Absolute time varies with tempo** — Ibn Mihran via النشر 1:316-317
   (muhaqqiqun 4 alifs vs hadirun 2 on the lazim); Ibn al-Badhish,
   الإقناع 158-159 («المد إنما يكون على حسب التحقيق أو الحدر»).
4. **The counts are approximations; talaqqi rules** — النشر 1:326 (via
   إذهاب الحزن 259): «المقدر غير محقق، والمحقق إنما هو الزيادة، وهذا ما
   تحكمه المشافهة» — the FIFTH measure-not-prescribe confirmation.
5. **The haraka = time to utter a voweled letter AT THE READER'S OWN
   TEMPO** — العميد 82-83 (explicitly rejecting fixed external units);
   الميزان 167-168; the alif↔haraka table (2=alif, 4=2, 6=3 — الميزان
   168; معجم علوم القرآن 1:127).
6. **The finger method REFUTED for exactly the absolute-threshold failure
   mode** — فتح رب البرية 76: «غير منضبط مع عمر القارئ... لا يتناسب مع
   سرعات القراءة»; العميد 82-83; الميزان 166-167 («محدث في المائة
   الأخيرة»).

ENGINEERING CONSEQUENCE (now doctrine, not design taste): the S4 gate
measures every duration in units of the clip's own tabee'i (optionally
per-quality a/i/u units per al-Sakhawi); ratios are the preserved object;
absolute milliseconds are never thresholds. The blind fixed-madd recovery
gate is the empirical test that the measured unit behaves as the sources
describe.

## SPEC-005 — the basmala junction system, sourced (2026-08-15)

For the concat/junction generator. Hafs separates every pair of surahs
with the basmala except Anfal->Tawba (التيسير 1:17-18).

**Three permitted joins** (هداية القاري 2:568, naming Hafs explicitly):
(1) qat' al-jamee' — stop on the surah end, stop on the basmala, start
the next; (2) qat' al-awwal + wasl 2-3 — stop on the surah end, join
basmala to the next surah's start; (3) wasl al-jamee' — one breath across
all three. **The FORBIDDEN fourth**: joining the surah's end to the
basmala then stopping on it — الشاطبية بيت 107 «ومهما تصلها مع أواخر
سورةٍ فلا تقفنَّ الدهر فيها فتثقلا»; 'illa: «التسمية للمستأنفة لا
للسالفة» (فتح الوصيد 1:276-277; الوافي 1:49-50). The generator must
REFUSE to synthesize join #4.

**Preference**: all three are riwaya-valid takhyeer; the shurrah's
ikhtiyar is #2 («هذا هو المختار» — سراج القارئ 1:30-31; «والأول أولى» —
فتح الوصيد). Concat default = #2; knob for #1/#3. The Tanzil embedded-
basmala wasl dabt at 95:1/97:1 (beh idgham from فَٱرْغَب/وَٱقْتَرِب) is
join #3's pointing, witnessed in the rasm.

**Nas -> Fatiha** (الحالّ المرتحل): the same three wajhs run (النشر 1:263
«ولو وصلت لفظًا فإنها مبتدأ بها حكمًا»; هداية القاري 2:593-594).

**Mid-surah starts**: basmala is takhyeer for every start below a surah
head (الشاطبية بيت 106 «وفي الأجزاء خُيِّر من تلا»; التيسير 1:18; النشر
1:265 — Iraqis prefer with, Maghariba without; no binding wajh for Hafs).
Adab constraint: avoid joins that produce a repugnant meaning (الزيادة
والإحسان 3:383) — out of engine scope, noted for the corpus builder.

## SPEC-183 — haa al-kinaya: the complete Hafs farsh, sourced (2026-08-15)

General rule (الشاطبية بيت 158-159; سراج القارئ 1:45-48; الوافي 1:67-72):
the pronoun haa takes SILAH (waw/yaa kubra-eligible) when it sits between
two voweled letters; NO silah when the preceding letter is sakin
(«وما قبله التحريك للكل وصلا» ... «وإسكانها في الوصل عن كل من تلا»).
The rasm carries the outcome: small waw/yaa = silah, bare haraka = qasr,
sukun head = iskan. Our engine reads the rasm — R183 is the ONLY added
semantics (silah drops at waqf: «الصلة تسقط في الوقف» — سراج القارئ 1:45;
هداية القاري 1:359).

**The six Hafs specials** (all verified in the engine, goldens in
tests/test_haa_kinaya.py):

| Site | Ruling | Source |
|---|---|---|
| يَرْضَهُ لَكُمْ 39:7 | damm bila silah (qasr) | الشاطبية 164 «وإسكان يرضه يمنه لبس طيب بخلفهما والقصر فاذكره نوفلا»؛ سراج القارئ 1:47؛ إبراز المعاني 1:109-110؛ النشر 1:306 |
| فِيهِ مُهَانًا 25:69 | KASR + SILAH — the sole Hafs silah after a sakin | الشاطبية 159 «وفيه مهانا معه حفص»؛ فتح الوصيد 1:320: tawjeeh = madd yuliqu bil-mubalagha fil-ihana |
| أَرْجِهْ 7:111، 26:36 | haa SAKIN (iskan) | الشاطبية 166-167 «وأسكن نصيرا فاز»؛ التيسير 1:29؛ سراج القارئ 1:48 |
| فَأَلْقِهْ إِلَيْهِمْ 27:28 | haa SAKIN | الشاطبية 161 «وعنهم وعن حفص فألقه ويتقه»؛ سراج القارئ 1:46؛ الوافي 1:69؛ النشر 1:305 |
| وَيَتَّقْهِ 24:52 | QAF sakin + haa kasr bila silah | الشاطبية «وقل بسكون القاف والقصر حفصهم» (بيت 162 في ترقيم، 168 في آخر)؛ هداية القاري 1:359 |

**The two haraka-specials** (haa takes DAMM where qiyas suggests kasr;
rasm carries both):
- أَنسَىٰنِيهُ إِلَّا 18:63 — damm bila silah (sakin yaa precedes).
- عَلَيْهُ ٱللَّهَ 48:10 — damm bila silah. Both: الشاطبية بيت 165
  «وعنه أنسانيه وعليه الله بالضم ذكرا»؛ التيسير 1:30؛ النشر 1:305.

Engine status: all EIGHT sites emit the sourced phones from the pinned
rasm alone (verified 2026-08-15, both editions agree). No code change was
needed — this round was pure verification + goldens.

**Second-retrieval refinements (2026-08-15, same day):**
- **The يَرْضَهُ «qasr» carries an interpretation khilaf**: Ibn al-Qasih
  glosses it «يعني باختلاس ضمة الهاء» (سراج القارئ 1:47) while the
  received Hafs ada' is a FULL damma bila silah (and Abu Shama's «له
  الرحب» commends the qasr's breadth — إبراز المعاني 1:109-110). Full-vs-
  ikhtilas is a sub-haraka DURATION distinction: the engine rightly emits
  damma with no silah and takes no side; only measurement could — the
  SIXTH measure-not-prescribe confirmation.
- **Tawjeeh recorded**: فيه مهانا = jam' bayna al-lughatayn, with the
  tashni'-on-the-sinner purpose also transmitted (فتح الوصيد 1:317-318؛
  إبراز المعاني 1:105-106); iskan = lughat أزد السراة, qasr/ikhtilas =
  lughat عقيل وكلاب, silah = the asl (الهادي شرح الطيبة 1:161).
- **Bayt texts pinned** (numbering varies by matn edition): 158-159 the
  general rule; 160 يؤده/نوله/نصله/نؤته (OTHER readers' iskan — Hafs
  keeps silah there, rasm agrees); 161-162 فألقه/يتقه; 164 يرضه;
  166-167 أرجه.
- The hasr is re-confirmed complete: five silah/qasr/iskan specials +
  the two damm specials = our eight sites exactly.

**RESOLVED (5th retrieval, 2026-08-15) — rawm/ishmam on the pronoun haa:**
the three madhahib of النشر 2:124-125 with Ibn al-Jazari's own tarjih:
jawaz mutlaqan (التيسير، التجريد، التلخيص، الإرشاد، الكفاية؛ اختيار ابن
مجاهد) / man' mutlaqan (the haraka is 'arida; ZAHIR of the Shatibiyyah;
al-Dani outside al-Taysir: «الوجهان جيدان») / **TAFSIL — man' after damm,
sakin waw, kasr, or sakin yaa; jawaz after fath, alif, or sakin sahih**
(qat' by مكي وابن شريح والهمداني والحصري؛ «وهو أعدل المذاهب عندي» —
النشر 2:124؛ الطيبة «وخلف ها الضمير وامنع في الأتم من بعد يا أو واو أو
كسر وضم» — شرح الطيبة 1:142). Followed by الإتحاف 1:135-136، غيث النفع
1:86-87، هداية القاري 1:322، 1:327-328.

Per-site under the tafsil (implemented in `waqf.isharah_modes`, goldens
in tests/test_isharah_gate.py):

| final | context | modes |
|---|---|---|
| يَرْضَهُ 39:7 | damm after fath | sukun + rawm + ishmam |
| فِيهِ مُهَانًا 25:69 | kasr after sakin yaa | sukun only |
| وَيَتَّقْهِ 24:52 | kasr after sakin sahih | sukun + rawm («ويتقه لحفص» named in al-Nashr's jawaz examples) |
| أَنسَىٰنِيهُ 18:63 | damm after sakin yaa | sukun only (الكنز 1:334) |
| عَلَيْهُ ٱللَّهَ 48:10 | damm after leen yaa | sukun only (عليه = al-Nashr's own man' example) |
| أَرْجِهْ / فَأَلْقِهْ | haa already sakin | sukun only (nothing to indicate) |

General finals stay on SPEC-123 (rawm: damm+kasr; ishmam: damm only;
neither on fath). **Haa as-sakt takes neither, ever** — it is a sakin haa
with no underlying haraka («هاء ساكنة زيدت في الوقف لبيان الحركة» —
الإقناع لابن الباذش 1:244; ثابتة ساكنة وصلًا ووقفًا لمن أثبتها, which
Hafs does at all nine sites: كتابيه ×2، حسابيه ×2، ماليه، سلطانيه،
ماهيه، يتسنه، اقتده؛ لطائف الإشارات 9:75). The ماليه-هلك wasl khilaf
(izhar+sakt / idgham) is a separate wasl matter, untouched. A modern
manual (مقدمات في علم القراءات 200) permits isharah at أنسانيه — contra
the tafsil nass and al-Kanz's explicit listing; recorded and rejected.

## SPEC-184 — the seven alifs (thabita waqfan, mahdhufa waslan), sourced (2026-08-15)

The class: أنا (حيث وقع)، لكنا 18:38، الظنونا 33:10، الرسولا 33:66،
السبيلا 33:67، سلاسلا 76:4، قواريرا الأولى 76:15 — alif written, marked
with the rectangular zero, dropped in wasl and realized at waqf for Hafs
(فتح رب البرية 1:122؛ مباحث في علم القراءات 1:105).

**Sources per site:** الظنونا/الرسولا/السبيلا: الشاطبية «وحق صحاب قصر
وصل الظنون والرسول السبيلا وهو في الوقف في حلا» — Hafs drops waslan,
keeps waqfan (سراج القارئ 1:325-326؛ التيسير 1:177-178؛ السبعة 1:519).
Tawjeeh: ru'us aayaat; the fawasil run like qawafi in taking alif
al-itlaq (حجة القراءات 1:572-574؛ الهادي 3:142؛ النشر 2:347-348: mushaf
ijma' on this rasm). — أنا: alif realized only at waqf, حفظًا للحركة
like a waqf-haa (جمال القراء 1:747-748؛ حجة القراءات 1:142؛ الوافي
1:222-223). — لكنا: asl لكنْ أنا, naql + idgham; waqf bil-alif is ijma',
wasl-drop for Hafs (الحجة للفارسي 5:144-146؛ حجة القراءات 1:416-417).
— قواريرا: first (ayah head) waqf WITH alif, second waqf WITHOUT, both
tanween-less and alif-less in wasl (التيسير 1:217-218؛ جامع البيان
4:1678-1679؛ السبعة 1:664-665). The difference: only the first is a
fasila.

**Dabt-as-oracle again:** the pinned rasm encodes the entire system —
U+06E0 (rectangular zero) ×66 = exactly أنا×61 + لكنا + the Ahzab three
+ قواريرا-1 (wasl-drop, waqf-realize); U+06DF (round zero) = never
realized, and it is what سلاسلا and قواريرا-2 carry. So for سلاسلا —
Shatibiyyah waqf WAJHAN (ithbat/hadhf, طيبة النشر «سلاسلا نون ... خلفهما
صف معهم الوقف امددا»؛ النويري 2:603؛ تحبير التيسير 1:599) — **the printed
dabt itself selects the hadhf wajh**; the taqdim is genuinely disputed
(الحذف: الضباع صريح النص 25؛ العميد 1:160-161 «مراعاة للوصل» — الإثبات:
هداية القاري 2:526). Engine: wasl (all v1 emits) is wajh-invariant;
the ithbat-alif waqf variant = P2-full knob `salasila_waqf_alif`
(default False = the printed dabt).

**آتاني 27:36** (yaa zawaid that behaves like idafa): wasl = yaa
maftuha (rasm: small yeh U+06E6 + fatha, engine reads it); waqf for
Hafs = wajhan ithbat-sakina / hadhf (الشاطبية بيت 429 «وفي النمل آتاني
ويفتح عن أولي حمى وخلاف الوقف بين حلا علا»؛ إبراز المعاني 1:309-310؛
الدر النثير 4:197). **Taqdim RESOLVED from the local corpus: ITHBAT of
the sakin yaa is muqaddam** — «والإثبات هو المقدم في الأداء على الحذف
إن وقف بهما معًا» (هداية القاري 2:544-545؛ ويوافقه الوجيز في علم
التجويد 1:55-56 «والإثبات هو المقدم في الأداء»). Disambiguation: the hadhf-wujub
lists at هداية القاري 1:290-295 are TAYYIBA qasr-munfasil tahrir
obligations («الأحكام التي تجب لحفص حال القصر في المنفصل من طريق طيبة
النشر» 1:291-292) — outside this tariq. P2-full knob
`aataani_waqf_yaa` default True (ithbat).

**أيه ×3 (43:49، 24:31، 55:31) — RESOLVED from the local corpus,
cross-validated by a second remote retrieval**: الشاطبية بيت 382 «ويا
أيها فوق الدخان وأيها لدى النور والرحمن رافقن حملا»؛ الوافي 1:182
(«فإذا وقفوا أسكنوا الهاء... مرسوم المصاحف... بحذف الألف»). Waqf
bil-haa (sakin) following the rasm for Hafs — «فوقف عليه بالألف في
المواضع الثلاث على الأصل خلافًا للرسم أبو عمرو والكسائي ويعقوب، ووقف
عليها الباقون بالحذف اتباعًا للرسم» (النشر 2:142 باب الوقف على مرسوم
الخط، و2:332)؛ «فتعيّن للباقين الوقف على الهاء من غير ألف اتباعًا
للرسم» (سراج القارئ 129-131 ترقيم الشاملة)؛ غيث النفع 531، 568
(«النحويان يقفان بالألف... والباقون بالسكون تبعًا للرسم»)؛ الإتحاف 410.
Ibn 'Amir's wasl haa-damm is his own. Wasl phones verified at all
three (article junction unaffected); waqf = plain P4 iskan, no alif
logic for Hafs. Goldens: tests/test_ayyuha_and_aataani.py. Bonus: the
same النشر page (2:142) carries the haa-sakt seven-word hasr — a
further anchor for SPEC-183's haa-sakt section.

Goldens: tests/test_seven_alifs.py (ayah-final ithbat as tabee'i {2} at
the four v1-scope sites; wasl deletions; آتاني yaa). All verified with
zero engine changes — the U+06E0/06DF decode tables already carried it.


## SPEC-003 amendment — the '~' ghunna axis (2026-08-15)

Token grammar: `BASE (shadda?) ('^'?) ('~'?) (haraka?) (residual?) (':LEN)?`.
The bijection build against the legacy 250-unit vocab surfaced a design
gap: idgham bi-ghunna into waw/yeh is NAQIS — the target is nasalized but
not geminated — so neither shadda nor a mukhfah base marked it, and the
token stream rendered a rule-bearing acoustic event invisible (the legacy
vocab HAD dedicated units for it). '~' (ASCII, normalization-immune like
'^') now marks the naqis target: و~َ ي~َ و~ُ ي~ُ و~ِ — 2,430 corpus
instances. Every ghunna carrier is now token-visible (ں، ۾، نّ، مّ، and
'~'); ghunna DURATION stays metadata (v1 decision unchanged). Vocab
229 -> 234, blank 233; determinism freeze log entry 2026-08-15f (phones
untouched, proven by sole-src-delta).

**Warm-start map** (`artifacts/tokenizer_tj1/bijection_old250.json`):
6,236/6,236 ayat align 1:1 after run-split reconciliation; 220 observed
mappings, 0 conflicts, 13 unmapped tokens carry warm-start parents.
Old-vocab granularity limits recorded as observed_split entries: ي:6
(leen-7 render vs their 5-cap — their engine never produced 'ayn 6),
نّ pausal (our ghunna-4 render vs their 3-cap — their Ghonna-3 path,
see the differential verdicts), ٲَ (they never fused the musahhala with
its haraka).


## SPEC-123 addendum — the five sukun-only asnaf (2026-08-15, local corpus)

النشر 2:122-124 (باب الوقف على أواخر الكلم): waqf divides into three
qisms — sukun-only / damm-class (sukun+rawm+ishmam) / kasr-class
(sukun+rawm) — and the sukun-only qism has exactly FIVE asnaf:
(1) sakin in wasl (فلا تنهر); (2) fath-final without tanween and without
naql (لا ريب); (3) **the waqf-haa replacing ta marbuta** (الجنة — the haa
carries no i'rab; tanbih 2:126: stopping on a word WRITTEN with open taa
keeps the isharah, for the taa itself bears the haraka); (4) meem
al-jam'; (5) **any 'arid haraka** (naql / iltiqa al-sakinayn:
عليهمُ القتال). Implemented: `isharah_modes` gains `ta_marbuta` and
`arid_haraka` flags (asnaf 1, 2, 4 already fall out of the haraka logic).

Terminology nass (النشر 2:126): «فالروم عند القراء غير الاختلاس، وغير
الإخفاء أيضًا. والاختلاس والإخفاء عندهم واحد» — and بعضهم عبّر بالإخفاء
عن الروم «توسعًا» كما في تأمنا. This refines SPEC-183's يرضه note: Ibn
al-Qasih's «يعني باختلاس» gloss sits inside a known terminological
looseness the Nashr itself flags.

## SPEC-214b addendum — sifat matrix completed (2026-08-15)

Self-audit against the canonical mnemonic sets confirmed every existing
set cell-for-cell, and found TWO classical sifat missing from the
projection: **inhiraf (ل ر)** and **idhlaq/ismat (فر من لب)**. Both
added — the table now carries the Jazariyya's full seventeen. (Leen as a
sifa needs neighbor context and stays with the madd machinery.)

**Bayt-verified (17th RAG round)**: the Jazariyya's sifat bayts 20-26
(المقدمة 1:59-61) list all thirteen named sets exactly as implemented —
«مهموسها فحثه شخص سكت / شديدها لفظ أجد قط بكت / وبين رخو والشديد لن عمر
/ وسبع علو خص ضغط قظ حصر / وصاد ضاد طاء ظاء مطبقه / وفر من لب الحروف
المذلقه / صفيرها صاد وزاي سين / قلقلة قطب جد واللين / واو وياء سكنا
وانفتحا قبلهما / والانحراف صححا في اللام والرا وبتكرير جعل / وللتفشي
الشين ضادا استطل»؛ الأضداد بـ«والضد قل» (النويري 1:237-238؛ استخراج
الصفات: هداية القاري 1:93).

**Count khilaf**: 17 = the jumhur and Ibn al-Jazari (هداية القاري 1:78);
14 = البركوي (drops idhlaq/ismat/inhiraf/leen, ADDS ghunna — الوجيز
1:10-11); 16 = attributed to al-Sakhawi (+الهوائي for alif — معجم علوم
القرآن 1:175). Idhlaq/ismat have no ada' effect: «لا دخل لهما في تجويد
الحروف» (هداية القاري 1:83) — kept for completeness, articulatorily
inert. An earlier attribution of the trimmed count to al-Mar'ashi was
NOT confirmed by the sources and is withdrawn.

## SPEC-013b — the ikhtilas/tasheel hasr for Hafs (2026-08-15)

**Tasheel**: explicit hasr nass — «لم تُسهَّل في رواية حفص إلا همزة
واحدة، هي همزة أعجمي» (معجم علوم القرآن 1:93؛ هداية القاري 2:577؛
فريدة الدهر 4:336). ءَآلذَّكَرَيْنِ and its sisters are IBDAL, not
tasheel bayna-bayna (فريدة الدهر 1:161) — matching our istifham_tasheel
knob semantics.

**Ikhtilas/rawm**: the sole site is تَأْمَنَّا 12:11, two transmitted
wajhs — idgham+ishmam / ikhtilas of the first noon's damma (which many
ada' authors call rawm here). **Taqdim khilaf recorded**: al-Marsafi
prefers IKHTILAS (هداية القاري 1:259-261) while the printed dabt marks
ISHMAM — our canonical follows the printed dabt (same pattern as
سلاسلا); the ikhtilas wajh lives as the damma_mukhtalasa variant.
Terminology: rawm-vs-ikhtilas usage wobbles between authors (الدر
النثير 4:219; cf. النشر 2:126). No third site exists in the riwaya.



## SPEC-213 — tafkheem inheritance now nass-sourced (2026-08-15, R19)

The vowel/alif inheritance rule (R213) sheds its CONVENTION tag:

- **The alif follows what precedes it**: «أما الألف المدية... فلا توصف
  بتفخيم ولا بترقيق، بل تابعة لما قبلها تفخيمًا وترقيقًا» (هداية القاري
  1:118؛ العميد 1:130؛ غاية المريد 1:158-159 with the phonetic 'illa:
  «ليس فيه عمل عضو أصلًا»). The tahqiq is Ibn al-Jazari's own — النشر
  1:215-216 — including the refutation: the claim that the alif is
  always raqiq after mofakham letters is «شيء وَهِمَ فيه، ولم يسبقه إليه
  أحد، وقد رد عليه الأئمة المحققون».
- **The ghunna follows what FOLLOWS it** — the mirror rule: «اتباعها
  لما بعدها من الحروف تفخيمًا وترقيقًا، على العكس من ألف المد» (هداية
  القاري 1:181-182), and by istiqra' the tafkheem occurs exactly at the
  ikhfa-haqiqi martaba before exactly FIVE letters — ص ض ط ظ ق — «عند
  كل القراء»: verbatim confirmation of the engine's mukhfah set
  (= ikhfa ∩ isti'la), independently seconding لطائف الإشارات
  1:366-367.


## SPEC-124 — ta' al-ta'nith at waqf, sourced (2026-08-15, local corpus)

النشر 2:131-133 (باب الوقف على مرسوم الخط): the general rule — «الاسم
المفرد المؤنث ما لم يرسم بالتاء تُبدل تاؤه وصلًا هاءً وقفًا سواء كان
منونًا أو غير منون» (R122's basis); and words WRITTEN with the open taa
are stopped on bil-TAA following the rasm — Hafs is among الباقون at
ياأبت (2:131 «ووقف الباقون بالتاء على الرسم»), هيهات، مرضات، لات،
اللات، ذات; Ibn Jubara's haa-claim at ذات الشوكة is rejected: «الصواب
الوقف عليه بالتاء للجميع اتباعًا للرسم» (2:133); the مناة-bil-haa report
is «غلط». Engine: fully rasm-carried (the pinned text writes ة or ت per
site); v1 ayah-end scope contains no open-taa waqf site (all mudaf,
mid-ayah) → P2-full inherits the behavior automatically. Cross-ref: the
open-taa waqf keeps rawm/ishmam (the taa bears the i'rab) per النشر
2:126 — already in the isharah gate's written-taa note.
