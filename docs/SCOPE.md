# Scope: the external completeness sweep

The register gate proves the engine, the rulings register, and the
review sheet agree with each other. This document records the *external*
check: the full chapter inventory of the tradition's own manuals (the
twenty abwab of هداية القاري, the babs of المقدمة الجزرية and تحفة
الأطفال, taken from the Shamela corpus tables of contents) mapped
against the register, so a ruling the engine never knew about cannot
hide. Every bab is either covered or listed here with the reason it is
out of scope.

## Covered by the register and review sheet

| bab (هداية القاري) | coverage |
|---|---|
| صفات الحروف (2) | sifat table + the sifat-sets review row |
| التفخيم والترقيق (3) | R210-R214 and the raa/jalala/maraatib rows |
| الضاد والظاء (4) | distinct bases + الاستطالة in the sifat row |
| النون الساكنة والتنوين (5) | R140-R144 |
| الغنة وأحكامها (6) | R170 + the ghunna-tab'iyya rows |
| الميم الساكنة (7) | R150-R152 rows |
| اللامات الساكنة (8) | lam al-ta'reef R133; lam al-fi'l idgham sites (قُل رَّبِّ، بَل رَّفَعَهُ) under R160/R162 rows; izhar elsewhere is the default the sites delimit |
| المثلان والمتجانسان والمتقاربان والمتباعدان (9، 10) | R160-R161 rows + the saghir/kabir taxonomy row |
| المد والقصر (11) | R180-R190C and the madd-amounts row |
| الوقف والسكت (12) | R120-R124, R132 |
| هاء التأنيث المرسومة بالتاء (14) | R122 (المربوطة) + the open-taa waqf row (رَحْمَتَ الزخرف) |
| همزتا الوصل والقطع (15) | R110-R112 rows; hamzat al-qat' is always realized |
| الوقف على أواخر الكلم (16) | iskan/rawm/ishmam rows |
| البسملة (18) | R136: the three legal joins, the forbidden fourth (enforced in `phonemize_concat`), Anfal→Tawba wajhs |
| ما يراعى لحفص في كلمات مخصوصة (19) | the farsh/one-off rows (R012x, R013, R190B/C, R220-R222 …) |

## Out of scope, with reasons

| bab | reason |
|---|---|
| مخارج الحروف وألقابها (1) | the articulation inventory *is* the phone alphabet itself; it defines the symbols, it is not a ruling over them |
| مبادئ العلم، مراتب القراءة، اللحن (intro fusul) | pedagogy and adab, no phonological output |
| الوقف والابتداء positions (تام/كاف/حسن/قبيح) (12) | choosing *where* to stop is the reciter's input (`WaqfSpec`); the engine rules on what happens *given* a stop |
| المقطوع والموصول (13) | rasm conventions governing permissible mid-phrase stops; same input-domain reason |
| الاستعاذة (17) | pre-recitation formula, not mushaf text; the ASR pipeline handles it as preamble audio, not as phonemized ayah content |
| التكبير (20) | transmitted for the ending surahs via al-Tayyibah's Makki turuq, not via al-Shatibiyyah for Hafs |
| النبر وإبراز التشديد عند الوقف على المشدد | suprasegmental articulation quality; the phone layer carries the gemination itself (`geminated=true` at waqf), the stress prominence is not a phonemic token |
| ياءات الإضافة والزوائد (Shatibiyyah farsh) | Hafs's choices are already encoded in the pinned mushaf text (harakat and rasm); the only within-Hafs waqf khilaf, آتَىٰنِ, has its own row |

Anything found missing by a future sweep belongs in the register and the
review sheet, not silently in code: the register gate enforces that
path.
