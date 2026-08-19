"""Ordered rule pipeline and the append-only RuleId registry.

«لِأَنَّ الْقِرَاءَةَ سُنَّةٌ مُتَّبَعَةٌ يَلْزَمُ قَبُولُهَا وَالْمَصِيرُ إِلَيْهَا» — ابن الجزري، النشر 1:11
"For recitation is a followed transmission: its acceptance is binding."
Nothing here was reasoned into existence: every ruling below is relayed
from the books, cited to its print, and judged by the people of the chain.

RuleIds are stable public identifiers: spec files, golden tests, provenance
chains, verdicts, and export artifacts all reference them. NEVER rename or
reuse an id; retired rules keep their id with a tombstone comment.
"""
from __future__ import annotations

from .base import Rule

#: Ordered pipeline. Populated phase by phase as rules land (P1 first).
PIPELINE: list[type] = []


def all_rule_ids() -> list[str]:
    return [rule.rule_id for rule in PIPELINE]


def register(rule_cls: type) -> type:
    """Class decorator: append a rule to the pipeline in declaration order."""
    if not isinstance(rule_cls, type):
        raise TypeError("register expects a class")
    for attr in ("rule_id", "spec", "phase"):
        if not hasattr(rule_cls, attr):
            raise TypeError(f"{rule_cls.__name__} missing {attr}")
    if rule_cls.rule_id in all_rule_ids():
        raise ValueError(f"duplicate rule_id {rule_cls.rule_id}")
    if PIPELINE and rule_cls.phase < PIPELINE[-1].phase:
        raise ValueError(
            f"{rule_cls.rule_id} phase {rule_cls.phase} declared after phase {PIPELINE[-1].phase}"
        )
    PIPELINE.append(rule_cls)
    return rule_cls


# ---------------------------------------------------------------------------
# The rulings register (review coverage, citations, Arabic names)
# ---------------------------------------------------------------------------
# One `Ruling` per rule id the engine can cite in a RuleApp trace. Ids are
# stable and append-only against tests/registry_frozen_ids.txt. Each entry
# binds the ruling's pipeline phase, Arabic name, SPEC anchor, classical
# citation (taken from its golden rows, which carry the fuller cites), and
# the golden rows that put it in front of the expert reviewer.
# tests/test_registry_complete.py enforces the whole contract: the register
# equals the set of ids used in src/ (both directions), coverage rows exist,
# every entry carries a citation, and the append-only manifest holds.

from dataclasses import dataclass


#: id number range -> pipeline phase. R00x/R01x decode orthography (P1);
#: R11x ibtida' (P3); R12x pausal (P4); R13x junction (P5); R14x noon
#: sakinah/tanween (P6); R15x meem sakinah (P7); R16x general idgham
#: (P8); R17x ghunna (P9); R18x-R19x madd (P10); R20x qalqalah (P11);
#: R21x tafkheem (P12); R22x one-offs (P13).
PHASE_BY_PREFIX: dict[str, str] = {
    "R00": "P1", "R01": "P1", "R11": "P3", "R12": "P4", "R13": "P5",
    "R14": "P6", "R15": "P7", "R16": "P8", "R17": "P9", "R18": "P10",
    "R19": "P10", "R20": "P11", "R21": "P12", "R22": "P13",
}


@dataclass(frozen=True)
class Ruling:
    id: str
    phase: str
    name_ar: str
    name_en: str
    spec: str
    cite: str
    covered_by: tuple[str, ...]
    note: str = ""


RULINGS: tuple[Ruling, ...] = (
    # ------------------------------------------------------ P1 orthography
    Ruling("R011_MUQATTAAT", "P1",
         "الحروف المقطعة وهجاؤها",
         "muqatta'at spell-out (incl. yaseen/noon izhar, ha/ta qasr)",
         "SPEC-011",
         "تحفة الأطفال؛ النشر 1:346",
         ("muq-taha", "muq-yaseen-seen", "muq-hameem", "madd-harfi-ha-two",
          "izhar-yaseen", "izhar-noon-qalam")),
    Ruling("R012_SEEN_SAD", "P1",
         "ما يقرأ بالسين أو الصاد (يبصط، بصطة، المصيطرون، بمصيطر)",
         "seen/sad khilaf words",
         "SPEC-012",
         "الشاطبية بيتا 514-515؛ سراج القارئ 1:163",
         ("oneoff-yabsut-seen", "oneoff-bastatan-seen",
          "oneoff-musaytirun-sad", "oneoff-bimusaytir-sad")),
    Ruling("R012B_DAAF_DAMM", "P1",
         "ضَعْف: الفتح المقدم والضم وجه ثان",
         "daaf fath (preferred) / damm wajh, 30:54",
         "SPEC-012",
         "الشاطبية بيتا 722-723؛ التيسير 174-176",
         ("oneoff-daaf-fath",)),
    Ruling("R013_ELIDED_WAW_LIYASUU", "P1",
         "لِيَسُوءُوا: إثبات الواو المحذوفة رسمًا والمد المتصل عليها",
         "restored elided waw, 17:7",
         "SPEC-012",
         "الحجة للقراء السبعة 5:85؛ المحكم في نقط المصاحف 1:168؛ دليل الحيران 1:405-406",
         ("sup-17-7-waw-restored",)),
    Ruling("R014B_ISTIFHAM_TASHEEL", "P1",
         "تسهيل همزة الوصل بعد همزة الاستفهام (الوجه الثاني)",
         "istifham tasheel wajh (ibdal preferred)",
         "SPEC-012",
         "الشاطبية أبيات 192-194؛ النشر 1:377 «وقال آخرون: تسهل بين بين»",
         ("sup2-istifham-tasheel",)),
    # --------------------------------------------------------- P3 ibtida'
    Ruling("R110_WASL_START", "P3",
         "أحكام الابتداء بهمزة الوصل (الفتح والكسر والضم)",
         "hamzat al-wasl vowel at ibtida'",
         "SPEC-110",
         "المقدمة الجزرية 101-103",
         ("wasl-article-fath", "wasl-noun-ibn", "wasl-noun-imraat",
          "wasl-noun-ithnayn", "wasl-verb-unzur-damm",
          "wasl-verb-idhab-kasr", "wasl-verb-udu-damm",
          "wasl-verb-iqra-kasr")),
    Ruling("R110_BADAL_IBTIDA", "P3",
         "إبدال الهمزة الساكنة حرف مد عند الابتداء (ٱئْتِ: إِيتِ)",
         "sakin hamza becomes a madd letter at ibtida'",
         "SPEC-110",
         "الجزرية؛ هداية القاري 2:482؛ النشر 1:343 «حرف المد إذا وقع بعد همزة الوصل حالة الابتداء نحو ايت بقرآن»",
         ("sup2-wasl-badal-hamza",)),
    Ruling("R112_STRIP_INITIAL_SHADDA", "P3",
         "تخفيف الشدة المرسومة أول الآية عند الابتداء (لَّيْسَ: لَيْسَ)",
         "ayah-initial junction shadda degeminates at ibtida'",
         "SPEC-110",
         "(ضبط المصحف؛ علامة إدغام المتماثلين والمتقاربين بين الآيتين؛ المحكم في نقط المصاحف للداني)",
         ("sup2-ibtida-shadda",)),
    # ---------------------------------------------------------- P4 pausal
    Ruling("R120_ISKAN", "P4",
         "الإسكان للوقف",
         "iskan al-waqf",
         "SPEC-120",
         "النشر 2:120 «فأما السكون فهو الأصل في الوقف على الكلم المتحركة وصلا»",
         ("pausal-iskan-alamin",)),
    Ruling("R121_MADD_EWAD", "P4",
         "مد العوض عن تنوين النصب وقفًا",
         "madd al-'iwad at waqf",
         "SPEC-121",
         "تحفة الأطفال؛ هداية القاري",
         ("madd-iwad", "pausal-iwad-fath-alif")),
    Ruling("R121_EWAD_SEAT_SILENT", "P4",
         "ألف تنوين النصب المرسومة لا تُنطق وصلًا",
         "the tanween-fath seat alif is silent in wasl",
         "SPEC-121",
         "النشر 2:120؛ تحفة الأطفال",
         ("pausal-iwad-fath-alif", "pausal-iwad-khusr"),
         note="the wasl-silence is the stated complement of the waqf "
              "ibdal ruling on these rows"),
    Ruling("R122_TAA_MARBUTA_WAQF", "P4",
         "الوقف على التاء المربوطة هاءً",
         "taa marbuta read as haa at waqf",
         "SPEC-122",
         "النشر 2:129؛ هداية القاري",
         ("pausal-marbuta-qaria", "pausal-marbuta-mid-wasl-teh")),
    Ruling("R123_RAWM", "P4",
         "الروم",
         "rawm (partial haraka at waqf)",
         "SPEC-123",
         "الشاطبية أبيات 368-373؛ النشر 2:121 «وأما الروم فهو عند القراء عبارة عن النطق ببعض الحركة»؛ التيسير 58-59",
         ("sup-rawm-general", "sup-rawm-exclusions", "sup-rawm-haa-damir")),
    Ruling("R123_ISHMAM", "P4",
         "الإشمام",
         "ishmam (lip-rounding at waqf, damm only)",
         "SPEC-123",
         "الشاطبية أبيات 368-373؛ النشر 2:121 «وأما الإشمام فهو عبارة عن الإشارة إلى الحركة من غير تصويت»؛ التيسير 58-59",
         ("sup-rawm-general",)),
    # -------------------------------------------------------- P5 junction
    Ruling("R130_WASL_ELISION", "P5",
         "سقوط همزة الوصل درجًا",
         "hamzat al-wasl elided inside connected speech",
         "SPEC-130",
         "(التقاء الساكنين)؛ هداية القاري",
         ("wiqaya-khayran", "junction-madd-shortening", "sup-naql-49-11",
          "lam-shamsi-shams"),
         note="the elision principle is exercised and stated across the "
              "junction and lam-altta'reef rows"),
    Ruling("R131_MADD_SHORTENING", "P5",
         "حذف حرف المد لالتقاء الساكنين",
         "madd letter shortened before hamzat-al-wasl sakin",
         "SPEC-131",
         "هداية القاري 2:599 «يحذف حرف المد لالتقاء الساكنين»",
         ("junction-madd-shortening",)),
    Ruling("R131_NOON_WIQAYA", "P5",
         "كسر نون التنوين لالتقاء الساكنين عند همزة الوصل",
         "tanween noon takes kasra at iltiqa al-sakinayn (wasl junctions)",
         "SPEC-131",
         "النشر 2:315 «بالنصب والتنوين وكسره للساكنين»؛ هداية القاري",
         ("wiqaya-khayran",)),
    Ruling("R132_SAKT", "P5",
         "سكتات حفص اللازمة من طريق الشاطبية",
         "the four obligatory sakts",
         "SPEC-132",
         "الشاطبية بيتا 830-831؛ النشر 1:240-241؛ سراج القارئ 1:277",
         ("sup-sakt-class", "sup-sakt-75-27")),
    Ruling("R132_MALIYAH_SAKT", "P5",
         "وجها وصل مَالِيَهْ هَلَكَ (السكت المقدم والإدغام)",
         "maliyah-halak wasl wajhan",
         "SPEC-132",
         "النشر 2:21-22؛ هداية القاري 1:236-237؛ فتح الوصيد 1:434؛ غيث النفع 1:601",
         ("sup2-maliyah-wasl",)),
    Ruling("R133_R160_IDGHAM_KAMIL", "P5",
         "الإدغام الكامل (اللام الشمسية والمثلان المتصلان)",
         "complete idgham: lam shamsiyya and adjacent mithlayn",
         "SPEC-133",
         "تحفة الأطفال «للام أل حالان قبل الأحرف»؛ النشر 2:18-19",
         ("lam-shamsi-shams", "lam-shamsi-nnas", "mutamathil-yudrikkum")),
    Ruling("R134_LAM_JALALA_ALIF", "P5",
         "ألف لفظ الجلالة المحذوفة رسمًا",
         "the dagger alif of the jalala",
         "SPEC-134",
         "الجزرية «وفخم اللام من اسم الله عن فتح أو ضم»",
         ("jalala-tarqeeq-after-kasr", "jalala-tafkheem-after-fath")),
    Ruling("R135_MEEM_ALLAH", "P5",
         "وصل الٓمٓ بلفظ الجلالة (فتح الميم وبقاء اللازم)",
         "alif-lam-meem joined to the jalala, 3:1-2",
         "SPEC-011",
         "السبعة 1:199؛ غيث النفع 1:129-130؛ النويري 2:231",
         ("sup-alm-allah",)),
    Ruling("R136_BASMALA_JOINS", "P5",
         "البسملة بين السورتين وأوجه وصلها والوجه الممنوع",
         "basmala between surahs: the three legal joins, the forbidden fourth",
         "SPEC-005",
         "الشاطبية أبيات 100-107 «وبسمل بين السورتين بسنة»؛ غيث النفع 1:270؛ البدور الزاهرة 1:133",
         ("sup2-basmala-joins",),
         note="enforced structurally: phonemize_concat refuses a group that "
              "ends on the basmala after joining it to a preceding item"),
    # ---------------------------------------- P6 noon sakinah and tanween
    Ruling("R140_IZHAR", "P6",
         "الإظهار الحلقي للنون الساكنة",
         "izhar halqi (noon sakinah)",
         "SPEC-140",
         "تحفة الأطفال «للحلق ست»؛ هداية القاري 1:181",
         ("izhar-hamza", "izhar-heh", "izhar-ain", "izhar-hah",
          "izhar-ghain", "izhar-khah")),
    Ruling("R140_IZHAR_HALQI", "P6",
         "الإظهار الحلقي للتنوين",
         "izhar halqi (tanween carrier)",
         "SPEC-140",
         "تحفة الأطفال «للحلق ست»؛ هداية القاري 1:181",
         ("izhar-hamza", "izhar-tanween-hah", "izhar-tanween-ain")),
    Ruling("R141_IDGHAM_GHUNNA", "P6",
         "الإدغام بغنة الكامل (ن، م)",
         "complete idgham with ghunna",
         "SPEC-141",
         "تحفة الأطفال «في يرملون»؛ النشر 2:22",
         ("idgham-noon-kamil", "idgham-meem-kamil", "idgham-tanween-meem",
          "tawkeed-layakoonan-idgham")),
    Ruling("R141_IDGHAM_GHUNNA_NAQIS", "P6",
         "الإدغام بغنة الناقص (و، ي)",
         "incomplete idgham with ghunna",
         "SPEC-141",
         "تحفة الأطفال؛ النشر 2:23 (الإدغام الناقص في الواو والياء)",
         ("idgham-yeh-naqis", "idgham-waw-naqis", "idgham-tanween-waw")),
    Ruling("R141_IZHAR_MUTLAQ", "P6",
         "الإظهار المطلق (الدنيا، بنيان، قنوان، صنوان)",
         "izhar mutlaq inside one word",
         "SPEC-141",
         "تحفة الأطفال «إلا إذا كانا بكلمة»؛ النشر 2:23",
         ("izhar-mutlaq-dunya", "izhar-mutlaq-bunyan",
          "izhar-mutlaq-qinwan", "izhar-mutlaq-sinwan")),
    Ruling("R142_IDGHAM_BILA_GHUNNA", "P6",
         "الإدغام بلا غنة (ل، ر)",
         "idgham without ghunna",
         "SPEC-142",
         "تحفة الأطفال «في اللام والرا ثم كررنه»؛ النشر 2:24",
         ("idgham-lam", "idgham-reh")),
    Ruling("R143_IQLAB", "P6",
         "الإقلاب",
         "iqlab (noon/tanween to hidden meem before baa)",
         "SPEC-143",
         "تحفة الأطفال «والثالث الإقلاب»؛ هداية القاري 1:186",
         ("iqlab-min-badi", "iqlab-anbihum", "iqlab-baqliha",
          "iqlab-burika", "iqlab-alim-bithat", "tawkeed-lanasfaan-iqlab")),
    Ruling("R144_IKHFA", "P6",
         "الإخفاء الحقيقي (الحروف الخمسة عشر)",
         "ikhfa haqiqi, all fifteen letters",
         "SPEC-144",
         "تحفة الأطفال «صف ذا ثنا...»؛ هداية القاري 1:187",
         ("ikhfa-teh", "ikhfa-theh", "ikhfa-jeem", "ikhfa-dal",
          "ikhfa-thal", "ikhfa-zain", "ikhfa-seen", "ikhfa-sheen",
          "ikhfa-sad-mofakham", "ikhfa-dad", "ikhfa-tah-mofakham",
          "ikhfa-zah", "ikhfa-feh", "ikhfa-qaf-mofakham", "ikhfa-kaf")),
    # ---------------------------------------------------- P7 meem sakinah
    Ruling("R150_IKHFA_SHAFAWI", "P7",
         "الإخفاء الشفوي",
         "ikhfa shafawi",
         "SPEC-150",
         "تحفة الأطفال «فالأول الإخفاء عند الباء»؛ هداية القاري 1:191",
         ("meem-ikhfa-tarmihim", "meem-ikhfa-yatasim")),
    # -------------------------------------------------- P8 general idgham
    Ruling("R160_MUTAMATHILAYN", "P8",
         "إدغام المتماثلين الصغير",
         "idgham mutamathilayn saghir",
         "SPEC-160",
         "الجزرية «وأولي مثل وجنس إن سكن» أدغم؛ النشر 2:18",
         ("mutamathil-yudrikkum", "meem-idgham-lahum-ma")),
    Ruling("R161_NAQIS_TA_NO_QALQALAH", "P8",
         "الإدغام الناقص للطاء في التاء (بقاء الإطباق ولا قلقلة)",
         "naqis taa idgham: itbaq retained, no qalqalah",
         "SPEC-161",
         "الجزرية «وبين الإطباق من أحطت مع بسطت»؛ النشر 2:19",
         ("naqis-tah-basatta", "naqis-tah-ahatt", "naqis-tah-farrattum")),
    # ---------------------------------------------------------- P9 ghunna
    Ruling("R170_GHUNNA_MUSHADDADAH", "P9",
         "غنة النون والميم المشددتين",
         "ghunna of mushaddad noon and meem",
         "SPEC-170",
         "تحفة الأطفال «وغن ميمًا ثم نونًا شددا»؛ لطائف الإشارات 1:350",
         ("ghunna-noon-mushaddad", "ghunna-meem-amma", "ghunna-inna",
          "ghunna-thumma")),
    # ------------------------------------------------------------ P10 madd
    Ruling("R180_TABEEI", "P10",
         "المد الطبيعي",
         "madd tabee'i (2)",
         "SPEC-180",
         "تحفة الأطفال «والمد أصلي وفرعي له»",
         ("madd-tabeei-qala",)),
    Ruling("R180_PAUSAL_GLIDE", "P10",
         "الحرف اللين الناشئ بإسكان الوقف",
         "waqf iskan exposing the leen glide",
         "SPEC-180",
         "الشاطبية باب المد؛ النشر 1:333",
         ("madd-leen-quraysh", "madd-leen-khawf")),
    Ruling("R181_BADAL", "P10",
         "مد البدل",
         "madd al-badal (2)",
         "SPEC-180",
         "الشاطبية باب المد؛ النشر 1:339",
         ("madd-badal",)),
    Ruling("R183_SILAH_WAQF_DROP", "P10",
         "سقوط صلة هاء الضمير وقفًا",
         "silah dropped at waqf",
         "SPEC-183",
         "الشاطبية أبيات 158-159؛ سراج القارئ 1:45",
         ("madd-silah-sughra", "pausal-iskan-alamin"),
         note="stated jointly by the silah row and the waqf-iskan row"),
    Ruling("R184_SILAH_KUBRA", "P10",
         "الصلة الكبرى قبل الهمز",
         "silah kubra before hamza",
         "SPEC-184",
         "الشاطبية بيت 158؛ النشر 1:306",
         ("madd-silah-kubra",)),
    Ruling("R185_MUTTASIL", "P10",
         "المد الواجب المتصل",
         "madd muttasil (4-5)",
         "SPEC-185",
         "الشاطبية باب المد؛ النشر 1:315 «فوجب أن لا يعتقد أن قصر المتصل جائز عند أحد من القراء»",
         ("madd-muttasil-jaa", "madd-muttasil-samaa")),
    Ruling("R185_MUTTASIL_WAQF", "P10",
         "المتصل الموقوف عليه (جواز الست)",
         "muttasil at waqf admits 6",
         "SPEC-185",
         "الشاطبية باب المد؛ النشر 1:315-346؛ هداية القاري",
         ("sup-madd-amounts",)),
    Ruling("R186_MUNFASIL", "P10",
         "المد الجائز المنفصل",
         "madd munfasil (4-5)",
         "SPEC-186",
         "الشاطبية؛ النشر 1:322",
         ("madd-munfasil-bima-unzila",)),
    Ruling("R187_LAZIM_MUTHAQQAL", "P10",
         "المد اللازم الكلمي",
         "madd lazim kalimi (6)",
         "SPEC-187",
         "تحفة الأطفال «ولازم إن السكون أصلا»؛ النشر 1:342",
         ("madd-lazim-daalleen", "madd-lazim-haaqqah", "madd-lazim-taammah",
          "madd-lazim-mukhaffaf-aalaan")),
    Ruling("R187_R188_LAZIM", "P10",
         "المد اللازم الحرفي",
         "madd lazim harfi (6)",
         "SPEC-187",
         "تحفة الأطفال «واللازم الحرفي أول السور»؛ النشر 1:346",
         ("madd-harfi-laam", "madd-harfi-meem", "madd-harfi-kaf-19-1",
          "madd-harfi-sad-19-1")),
    Ruling("R188_AIN_LEEN_LAZIM", "P10",
         "عَيْن: اللين اللازم الحرفي (الوجهان والإشباع مقدم)",
         "'ayn: lazim leen, {4,6} with 6 preferred",
         "SPEC-190",
         "الشاطبية بيت 177؛ هداية القاري 1:343؛ حجة القراءات 1:521-522",
         ("madd-ain-19-1",)),
    Ruling("R189_AARED", "P10",
         "المد العارض للسكون",
         "madd 'aared lil-sukun (2/4/6)",
         "SPEC-189",
         "تحفة الأطفال «ومثل ذا إن عرض السكون»",
         ("madd-aared-nastaeen",)),
    Ruling("R190_LEEN", "P10",
         "مد اللين",
         "madd al-leen (2/4/6 at waqf)",
         "SPEC-190",
         "الشاطبية باب المد؛ النشر 1:333",
         ("madd-leen-quraysh", "madd-leen-khawf")),
    Ruling("R190B_SALASILA_ITHBAT", "P10",
         "سَلَاسِلَا: إثبات الألف وقفًا ووجهه",
         "salasila waqf alif ithbat",
         "SPEC-184",
         "طيبة النشر (سلاسلا نوّن)؛ النويري 2:603؛ العميد 1:160-161",
         ("alif7-salasila-wasl",)),
    Ruling("R190C_AATAANI_HADHF", "P10",
         "آتَانِ: وجها الوقف (إثبات الياء المقدم وحذفها)",
         "aataani waqf wajhan",
         "SPEC-184",
         "الشاطبية بيت 429؛ هداية القاري 2:544-545؛ إبراز المعاني 1:309",
         ("sup-aataani-wajh",)),
    # ------------------------------------------------------- P11 qalqalah
    Ruling("R200_QALQALAH_SUGHRA", "P11",
         "القلقلة الصغرى",
         "qalqalah sughra",
         "SPEC-200",
         "الشاطبية بيت 1158 «وفي قطب جد خمس قلقلة»؛ النشر 1:203",
         ("qlq-sughra-qaf", "qlq-sughra-tah", "qlq-sughra-beh",
          "qlq-sughra-jeem", "qlq-sughra-dal")),
    Ruling("R201_QALQALAH_KUBRA", "P11",
         "القلقلة الكبرى",
         "qalqalah kubra (waqf)",
         "SPEC-200",
         "الجزرية «وبينن مقلقلًا إن سكنا وإن يكن في الوقف كان أبينا»؛ هداية القاري 1:84-87",
         ("qlq-kubra-falaq", "qlq-kubra-ahad", "qlq-kubra-muheet",
          "qlq-kubra-bahij")),
    Ruling("R202_QALQALAH_AKBAR", "P11",
         "القلقلة الأكبر (الموقوف عليه مشددًا)",
         "qalqalah akbar (waqf on mushaddad)",
         "SPEC-200",
         "الجزرية «وبينن مقلقلًا إن سكنا وإن يكن في الوقف كان أبينا»؛ هداية القاري 1:84-87",
         ("qlq-kubra-tabb", "sup2-qalqalah-akbar")),
    # ------------------------------------------------------- P12 tafkheem
    Ruling("R210_ISTILA", "P12",
         "تفخيم حروف الاستعلاء ومراتبه",
         "isti'la tafkheem and its maraatib",
         "SPEC-210",
         "المقدمة الجزرية (باب صفات الحروف)؛ النويري 1:237-238",
         ("sup-sifat-sets", "sup2-tafkheem-maratib"),
         note="the letter set is stated by the sifat row, the grading by "
              "the maraatib row"),
    Ruling("R211_REH", "P12",
         "أحكام الراء تفخيمًا وترقيقًا",
         "the raa decision table",
         "SPEC-210",
         "الجزرية باب الراءات «ورقق الراء إذا ما كسرت»؛ هداية القاري 1:130",
         ("ra-fath-tafkheem", "ra-damm-tafkheem", "ra-kasr-tarqeeq",
          "ra-sakin-after-fath", "ra-sakin-after-damm",
          "ra-sakin-after-kasr-tarqeeq", "ra-sakin-kasr-istila-mirsad",
          "ra-firq-wasl-tarqeeq", "ra-nudhur-waqf-tarqeeq",
          "ra-yasr-waqf-tarqeeq", "ra-fajr-waqf-tafkheem",
          "ra-khabir-waqf-tarqeeq")),
    Ruling("R211_WAQF_KHILAF", "P12",
         "فرش راءات الوقف الخلافية (مصر، القطر، أسر)",
         "the waqf raa khilaf words",
         "SPEC-210",
         "النشر 2:105، 2:110؛ النويري 2:33 «وأختار في مصر التفخيم وفي القطر الترقيق نظرا للوصل وعملا بالأصل»؛ هداية القاري 1:130-133",
         ("sup-misr-qitr-asr",)),
    Ruling("R212_LAM_JALALA", "P12",
         "تفخيم لام الجلالة وترقيقها",
         "lam al-jalala tafkheem/tarqeeq",
         "SPEC-210",
         "الجزرية «وفخم اللام من اسم الله عن فتح أو ضم»",
         ("jalala-tarqeeq-after-kasr", "jalala-tafkheem-after-fath")),
    Ruling("R214_IKHFA_TAFKHEEM", "P12",
         "تبعية غنة الإخفاء لما بعدها تفخيمًا وترقيقًا",
         "ikhfa ghunna follows the trigger's tafkheem",
         "SPEC-210",
         "هداية القاري 1:181 «ومن تمام كيفية أدائها اتباعها لما بعدها من الحروف تفخيما وترقيقا»",
         ("sup-ghunna-tabiyya", "ikhfa-sad-mofakham", "ikhfa-tah-mofakham",
          "ikhfa-qaf-mofakham")),
    # ------------------------------------------------------- P13 one-offs
    Ruling("R220_ISHMAM", "P13",
         "إشمام تَأْمَنَّا",
         "ishmam of ta'manna, 12:11",
         "SPEC-220",
         "الشاطبية؛ هداية القاري 1:259-261؛ النشر 2:126",
         ("sup-taamanna-ishmam",)),
    Ruling("R220B_TAAMANNA_IKHTILAS", "P13",
         "اختلاس تَأْمَنَّا (الوجه الثاني)",
         "ikhtilas wajh of ta'manna",
         "SPEC-013b",
         "الشاطبية؛ هداية القاري 1:259-261؛ النشر 2:126",
         ("sup-taamanna-ishmam",)),
    Ruling("R221_IMALA", "P13",
         "إمالة مَجْر۪ىٰهَا",
         "imala, 11:41",
         "SPEC-221",
         "الشاطبية؛ (الموضع الوحيد لحفص)",
         ("oneoff-imala",)),
    Ruling("R222_TASHEEL", "P13",
         "تسهيل ءَا۬عْجَمِيٌّ",
         "tasheel, 41:44",
         "SPEC-222",
         "الشاطبية؛ (الموضع الوحيد لحفص)",
         ("oneoff-tasheel",)),
)


def _well_formed_id(rid: str) -> bool:
    """R + three digits + optional [A-Z0-9_] tail, checked without regex:
    the engine bans pattern matching outright (tests/test_no_regex_rules.py)."""
    if len(rid) < 4 or rid[0] != "R" or not rid[1:4].isdigit():
        return False
    tail = rid[4:]
    return all(c == "_" or c.isdigit() or (c.isupper() and c.isascii())
               for c in tail)


def _validate() -> None:
    seen: set[str] = set()
    for r in RULINGS:
        if not _well_formed_id(r.id):
            raise ValueError(f"malformed rule id: {r.id}")
        if r.id in seen:
            raise ValueError(f"duplicate rule id: {r.id}")
        seen.add(r.id)
        want = PHASE_BY_PREFIX.get(r.id[:3])
        if want is None or r.phase != want:
            raise ValueError(
                f"{r.id}: phase {r.phase} does not match id range ({want})")
        if not r.covered_by:
            raise ValueError(f"{r.id}: empty coverage")
        if not r.cite.strip():
            raise ValueError(f"{r.id}: empty citation")


_validate()

BY_ID: dict[str, Ruling] = {r.id: r for r in RULINGS}

#: rule id -> covering golden row ids (the completeness gate's view).
COVERAGE: dict[str, tuple[str, ...]] = {r.id: r.covered_by for r in RULINGS}
