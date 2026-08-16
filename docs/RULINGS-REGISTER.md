# The rulings register

Generated from `src/quran_g2p/rules/registry.py` by
`tools/export_register.py`; a test keeps this file in sync, and a
second test keeps the register itself equal to the set of rules the
engine can actually cite. Every ruling is stated for the expert
reviewer by the golden rows listed in its **review** column
(`tests/goldens/`), each of which carries the fuller citation.

62 rules. Ids are stable and append-only.

## P1 - Orthographic decode

| id | الحكم | sources | review |
|---|---|---|---|
| `R011_MUQATTAAT` | الحروف المقطعة وهجاؤها / muqatta'at spell-out (incl. yaseen/noon izhar, ha/ta qasr) | تحفة الأطفال؛ النشر 1:346 | `muq-taha`, `muq-yaseen-seen`, `muq-hameem`, `madd-harfi-ha-two`, `izhar-yaseen`, `izhar-noon-qalam` |
| `R012_SEEN_SAD` | ما يقرأ بالسين أو الصاد (يبصط، بصطة، المصيطرون، بمصيطر) / seen/sad khilaf words | الشاطبية بيتا 514-515؛ سراج القارئ 1:163 | `oneoff-yabsut-seen`, `oneoff-bastatan-seen`, `oneoff-musaytirun-sad`, `oneoff-bimusaytir-sad` |
| `R012B_DAAF_DAMM` | ضَعْف: الفتح المقدم والضم وجه ثان / daaf fath (preferred) / damm wajh, 30:54 | الشاطبية بيتا 722-723؛ التيسير 174-176 | `oneoff-daaf-fath` |
| `R013_ELIDED_WAW_LIYASUU` | لِيَسُوءُوا: إثبات الواو المحذوفة رسمًا والمد المتصل عليها / restored elided waw, 17:7 | الحجة للقراء السبعة 5:85؛ المحكم في نقط المصاحف 1:168؛ دليل الحيران 1:405-406 | `sup-17-7-waw-restored` |
| `R014B_ISTIFHAM_TASHEEL` | تسهيل همزة الوصل بعد همزة الاستفهام (الوجه الثاني) / istifham tasheel wajh (ibdal preferred) | الشاطبية أبيات 192-194؛ النشر 1:377-378 | `sup2-istifham-tasheel` |

## P3 - Ibtida'

| id | الحكم | sources | review |
|---|---|---|---|
| `R110_WASL_START` | أحكام الابتداء بهمزة الوصل (الفتح والكسر والضم) / hamzat al-wasl vowel at ibtida' | المقدمة الجزرية 101-103 | `wasl-article-fath`, `wasl-noun-ibn`, `wasl-noun-imraat`, `wasl-noun-ithnayn`, `wasl-verb-unzur-damm`, `wasl-verb-idhab-kasr`, `wasl-verb-udu-damm`, `wasl-verb-iqra-kasr` |
| `R110_BADAL_IBTIDA` | إبدال الهمزة الساكنة حرف مد عند الابتداء (ٱئْتِ: إِيتِ) / sakin hamza becomes a madd letter at ibtida' | الجزرية؛ هداية القاري 2:482؛ النشر 1:343 «حرف المد إذا وقع بعد همزة الوصل حالة الابتداء نحو ايت بقرآن» | `sup2-wasl-badal-hamza` |
| `R112_STRIP_INITIAL_SHADDA` | تخفيف الشدة المرسومة أول الآية عند الابتداء (لَّيْسَ: لَيْسَ) / ayah-initial junction shadda degeminates at ibtida' | (ضبط المصحف؛ علامة إدغام المتماثلين والمتقاربين بين الآيتين؛ المحكم في نقط المصاحف للداني) | `sup2-ibtida-shadda` |

## P4 - Pausal (waqf)

| id | الحكم | sources | review |
|---|---|---|---|
| `R120_ISKAN` | الإسكان للوقف / iskan al-waqf | النشر 2:120 (الوقف بالسكون هو الأصل) | `pausal-iskan-alamin` |
| `R121_MADD_EWAD` | مد العوض عن تنوين النصب وقفًا / madd al-'iwad at waqf | تحفة الأطفال؛ هداية القاري | `madd-iwad`, `pausal-iwad-fath-alif` |
| `R121_EWAD_SEAT_SILENT` | ألف تنوين النصب المرسومة لا تُنطق وصلًا / the tanween-fath seat alif is silent in wasl | النشر 2:120؛ تحفة الأطفال | `pausal-iwad-fath-alif`, `pausal-iwad-khusr` *(the wasl-silence is the stated complement of the waqf ibdal ruling on these rows)* |
| `R122_TAA_MARBUTA_WAQF` | الوقف على التاء المربوطة هاءً / taa marbuta read as haa at waqf | النشر 2:129؛ هداية القاري | `pausal-marbuta-qaria`, `pausal-marbuta-mid-wasl-teh` |
| `R123_RAWM` | الروم / rawm (partial haraka at waqf) | الشاطبية أبيات 368-373؛ النشر 2:121؛ التيسير 58-59 | `sup-rawm-general`, `sup-rawm-exclusions`, `sup-rawm-haa-damir` |
| `R123_ISHMAM` | الإشمام / ishmam (lip-rounding at waqf, damm only) | الشاطبية أبيات 368-373؛ النشر 2:121؛ التيسير 58-59 | `sup-rawm-general` |

## P5 - Junction (wasl)

| id | الحكم | sources | review |
|---|---|---|---|
| `R130_WASL_ELISION` | سقوط همزة الوصل درجًا / hamzat al-wasl elided inside connected speech | (التقاء الساكنين)؛ هداية القاري | `wiqaya-khayran`, `junction-madd-shortening`, `sup-naql-49-11`, `lam-shamsi-shams` *(the elision principle is exercised and stated across the junction and lam-altta'reef rows)* |
| `R131_MADD_SHORTENING` | قصر حرف المد لالتقاء الساكنين / madd letter shortened before hamzat-al-wasl sakin | هداية القاري 2:599 «يحذف حرف المد لالتقاء الساكنين» | `junction-madd-shortening` |
| `R131_NOON_WIQAYA` | نون الوقاية بين التنوين وهمزة الوصل / noon al-wiqaya resolving tanween + wasl | (التقاء الساكنين)؛ هداية القاري | `wiqaya-khayran` |
| `R132_SAKT` | سكتات حفص اللازمة من طريق الشاطبية / the four obligatory sakts | الشاطبية بيتا 830-831؛ النشر 1:240-241؛ سراج القارئ 1:277 | `sup-sakt-class`, `sup-sakt-75-27` |
| `R132_MALIYAH_SAKT` | وجها وصل مَالِيَهْ هَلَكَ (السكت المقدم والإدغام) / maliyah-halak wasl wajhan | النشر 2:21-22؛ هداية القاري 1:236-237؛ فتح الوصيد 1:434؛ غيث النفع 1:601 | `sup2-maliyah-wasl` |
| `R133_R160_IDGHAM_KAMIL` | الإدغام الكامل (اللام الشمسية والمثلان المتصلان) / complete idgham: lam shamsiyya and adjacent mithlayn | تحفة الأطفال «للام أل حالان قبل الأحرف»؛ النشر 2:18-19 | `lam-shamsi-shams`, `lam-shamsi-nnas`, `mutamathil-yudrikkum` |
| `R134_LAM_JALALA_ALIF` | ألف لفظ الجلالة المحذوفة رسمًا / the dagger alif of the jalala | الجزرية «وفخم اللام من اسم الله عن فتح أو ضم» | `jalala-tarqeeq-after-kasr`, `jalala-tafkheem-after-fath` |
| `R135_MEEM_ALLAH` | وصل الٓمٓ بلفظ الجلالة (فتح الميم وبقاء اللازم) / alif-lam-meem joined to the jalala, 3:1-2 | السبعة 1:199؛ غيث النفع 1:129-130؛ النويري 2:231 | `sup-alm-allah` |
| `R136_BASMALA_JOINS` | البسملة بين السورتين وأوجه وصلها والوجه الممنوع / basmala between surahs: the three legal joins, the forbidden fourth | الشاطبية أبيات 100-107 «وبسمل بين السورتين بسنة»؛ غيث النفع 1:270؛ البدور الزاهرة 1:133 | `sup2-basmala-joins` *(enforced structurally: phonemize_concat refuses a group that ends on the basmala after joining it to a preceding item)* |

## P6 - Noon sakinah and tanween

| id | الحكم | sources | review |
|---|---|---|---|
| `R140_IZHAR` | الإظهار الحلقي للنون الساكنة / izhar halqi (noon sakinah) | تحفة الأطفال «للحلق ست»؛ هداية القاري 1:181 | `izhar-hamza`, `izhar-heh`, `izhar-ain`, `izhar-hah`, `izhar-ghain`, `izhar-khah` |
| `R140_IZHAR_HALQI` | الإظهار الحلقي للتنوين / izhar halqi (tanween carrier) | تحفة الأطفال «للحلق ست»؛ هداية القاري 1:181 | `izhar-hamza`, `izhar-tanween-hah`, `izhar-tanween-ain` |
| `R141_IDGHAM_GHUNNA` | الإدغام بغنة الكامل (ن، م) / complete idgham with ghunna | تحفة الأطفال «في يرملون»؛ النشر 2:22 | `idgham-noon-kamil`, `idgham-meem-kamil`, `idgham-tanween-meem`, `tawkeed-layakoonan-idgham` |
| `R141_IDGHAM_GHUNNA_NAQIS` | الإدغام بغنة الناقص (و، ي) / incomplete idgham with ghunna | تحفة الأطفال؛ النشر 2:23 (الإدغام الناقص في الواو والياء) | `idgham-yeh-naqis`, `idgham-waw-naqis`, `idgham-tanween-waw` |
| `R141_IZHAR_MUTLAQ` | الإظهار المطلق (الدنيا، بنيان، قنوان، صنوان) / izhar mutlaq inside one word | تحفة الأطفال «إلا إذا كانا بكلمة»؛ النشر 2:23 | `izhar-mutlaq-dunya`, `izhar-mutlaq-bunyan`, `izhar-mutlaq-qinwan`, `izhar-mutlaq-sinwan` |
| `R142_IDGHAM_BILA_GHUNNA` | الإدغام بلا غنة (ل، ر) / idgham without ghunna | تحفة الأطفال «في اللام والرا ثم كررنه»؛ النشر 2:24 | `idgham-lam`, `idgham-reh` |
| `R143_IQLAB` | الإقلاب / iqlab (noon/tanween to hidden meem before baa) | تحفة الأطفال «والثالث الإقلاب»؛ هداية القاري 1:186 | `iqlab-min-badi`, `iqlab-anbihum`, `iqlab-baqliha`, `iqlab-burika`, `iqlab-alim-bithat`, `tawkeed-lanasfaan-iqlab` |
| `R144_IKHFA` | الإخفاء الحقيقي (الحروف الخمسة عشر) / ikhfa haqiqi, all fifteen letters | تحفة الأطفال «صف ذا ثنا...»؛ هداية القاري 1:187 | `ikhfa-teh`, `ikhfa-theh`, `ikhfa-jeem`, `ikhfa-dal`, `ikhfa-thal`, `ikhfa-zain`, `ikhfa-seen`, `ikhfa-sheen`, `ikhfa-sad-mofakham`, `ikhfa-dad`, `ikhfa-tah-mofakham`, `ikhfa-zah`, `ikhfa-feh`, `ikhfa-qaf-mofakham`, `ikhfa-kaf` |

## P7 - Meem sakinah

| id | الحكم | sources | review |
|---|---|---|---|
| `R150_IKHFA_SHAFAWI` | الإخفاء الشفوي / ikhfa shafawi | تحفة الأطفال «فالأول الإخفاء عند الباء»؛ هداية القاري 1:191 | `meem-ikhfa-tarmihim`, `meem-ikhfa-yatasim` |

## P8 - General idgham

| id | الحكم | sources | review |
|---|---|---|---|
| `R160_MUTAMATHILAYN` | إدغام المتماثلين الصغير / idgham mutamathilayn saghir | الجزرية «وأولي مثل وجنس إن سكن» أدغم؛ النشر 2:18 | `mutamathil-yudrikkum`, `meem-idgham-lahum-ma` |
| `R161_NAQIS_TA_NO_QALQALAH` | الإدغام الناقص للطاء في التاء (بقاء الإطباق ولا قلقلة) / naqis taa idgham: itbaq retained, no qalqalah | الجزرية «وبين الإطباق من أحطت مع بسطت»؛ النشر 2:19 | `naqis-tah-basatta`, `naqis-tah-ahatt`, `naqis-tah-farrattum` |

## P9 - Ghunna

| id | الحكم | sources | review |
|---|---|---|---|
| `R170_GHUNNA_MUSHADDADAH` | غنة النون والميم المشددتين / ghunna of mushaddad noon and meem | تحفة الأطفال «وغن ميمًا ثم نونًا شددا»؛ لطائف الإشارات 1:350 | `ghunna-noon-mushaddad`, `ghunna-meem-amma`, `ghunna-inna`, `ghunna-thumma` |

## P10 - Madd

| id | الحكم | sources | review |
|---|---|---|---|
| `R180_TABEEI` | المد الطبيعي / madd tabee'i (2) | تحفة الأطفال «والمد أصلي وفرعي له» | `madd-tabeei-qala` |
| `R180_PAUSAL_GLIDE` | الحرف اللين الناشئ بإسكان الوقف / waqf iskan exposing the leen glide | الشاطبية باب المد؛ النشر 1:333 | `madd-leen-quraysh`, `madd-leen-khawf` |
| `R181_BADAL` | مد البدل / madd al-badal (2) | الشاطبية باب المد؛ النشر 1:339 | `madd-badal` |
| `R183_SILAH_WAQF_DROP` | سقوط صلة هاء الضمير وقفًا / silah dropped at waqf | الشاطبية أبيات 158-159؛ سراج القارئ 1:45 | `madd-silah-sughra`, `pausal-iskan-alamin` *(stated jointly by the silah row and the waqf-iskan row)* |
| `R184_SILAH_KUBRA` | الصلة الكبرى قبل الهمز / silah kubra before hamza | الشاطبية بيت 158؛ النشر 1:306 | `madd-silah-kubra` |
| `R185_MUTTASIL` | المد الواجب المتصل / madd muttasil (4-5) | الشاطبية باب المد؛ النشر 1:315 | `madd-muttasil-jaa`, `madd-muttasil-samaa` |
| `R185_MUTTASIL_WAQF` | المتصل الموقوف عليه (جواز الست) / muttasil at waqf admits 6 | الشاطبية باب المد؛ النشر 1:315-346؛ هداية القاري | `sup-madd-amounts` |
| `R186_MUNFASIL` | المد الجائز المنفصل / madd munfasil (4-5) | الشاطبية؛ النشر 1:322 | `madd-munfasil-bima-unzila` |
| `R187_LAZIM_MUTHAQQAL` | المد اللازم الكلمي / madd lazim kalimi (6) | تحفة الأطفال «ولازم إن السكون أصلا»؛ النشر 1:342 | `madd-lazim-daalleen`, `madd-lazim-haaqqah`, `madd-lazim-taammah`, `madd-lazim-mukhaffaf-aalaan` |
| `R187_R188_LAZIM` | المد اللازم الحرفي / madd lazim harfi (6) | تحفة الأطفال «واللازم الحرفي أول السور»؛ النشر 1:346 | `madd-harfi-laam`, `madd-harfi-meem`, `madd-harfi-kaf-19-1`, `madd-harfi-sad-19-1` |
| `R188_AIN_LEEN_LAZIM` | عَيْن: اللين اللازم الحرفي (الوجهان والإشباع مقدم) / 'ayn: lazim leen, {4,6} with 6 preferred | الشاطبية بيت 177؛ هداية القاري 1:343؛ حجة القراءات 1:521-522 | `madd-ain-19-1` |
| `R189_AARED` | المد العارض للسكون / madd 'aared lil-sukun (2/4/6) | تحفة الأطفال «ومثل ذا إن عرض السكون» | `madd-aared-nastaeen` |
| `R190_LEEN` | مد اللين / madd al-leen (2/4/6 at waqf) | الشاطبية باب المد؛ النشر 1:333 | `madd-leen-quraysh`, `madd-leen-khawf` |
| `R190B_SALASILA_ITHBAT` | سَلَاسِلَا: إثبات الألف وقفًا ووجهه / salasila waqf alif ithbat | طيبة النشر (سلاسلا نوّن)؛ النويري 2:603؛ العميد 1:160-161 | `alif7-salasila-wasl` |
| `R190C_AATAANI_HADHF` | آتَانِ: وجها الوقف (إثبات الياء المقدم وحذفها) / aataani waqf wajhan | الشاطبية بيت 429؛ هداية القاري 2:544-545؛ إبراز المعاني 1:309 | `sup-aataani-wajh` |

## P11 - Qalqalah

| id | الحكم | sources | review |
|---|---|---|---|
| `R200_QALQALAH_SUGHRA` | القلقلة الصغرى / qalqalah sughra | الشاطبية بيت 1158 «وفي قطب جد خمس قلقلة»؛ النشر 1:203 | `qlq-sughra-qaf`, `qlq-sughra-tah`, `qlq-sughra-beh`, `qlq-sughra-jeem`, `qlq-sughra-dal` |
| `R201_QALQALAH_KUBRA` | القلقلة الكبرى / qalqalah kubra (waqf) | الجزرية «وبينن مقلقلًا إن سكنا وإن يكن في الوقف كان أبينا»؛ هداية القاري 1:84-87 | `qlq-kubra-falaq`, `qlq-kubra-ahad`, `qlq-kubra-muheet`, `qlq-kubra-bahij` |
| `R202_QALQALAH_AKBAR` | القلقلة الأكبر (الموقوف عليه مشددًا) / qalqalah akbar (waqf on mushaddad) | الجزرية «وبينن مقلقلًا إن سكنا وإن يكن في الوقف كان أبينا»؛ هداية القاري 1:84-87 | `qlq-kubra-tabb`, `sup2-qalqalah-akbar` |

## P12 - Tafkheem

| id | الحكم | sources | review |
|---|---|---|---|
| `R210_ISTILA` | تفخيم حروف الاستعلاء ومراتبه / isti'la tafkheem and its maraatib | المقدمة الجزرية (باب صفات الحروف)؛ النويري 1:237-238 | `sup-sifat-sets`, `sup2-tafkheem-maratib` *(the letter set is stated by the sifat row, the grading by the maraatib row)* |
| `R211_REH` | أحكام الراء تفخيمًا وترقيقًا / the raa decision table | الجزرية باب الراءات؛ هداية القاري 1:130 | `ra-fath-tafkheem`, `ra-damm-tafkheem`, `ra-kasr-tarqeeq`, `ra-sakin-after-fath`, `ra-sakin-after-damm`, `ra-sakin-after-kasr-tarqeeq`, `ra-sakin-kasr-istila-mirsad`, `ra-firq-wasl-tarqeeq`, `ra-nudhur-waqf-tarqeeq`, `ra-yasr-waqf-tarqeeq`, `ra-fajr-waqf-tafkheem`, `ra-khabir-waqf-tarqeeq` |
| `R211_WAQF_KHILAF` | فرش راءات الوقف الخلافية (مصر، القطر، أسر) / the waqf raa khilaf words | النشر 2:105، 2:110؛ النويري 2:33؛ هداية القاري 1:130-133 | `sup-misr-qitr-asr` |
| `R212_LAM_JALALA` | تفخيم لام الجلالة وترقيقها / lam al-jalala tafkheem/tarqeeq | الجزرية «وفخم اللام من اسم الله عن فتح أو ضم» | `jalala-tarqeeq-after-kasr`, `jalala-tafkheem-after-fath` |
| `R214_IKHFA_TAFKHEEM` | تبعية غنة الإخفاء لما بعدها تفخيمًا وترقيقًا / ikhfa ghunna follows the trigger's tafkheem | هداية القاري 1:181-182 | `sup-ghunna-tabiyya`, `ikhfa-sad-mofakham`, `ikhfa-tah-mofakham`, `ikhfa-qaf-mofakham` |

## P13 - One-offs

| id | الحكم | sources | review |
|---|---|---|---|
| `R220_ISHMAM` | إشمام تَأْمَنَّا / ishmam of ta'manna, 12:11 | الشاطبية؛ هداية القاري 1:259-261؛ النشر 2:126 | `sup-taamanna-ishmam` |
| `R220B_TAAMANNA_IKHTILAS` | اختلاس تَأْمَنَّا (الوجه الثاني) / ikhtilas wajh of ta'manna | الشاطبية؛ هداية القاري 1:259-261؛ النشر 2:126 | `sup-taamanna-ishmam` |
| `R221_IMALA` | إمالة مَجْر۪ىٰهَا / imala, 11:41 | الشاطبية؛ (الموضع الوحيد لحفص) | `oneoff-imala` |
| `R222_TASHEEL` | تسهيل ءَا۬عْجَمِيٌّ / tasheel, 41:44 | الشاطبية؛ (الموضع الوحيد لحفص) | `oneoff-tasheel` |
