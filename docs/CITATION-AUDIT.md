# Citation audit

Every classical reference in the rulings register (`src/quran_g2p/rules/registry.py`) checked against the Shamela library: the cited book must exist in the corpus, the cited volume:page (or bayt number) must exist in the Shamela print, and the ruling's topic keywords must appear at the cited location (±3 pages of edition drift tolerated). Quoted matn snippets are additionally verified verbatim, character-stream, inside the matns themselves. Regenerate with `python tools/audit_citations.py`.

**130 references checked: 124 verified, 6 descriptive notes, 0 failures.**

| ruling | reference | status |
|---|---|---|
| `R011_MUQATTAAT` | تحفة الأطفال [تحفة الأطفال] | OK-BOOK |
| `R011_MUQATTAAT` | النشر [النشر 1:346] | OK |
| `R012_SEEN_SAD` | الشاطبية [الشاطبية بيتا 514-515] | OK |
| `R012_SEEN_SAD` | سراج القارئ [سراج القارئ 1:163] | OK |
| `R012B_DAAF_DAMM` | الشاطبية [الشاطبية بيتا 722-723] | OK |
| `R012B_DAAF_DAMM` | التيسير [التيسير 174-176] | OK-BOOK |
| `R013_ELIDED_WAW_LIYASUU` | الحجة للقراء السبعة [الحجة للقراء السبعة 5:85] | OK |
| `R013_ELIDED_WAW_LIYASUU` | المحكم في نقط المصاحف [المحكم في نقط المصاحف 1:168] | OK |
| `R013_ELIDED_WAW_LIYASUU` | دليل الحيران [دليل الحيران 1:405-406] | OK |
| `R014B_ISTIFHAM_TASHEEL` | الشاطبية [الشاطبية أبيات 192-194] | OK |
| `R014B_ISTIFHAM_TASHEEL` | النشر [النشر 1:377-378] | OK |
| `R110_WASL_START` | المقدمة الجزرية [المقدمة الجزرية 101-103] | OK-BOOK |
| `R110_BADAL_IBTIDA` | الجزرية [الجزرية] | OK-BOOK |
| `R110_BADAL_IBTIDA` | هداية القاري [هداية القاري 2:482] | OK |
| `R110_BADAL_IBTIDA` | النشر [النشر 1:343 «حرف المد إذا وقع بعد ] | OK |
| `R112_STRIP_INITIAL_SHADDA` | (ضبط المصحف | NOTE |
| `R112_STRIP_INITIAL_SHADDA` | علامة إدغام المتماثلين والمتقاربين بين ا | NOTE |
| `R112_STRIP_INITIAL_SHADDA` | المحكم في نقط المصاحف [المحكم في نقط المصاحف للداني)] | OK-BOOK |
| `R120_ISKAN` | النشر [النشر 2:120 (الوقف بالسكون هو الأص] | OK |
| `R121_MADD_EWAD` | تحفة الأطفال [تحفة الأطفال] | OK-BOOK |
| `R121_MADD_EWAD` | هداية القاري [هداية القاري] | OK-BOOK |
| `R121_EWAD_SEAT_SILENT` | النشر [النشر 2:120] | OK |
| `R121_EWAD_SEAT_SILENT` | تحفة الأطفال [تحفة الأطفال] | OK-BOOK |
| `R122_TAA_MARBUTA_WAQF` | النشر [النشر 2:129] | OK |
| `R122_TAA_MARBUTA_WAQF` | هداية القاري [هداية القاري] | OK-BOOK |
| `R123_RAWM` | الشاطبية [الشاطبية أبيات 368-373] | OK |
| `R123_RAWM` | النشر [النشر 2:121] | OK |
| `R123_RAWM` | التيسير [التيسير 58-59] | OK-BOOK |
| `R123_ISHMAM` | الشاطبية [الشاطبية أبيات 368-373] | OK |
| `R123_ISHMAM` | النشر [النشر 2:121] | OK |
| `R123_ISHMAM` | التيسير [التيسير 58-59] | OK-BOOK |
| `R130_WASL_ELISION` | (التقاء الساكنين) | NOTE |
| `R130_WASL_ELISION` | هداية القاري [هداية القاري] | OK-BOOK |
| `R131_MADD_SHORTENING` | هداية القاري [هداية القاري 2:599 «يحذف حرف المد ] | OK |
| `R131_NOON_WIQAYA` | (التقاء الساكنين) | NOTE |
| `R131_NOON_WIQAYA` | هداية القاري [هداية القاري] | OK-BOOK |
| `R132_SAKT` | الشاطبية [الشاطبية بيتا 830-831] | OK |
| `R132_SAKT` | النشر [النشر 1:240-241] | OK |
| `R132_SAKT` | سراج القارئ [سراج القارئ 1:277] | OK |
| `R132_MALIYAH_SAKT` | النشر [النشر 2:21-22] | OK |
| `R132_MALIYAH_SAKT` | هداية القاري [هداية القاري 1:236-237] | OK |
| `R132_MALIYAH_SAKT` | فتح الوصيد [فتح الوصيد 1:434] | OK |
| `R132_MALIYAH_SAKT` | غيث النفع [غيث النفع 1:601] | OK |
| `R133_R160_IDGHAM_KAMIL` | تحفة الأطفال [تحفة الأطفال «للام أل حالان قبل ال] | OK-BOOK |
| `R133_R160_IDGHAM_KAMIL` | النشر [النشر 2:18-19] | OK |
| `R134_LAM_JALALA_ALIF` | الجزرية [الجزرية «وفخم اللام من اسم الله عن] | OK-BOOK |
| `R135_MEEM_ALLAH` | السبعة [السبعة 1:199] | OK |
| `R135_MEEM_ALLAH` | غيث النفع [غيث النفع 1:129-130] | OK |
| `R135_MEEM_ALLAH` | النويري [النويري 2:231] | OK |
| `R140_IZHAR` | تحفة الأطفال [تحفة الأطفال «للحلق ست»] | OK-BOOK |
| `R140_IZHAR` | هداية القاري [هداية القاري 1:181] | OK |
| `R140_IZHAR_HALQI` | تحفة الأطفال [تحفة الأطفال «للحلق ست»] | OK-BOOK |
| `R140_IZHAR_HALQI` | هداية القاري [هداية القاري 1:181] | OK |
| `R141_IDGHAM_GHUNNA` | تحفة الأطفال [تحفة الأطفال «في يرملون»] | OK-BOOK |
| `R141_IDGHAM_GHUNNA` | النشر [النشر 2:22] | OK |
| `R141_IDGHAM_GHUNNA_NAQIS` | تحفة الأطفال [تحفة الأطفال] | OK-BOOK |
| `R141_IDGHAM_GHUNNA_NAQIS` | النشر [النشر 2:23 (الإدغام الناقص في الوا] | OK |
| `R141_IZHAR_MUTLAQ` | تحفة الأطفال [تحفة الأطفال «إلا إذا كانا بكلمة»] | OK-BOOK |
| `R141_IZHAR_MUTLAQ` | النشر [النشر 2:23] | OK |
| `R142_IDGHAM_BILA_GHUNNA` | تحفة الأطفال [تحفة الأطفال «في اللام والرا ثم كر] | OK-BOOK |
| `R142_IDGHAM_BILA_GHUNNA` | النشر [النشر 2:24] | OK |
| `R143_IQLAB` | تحفة الأطفال [تحفة الأطفال «والثالث الإقلاب»] | OK-BOOK |
| `R143_IQLAB` | هداية القاري [هداية القاري 1:186] | OK |
| `R144_IKHFA` | تحفة الأطفال [تحفة الأطفال «صف ذا ثنا...»] | OK-BOOK |
| `R144_IKHFA` | هداية القاري [هداية القاري 1:187] | OK |
| `R150_IKHFA_SHAFAWI` | تحفة الأطفال [تحفة الأطفال «فالأول الإخفاء عند ا] | OK-BOOK |
| `R150_IKHFA_SHAFAWI` | هداية القاري [هداية القاري 1:191] | OK |
| `R160_MUTAMATHILAYN` | الجزرية [الجزرية «وأولي مثل وجنس إن سكن» أد] | OK-BOOK |
| `R160_MUTAMATHILAYN` | النشر [النشر 2:18] | OK |
| `R161_NAQIS_TA_NO_QALQALAH` | الجزرية [الجزرية «وبين الإطباق من أحطت مع ب] | OK-BOOK |
| `R161_NAQIS_TA_NO_QALQALAH` | النشر [النشر 2:19] | OK |
| `R170_GHUNNA_MUSHADDADAH` | تحفة الأطفال [تحفة الأطفال «وغن ميمًا ثم نونًا ش] | OK-BOOK |
| `R170_GHUNNA_MUSHADDADAH` | لطائف الإشارات [لطائف الإشارات 1:350] | OK |
| `R180_TABEEI` | تحفة الأطفال [تحفة الأطفال «والمد أصلي وفرعي له»] | OK-BOOK |
| `R180_PAUSAL_GLIDE` | الشاطبية [الشاطبية باب المد] | OK-BOOK |
| `R180_PAUSAL_GLIDE` | النشر [النشر 1:333] | OK |
| `R181_BADAL` | الشاطبية [الشاطبية باب المد] | OK-BOOK |
| `R181_BADAL` | النشر [النشر 1:339] | OK |
| `R183_SILAH_WAQF_DROP` | الشاطبية [الشاطبية أبيات 158-159] | OK |
| `R183_SILAH_WAQF_DROP` | سراج القارئ [سراج القارئ 1:45] | OK |
| `R184_SILAH_KUBRA` | الشاطبية [الشاطبية بيت 158] | OK |
| `R184_SILAH_KUBRA` | النشر [النشر 1:306] | OK |
| `R185_MUTTASIL` | الشاطبية [الشاطبية باب المد] | OK-BOOK |
| `R185_MUTTASIL` | النشر [النشر 1:315] | OK |
| `R185_MUTTASIL_WAQF` | الشاطبية [الشاطبية باب المد] | OK-BOOK |
| `R185_MUTTASIL_WAQF` | النشر [النشر 1:315-346] | OK |
| `R185_MUTTASIL_WAQF` | هداية القاري [هداية القاري] | OK-BOOK |
| `R186_MUNFASIL` | الشاطبية [الشاطبية] | OK-BOOK |
| `R186_MUNFASIL` | النشر [النشر 1:322] | OK |
| `R187_LAZIM_MUTHAQQAL` | تحفة الأطفال [تحفة الأطفال «ولازم إن السكون أصلا] | OK-BOOK |
| `R187_LAZIM_MUTHAQQAL` | النشر [النشر 1:342] | OK |
| `R187_R188_LAZIM` | تحفة الأطفال [تحفة الأطفال «واللازم الحرفي أول ا] | OK-BOOK |
| `R187_R188_LAZIM` | النشر [النشر 1:346] | OK |
| `R188_AIN_LEEN_LAZIM` | الشاطبية [الشاطبية بيت 177] | OK |
| `R188_AIN_LEEN_LAZIM` | هداية القاري [هداية القاري 1:343] | OK |
| `R188_AIN_LEEN_LAZIM` | حجة القراءات [حجة القراءات 1:521-522] | OK |
| `R189_AARED` | تحفة الأطفال [تحفة الأطفال «ومثل ذا إن عرض السكو] | OK-BOOK |
| `R190_LEEN` | الشاطبية [الشاطبية باب المد] | OK-BOOK |
| `R190_LEEN` | النشر [النشر 1:333] | OK |
| `R190B_SALASILA_ITHBAT` | طيبة النشر [طيبة النشر (سلاسلا نوّن)] | OK-BOOK |
| `R190B_SALASILA_ITHBAT` | النويري [النويري 2:603] | OK |
| `R190B_SALASILA_ITHBAT` | العميد [العميد 1:160-161] | OK |
| `R190C_AATAANI_HADHF` | الشاطبية [الشاطبية بيت 429] | OK |
| `R190C_AATAANI_HADHF` | هداية القاري [هداية القاري 2:544-545] | OK |
| `R190C_AATAANI_HADHF` | إبراز المعاني [إبراز المعاني 1:309] | OK |
| `R200_QALQALAH_SUGHRA` | الشاطبية [الشاطبية بيت 1158 «وفي قطب جد خمس ] | OK |
| `R200_QALQALAH_SUGHRA` | النشر [النشر 1:203] | OK |
| `R201_QALQALAH_KUBRA` | الجزرية [الجزرية «وبينن مقلقلًا إن سكنا وإن] | OK-BOOK |
| `R201_QALQALAH_KUBRA` | هداية القاري [هداية القاري 1:84-87] | OK |
| `R202_QALQALAH_AKBAR` | الجزرية [الجزرية «وبينن مقلقلًا إن سكنا وإن] | OK-BOOK |
| `R202_QALQALAH_AKBAR` | هداية القاري [هداية القاري 1:84-87] | OK |
| `R210_ISTILA` | المقدمة الجزرية [المقدمة الجزرية (باب صفات الحروف)] | OK-BOOK |
| `R210_ISTILA` | النويري [النويري 1:237-238] | OK |
| `R211_REH` | الجزرية [الجزرية باب الراءات] | OK-BOOK |
| `R211_REH` | هداية القاري [هداية القاري 1:130] | OK |
| `R211_WAQF_KHILAF` | النشر [النشر 2:105، 2:110] | OK |
| `R211_WAQF_KHILAF` | النويري [النويري 2:33] | OK |
| `R211_WAQF_KHILAF` | هداية القاري [هداية القاري 1:130-133] | OK |
| `R212_LAM_JALALA` | الجزرية [الجزرية «وفخم اللام من اسم الله عن] | OK-BOOK |
| `R214_IKHFA_TAFKHEEM` | هداية القاري [هداية القاري 1:181-182] | OK |
| `R220_ISHMAM` | الشاطبية [الشاطبية] | OK-BOOK |
| `R220_ISHMAM` | هداية القاري [هداية القاري 1:259-261] | OK |
| `R220_ISHMAM` | النشر [النشر 2:126] | OK |
| `R220B_TAAMANNA_IKHTILAS` | الشاطبية [الشاطبية] | OK-BOOK |
| `R220B_TAAMANNA_IKHTILAS` | هداية القاري [هداية القاري 1:259-261] | OK |
| `R220B_TAAMANNA_IKHTILAS` | النشر [النشر 2:126] | OK |
| `R221_IMALA` | الشاطبية [الشاطبية] | OK-BOOK |
| `R221_IMALA` | (الموضع الوحيد لحفص) | NOTE |
| `R222_TASHEEL` | الشاطبية [الشاطبية] | OK-BOOK |
| `R222_TASHEEL` | (الموضع الوحيد لحفص) | NOTE |
