"""Locate every citation of the rulings register on a page of a named print.

For each ruling of the register (src/quran_g2p/rules/registry.py) and each
part of its citation, find the passage in the text of one identified edition
and record the volume, page (and bayt where the edition prints its number),
a verbatim excerpt from that page, and the public URL of that page.

The text is the Shamela library (al-Maktaba al-Shamila 4), every book used
here carrying the card note «ترقيم الكتاب موافق للمطبوع»: its page numbers
are those of the print the card names. Each located page is public at
https://shamela.ws/book/<book>/<page id>.

`status`, strongest evidence first:
  quoted         the «...» text the citation quotes is on the page (on a
                 neighbouring page, up to 3 away, `page_agrees` is false)
  bayt           the cited bayt number is printed on the page and the bayt
                 holds the ruling's topic terms
  on_cited_page  the cited page holds the ruling's topic terms, every group
                 of them within PROX letters; the excerpt is the sentence
                 that holds them
  located        the citation names the work, or a chapter of it, with no
                 place: the page is the only one of the work, or the first of
                 the named chapter, that holds the terms (`pages_matching`)
  candidate      not confirmed: the terms are only on a neighbouring page of
                 the one cited, or on several pages of a whole work
  not_found      with the reason
  note           the part names a topic or a mushaf convention, not a work
Topic terms are matched in the body of a page, headings left out, and in a
poem one bayt at a time. A quotation the cited work lacks is looked for in
the other works (`quote_found` false, `quote_elsewhere`).

    python tools/locate_citations.py            # artifacts/citations/ and
                                                # docs/CITATION-PAGES.md
    python tools/locate_citations.py --online   # also fetch every URL and
                                                # find the excerpt on the page

SHAMELA4 names the corpus root (default F:/shamela4): one directory per book
with book_metadata.json, toc.jsonl and pages.jsonl.
"""
from __future__ import annotations

import argparse
import hashlib
import html
import json
import os
import re
import sys
import time
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from quran_g2p.rules.registry import RULINGS  # noqa: E402

SH = Path(os.environ.get("SHAMELA4", "F:/shamela4"))
OUT = ROOT / "artifacts" / "citations"
DRIFT = 3
AR_DIGITS = str.maketrans("٠١٢٣٤٥٦٧٨٩", "0123456789")

# ---------------------------------------------------------------------------
# The editions. Local Shamela book id -> the work and the print, in English.
# The Arabic card (betaka) is copied from the corpus into editions.jsonl.
# ---------------------------------------------------------------------------
EDITIONS = {
    2832: ("Hirz al-Amani wa-Wajh al-Tahani (al-Shatibiyyah)", "al-Shatibi (d. 590 AH)",
           "ed. Muhammad Tamim al-Zu'bi, Maktabat Dar al-Huda and Dar al-Ghawthani lil-Dirasat al-Qur'aniyyah, 4th ed., 1426 AH / 2005"),
    4484: ("al-Muqaddimah al-Jazariyyah", "Ibn al-Jazari (d. 833 AH)",
           "Dar al-Mughni, 1st ed., 1422 AH / 2001"),
    561: ("al-Muqaddimah al-Jazariyyah", "Ibn al-Jazari (d. 833 AH)",
          "ed. 'Abd al-Muhsin ibn Muhammad al-Qasim, 2nd ed., 1441 AH / 2020"),
    3459: ("Tuhfat al-Atfal wa-l-Ghilman", "al-Jamzuri (d. after 1198 AH)",
           "with notes by 'Ali Muhammad al-Dabba' (the card names no publisher or year)"),
    5932: ("al-Nashr fi al-Qira'at al-'Ashr", "Ibn al-Jazari (d. 833 AH)",
           "ed. 'Ali Muhammad al-Dabba', al-Matba'ah al-Tijariyyah al-Kubra (photo-reprint), 2 vols"),
    5988: ("Hidayat al-Qari ila Tajwid Kalam al-Bari", "'Abd al-Fattah al-Marsafi (d. 1409 AH)",
           "Maktabat Taybah, Madinah, 2nd ed., 2 vols (continuous pagination)"),
    7824: ("Siraj al-Qari al-Mubtadi wa-Tidhkar al-Muqri' al-Muntahi", "Ibn al-Qasih (d. 801 AH)",
           "revised by 'Ali al-Dabba', Matba'at Mustafa al-Babi al-Halabi, Egypt, 3rd ed., 1373 AH / 1954"),
    1878: ("al-Taysir fi al-Qira'at al-Sab'", "Abu 'Amr al-Dani (d. 444 AH)",
           "ed. Otto Pretzl, Dar al-Kitab al-'Arabi, Beirut, 2nd ed., 1404 AH / 1984"),
    8430: ("al-Taysir fi al-Qira'at al-Sab'", "Abu 'Amr al-Dani (d. 444 AH)",
           "ed. Khalaf Hammud Salim al-Shaghdali, Dar al-Andalus, Ha'il, 1st ed., 1436 AH / 2015"),
    1879: ("Kitab al-Sab'ah fi al-Qira'at", "Ibn Mujahid (d. 324 AH)",
           "ed. Shawqi Dayf, Dar al-Ma'arif, Egypt, 2nd ed., 1400 AH"),
    1880: ("Hujjat al-Qira'at", "Abu Zur'ah Ibn Zanjalah (d. c. 403 AH)",
           "ed. Sa'id al-Afghani, Dar al-Risalah (the card names no year)"),
    7175: ("al-Hujjah lil-Qurra' al-Sab'ah", "Abu 'Ali al-Farisi (d. 377 AH)",
           "ed. Badr al-Din Qahwaji and Bashir Juwayjabi, Dar al-Ma'mun lil-Turath, Damascus and Beirut, 2nd ed., 1413 AH / 1993, 7 vols"),
    1887: ("al-Muhkam fi Naqt al-Masahif", "Abu 'Amr al-Dani (d. 444 AH)",
           "ed. 'Izzah Hasan, Dar al-Fikr, Damascus, 2nd ed., 1407 AH"),
    1326: ("Dalil al-Hayran 'ala Mawrid al-Zam'an", "al-Marighni (d. 1349 AH)",
           "Dar al-Hadith, Cairo (the card names no year)"),
    6461: ("Ghayth al-Naf' fi al-Qira'at al-Sab'", "al-Safaqisi (d. 1118 AH)",
           "ed. Ahmad Mahmud 'Abd al-Sami' al-Shafi'i al-Hafyan, Dar al-Kutub al-'Ilmiyyah, Beirut, 1st ed., 1425 AH / 2004"),
    825: ("Fath al-Wasid fi Sharh al-Qasid", "al-Sakhawi (d. 643 AH)",
          "ed. Ahmad 'Adnan al-Zu'bi, Maktabat Dar al-Bayan, Kuwait, 1st ed., 1423 AH / 2002, 2 vols"),
    1870: ("Ibraz al-Ma'ani min Hirz al-Amani", "Abu Shamah (d. 665 AH)",
           "ed. Ibrahim 'Atwah 'Awad, Matba'at Mustafa al-Babi al-Halabi, Cairo, 1402 AH / 1982, 2 vols (continuous pagination)"),
    7801: ("Sharh Tayyibat al-Nashr", "al-Nuwayri (d. 857 AH)",
           "ed. Majdi Muhammad Surur Sa'd Baslum, Dar al-Kutub al-'Ilmiyyah, Beirut, 1st ed., 1424 AH / 2003, 2 vols"),
    6727: ("Lata'if al-Isharat li-Funun al-Qira'at", "al-Qastallani (d. 923 AH)",
           "ed. Khalid Hasan Abu al-Jud, Maktabat Awlad al-Shaykh lil-Turath, Giza, 1st ed., 10 vols"),
    52: ("al-Budur al-Zahirah fi al-Qira'at al-'Ashr al-Mutawatirah", "'Abd al-Fattah al-Qadi (d. 1403 AH)",
         "Dar al-Kitab al-'Arabi, Beirut, 1st ed., 1401 AH / 1981"),
    4654: ("al-'Amid fi 'Ilm al-Tajwid", "Mahmud 'Ali Bassah (d. after 1367 AH)",
           "ed. Muhammad al-Sadiq Qamhawi, Dar al-'Aqidah, Alexandria, 1st ed., 1425 AH / 2004"),
    2838: ("Tayyibat al-Nashr fi al-Qira'at al-'Ashr", "Ibn al-Jazari (d. 833 AH)",
           "ed. Muhammad Tamim al-Zu'bi, Dar al-Huda, Jeddah, 1st ed., 1414 AH / 1994"),
}
MATN = {2832, 4484, 561, 3459, 2838}
NUMBERED = {2832, 2838}       # editions that print the number of every bayt

# citation token -> Shamela books, in the order tried
WORKS = {
    "المقدمة الجزرية": [4484, 561], "الجزرية": [4484, 561],
    "الشاطبية": [2832], "تحفة الأطفال": [3459], "طيبة النشر": [2838],
    "النشر": [5932], "هداية القاري": [5988], "سراج القارئ": [7824],
    "التيسير": [1878, 8430], "الحجة للقراء السبعة": [7175], "السبعة": [1879],
    "حجة القراءات": [1880], "المحكم في نقط المصاحف": [1887],
    "دليل الحيران": [1326], "غيث النفع": [6461], "فتح الوصيد": [825],
    "إبراز المعاني": [1870], "النويري": [7801], "لطائف الإشارات": [6727],
    "البدور الزاهرة": [52], "العميد": [4654],
}

# ---------------------------------------------------------------------------
# Topic terms per ruling: groups that must all occur within PROX letters of
# each other (any word of a group). Plain spelling; normalised before use.
# ---------------------------------------------------------------------------
PROX = 250
T = {
    "R011_MUQATTAAT": [["فواتح السور", "الفواتح", "حروف الهجاء", "حي طاهر"]],
    "R012_SEEN_SAD": [["يبصط", "بصطة", "المصيطرون", "بمصيطر", "مصيطر"]],
    "R012B_DAAF_DAMM": [["ضعف", "ضعفا"]],
    "R013_ELIDED_WAW_LIYASUU": [["ليسوءوا", "يسوءوا", "ليسوء"]],
    "R014B_ISTIFHAM_TASHEEL": [["تسهل", "تسهيل", "يسهل", "سهل", "بين بين"]],
    "R110_WASL_START": [["همز الوصل", "همزة الوصل"], ["ابدأ", "ابدا", "ابتدئ", "الابتداء"]],
    "R110_BADAL_IBTIDA": [["ابتدئ", "الابتداء", "ابتداء", "ابتدأ"], ["ايت", "ائت", "ايتوني", "ائتوني", "اوتمن", "ابدل", "ابدال", "يبدل", "تبدل"]],
    "R112_STRIP_INITIAL_SHADDA": [["التشديد", "الشدة", "مشدد", "المشدد"], ["الابتداء", "ابتدئ", "ابتدأ", "يبتدأ"]],
    "R120_ISKAN": [["السكون", "الاسكان"], ["الوقف"]],
    "R121_MADD_EWAD": [["العوض", "عوض", "عوضا", "بدلا", "بدل", "ابدال"], ["التنوين", "تنوين", "المنون"], ["الالف", "بالالف", "الف"]],
    "R121_EWAD_SEAT_SILENT": [["التنوين", "تنوين", "المنون"], ["الالف", "بالالف", "الف"]],
    "R122_TAA_MARBUTA_WAQF": [["هاء التانيث", "تاء التانيث"], ["بالهاء", "هاء"]],
    "R123_RAWM": [["الروم", "روم", "رومك"]],
    "R123_ISHMAM": [["الاشمام", "اشمام", "اشمم"]],
    "R130_WASL_ELISION": [["همزة الوصل", "همز الوصل", "الف الوصل"], ["تسقط", "يسقط", "سقطت", "تحذف", "حذفت", "الدرج", "سقوط", "تثبت"]],
    "R131_MADD_SHORTENING": [["الساكنين"], ["حرف المد", "حروف المد"]],
    "R131_NOON_WIQAYA": [["التنوين", "تنوين"], ["الساكنين"], ["كسر", "بالكسر", "يكسر", "يحرك"]],
    "R132_SAKT": [["سكت", "السكت", "سكتة", "سكته"], ["حفص", "عوجا", "مرقدنا", "راق", "ران"]],
    "R132_MALIYAH_SAKT": [["ماليه"], ["هلك"]],
    "R133_R160_IDGHAM_KAMIL": [["ادغام", "الادغام", "يدغم", "ادغم", "مدغم", "وجب ادغام"], ["مثلين", "المثلين", "التعريف", "الشمسية"]],
    "R134_LAM_JALALA_ALIF": [["اسم الله"]],
    "R135_MEEM_ALLAH": [["الم الله"]],
    "R136_BASMALA_JOINS": [["بسمل", "البسملة", "التسمية"], ["السورتين", "سورتين", "الانفال", "براءة"]],
    "R140_IZHAR": [["الاظهار", "اظهار", "المظهر", "يظهر"], ["الحلق", "حلق", "الحلقية"]],
    "R140_IZHAR_HALQI": [["الاظهار", "اظهار", "المظهر", "يظهر"], ["الحلق", "حلق", "الحلقية"]],
    "R141_IDGHAM_GHUNNA": [["ادغام", "الادغام", "يدغم", "مدغم"], ["يرملون", "بغنة", "غنة", "ينمو"]],
    "R141_IDGHAM_GHUNNA_NAQIS": [["الواو", "الياء", "ينمو", "بينمو"], ["الغنة", "غنة", "بغنة"]],
    "R141_IZHAR_MUTLAQ": [["الدنيا", "دنيا", "بنيان", "صنوان", "قنوان"]],
    "R142_IDGHAM_BILA_GHUNNA": [["اللام والراء", "اللام والرا", "بغير غنة", "بلا غنة"]],
    "R143_IQLAB": [["الاقلاب", "القلب", "قلبا", "تقلب", "يقلب", "اقلاب"], ["الباء", "ميم", "ميما"]],
    "R144_IKHFA": [["الاخفاء", "اخفاء", "يخفي", "تخفي"], ["النون", "التنوين", "الحروف", "احرف"]],
    "R150_IKHFA_SHAFAWI": [["الشفوي", "الشفوية", "الميم الساكنة"], ["الباء", "الاخفاء", "اخفاء"]],
    "R160_MUTAMATHILAYN": [["المثلين", "مثلين", "المتماثلين", "مثل"], ["ادغام", "ادغم", "الادغام", "مدغم"]],
    "R161_NAQIS_TA_NO_QALQALAH": [["بسطت", "احطت", "فرطت"]],
    "R162_NAKHLUQKUM_NAQIS": [["نخلقكم"]],
    "R170_GHUNNA_MUSHADDADAH": [["غنة", "الغنة", "غن"], ["مشدد", "المشدد", "شددا", "المشددتين", "المشددة", "مشددة", "المشددين"]],
    "R180_TABEEI": [["الطبيعي", "طبيعي", "طبيعيا", "اصلي"]],
    "R180_PAUSAL_GLIDE": [["اللين", "لين"], ["الوقف", "وقف", "سكون", "ساكن"]],
    "R181_BADAL": [["بعد همز", "بعد الهمز", "البدل", "تقدم الهمز", "بعد همزة"]],
    "R183_SILAH_WAQF_DROP": [["الصلة", "صلة", "يصلوا", "وصلا", "الكناية", "هاء الضمير", "مضمر"]],
    "R184_SILAH_KUBRA": [["الصلة", "صلة", "يصلوا", "وصلا", "الكناية", "هاء الضمير", "مضمر"]],
    "R185_MUTTASIL": [["المتصل", "متصل", "يتصل", "اتصل", "اتصاله"]],
    "R185_MUTTASIL_WAQF": [["المتصل", "متصل"], ["الوقف", "وقفا", "للوقف", "الموقوف", "سكون الوقف"]],
    "R186_MUNFASIL": [["المنفصل", "منفصل", "ينفصل", "انفصل"]],
    "R187_LAZIM_MUTHAQQAL": [["اللازم", "لازم"], ["السكون", "ساكن", "مدغم", "مشدد"]],
    "R187_R188_LAZIM": [["اللازم", "لازم"], ["الفواتح", "فواتح", "السور", "الحرفي", "حروف الهجاء"]],
    "R188_AIN_LEEN_LAZIM": [["عين"], ["الطول", "المد", "مد", "التوسط", "الوجهان", "وجهان", "اللين"]],
    "R189_AARED": [["عارض", "العارض", "عرض"]],
    "R190_LEEN": [["اللين", "لين"], ["الياء", "الواو", "حرفي", "حرفا"]],
    "R190B_SALASILA_ITHBAT": [["سلاسلا", "سلاسل"]],
    "R190C_AATAANI_HADHF": [["اتان", "اتاني"]],
    "R200_QALQALAH_SUGHRA": [["قلقلة", "القلقلة", "قطب جد"]],
    "R201_QALQALAH_KUBRA": [["قلقلة", "القلقلة", "مقلقلا"]],
    "R202_QALQALAH_AKBAR": [["قلقلة", "القلقلة", "مقلقلا"]],
    "R210_ISTILA": [["الاستعلاء", "استعلاء", "المستعلية", "علو"]],
    "R211_REH": [["الراء", "الرا", "الراءات", "راء"], ["رقق", "فخم", "ترقيق", "تفخيم", "ترقق", "تفخم", "يرقق", "يفخم"]],
    "R211_WAQF_KHILAF": [["مصر", "القطر", "اسر"], ["الوقف", "وقف", "يوقف", "الراء"]],
    "R212_LAM_JALALA": [["اسم الله"]],
    "R214_IKHFA_TAFKHEEM": [["تفخيما", "التفخيم"], ["ترقيقا", "الترقيق"]],
    "R220_ISHMAM": [["تامنا", "تامننا"]],
    "R220B_TAAMANNA_IKHTILAS": [["تامنا", "تامننا"]],
    "R221_IMALA": [["مجراها", "مجريها"], ["حفص", "حفصهم"]],
    "R222_TASHEEL": [["اعجمي"]],
}

# Terms for one ruling in one work, where the work words it its own way.
# Each was read off the page text it is matched in.
TW = {
    ("R185_MUTTASIL", "الشاطبية"): [["لقي الهمز طولا"]],
    ("R185_MUTTASIL_WAQF", "الشاطبية"): [["سكون الوقف"]],
    ("R190_LEEN", "الشاطبية"): [["سكون الوقف للكل"]],
    ("R180_PAUSAL_GLIDE", "الشاطبية"): [["سكون الوقف للكل"]],
    ("R186_MUNFASIL", "الشاطبية"): [["ينفصل"]],
    ("R011_MUQATTAAT", "تحفة الأطفال"): [["فواتح السور"]],
    ("R141_IDGHAM_GHUNNA_NAQIS", "تحفة الأطفال"): [["بينمو"]],
    ("R110_BADAL_IBTIDA", "الجزرية"): [["ابدل", "ابدال", "يبدل"]],
    ("R121_EWAD_SEAT_SILENT", "تحفة الأطفال"): [["التنوين"], ["الف", "الالف"]],
    ("R222_TASHEEL", "الشاطبية"): [["فصلت"], ["صحبه"]],
    ("R220_ISHMAM", "الشاطبية"): [["ادغم مع اشمامه"]],
    ("R220_ISHMAM", "هداية القاري"): [["الاشمام", "اشمام", "باشمام"], ["الاختلاس", "اختلاس"]],
    ("R220B_TAAMANNA_IKHTILAS", "هداية القاري"): [["الاختلاس", "اختلاس"], ["الاشمام", "اشمام", "باشمام"]],
    ("R185_MUTTASIL_WAQF", "هداية القاري"): [["متطرفا وموقوفا عليه"]],
    ("R162_NAKHLUQKUM_NAQIS", "هداية القاري"): [["نخلقكم"], ["الناقص", "ناقصا"]],
    # the page names ta'manna in a note on rawm; ishmam must be beside it
    ("R220_ISHMAM", "النشر"): None,
}


class Near(list):
    """Term groups that must fall closer together than PROX."""
    def __init__(self, groups, prox):
        super().__init__(groups)
        self.prox = prox


TW[("R220_ISHMAM", "النشر")] = Near([["تامنا", "تامننا"], ["الاشمام", "اشمام", "باشمام"]], 80)

# Where to search a citation that names a work, or a chapter of it, with no
# place: the TOC title of the chapter (absent: the whole work).
CHAPTER = {
    ("R121_MADD_EWAD", "هداية القاري"): "الباب الحادي عشر",
    ("R122_TAA_MARBUTA_WAQF", "هداية القاري"): "الباب السادس عشر",
    ("R130_WASL_ELISION", "هداية القاري"): "الباب الخامس عشر",
    ("R185_MUTTASIL_WAQF", "هداية القاري"): "الباب الحادي عشر",
    ("R180_PAUSAL_GLIDE", "الشاطبية"): "باب المد والقصر",
    ("R181_BADAL", "الشاطبية"): "باب المد والقصر",
    ("R185_MUTTASIL", "الشاطبية"): "باب المد والقصر",
    ("R185_MUTTASIL_WAQF", "الشاطبية"): "باب المد والقصر",
    ("R186_MUNFASIL", "الشاطبية"): "باب المد والقصر",
    ("R190_LEEN", "الشاطبية"): "باب المد والقصر",
    ("R210_ISTILA", "المقدمة الجزرية"): "صفات",
}

# What a reader of a row should know that the row cannot show.
REMARK = {
    ("R134_LAM_JALALA_ALIF", "الجزرية"):
        "The cited line states the tafkheem of the lam of the name Allah; the dagger alif after it is not in the line.",
    ("R185_MUTTASIL_WAQF", "الشاطبية"):
        "The bayt gives two ways at the sukun of a stop for every madd before a sukun; it does not name the muttasil.",
    ("R180_PAUSAL_GLIDE", "الشاطبية"):
        "The bayt gives the lengthening of the leen letter at the sukun of a stop for every reader.",
    ("R133_R160_IDGHAM_KAMIL", "تحفة الأطفال"):
        "The quoted bayt opens the two cases of the lam of al and states the first, its izhar; the second, "
        "its idgham, is two abyat below on the same page: «ثَانِيهِمَا إِدْغَامُهَا فِي أَرْبَعِ ... وَعَشْرَةٍ أَيْضًا وَرَمْزَهَا فَعِ».",
}

# ---------------------------------------------------------------------------
# Text
# ---------------------------------------------------------------------------
TITLE = re.compile(r"<span data-type=['\"]title['\"][^>]*>.*?</span>", re.S)
TAG = re.compile(r"<[^>]+>")
FOOTMARK = re.compile(r"\([\d٠-٩]+\)|¬[\d٠-٩]+")
DROP = set(chr(c) for c in range(0x064B, 0x0660)) | {"ٰ", "ـ", "ۡ", "ۢ", "ۥ", "ۦ", "ۭ"}
FOLD = {"إ": "ا", "أ": "ا", "آ": "ا", "ٱ": "ا", "ى": "ي", "ة": "ه", "ؤ": "و", "ئ": "ي"}
PROCLITIC = {"", "و", "ف", "ب", "ل", "ك", "ال", "وال", "فال", "بال", "لل", "ول", "وب", "فب", "وك", "كال", "ولل", "فل"}
ENCLITIC = {"", "ا", "ه", "ها", "هم", "ك", "ي", "ن", "وا", "ات", "ين", "ون", "هما"}


def clean(raw: str, keep_titles: bool = False) -> str:
    """Page text as displayed, without headings (they are the book's
    navigation, not its statement), tags or footnote marks."""
    s = raw or ""
    if not keep_titles:
        s = TITLE.sub("\n", s)
    s = html.unescape(TAG.sub(" ", s))
    s = FOOTMARK.sub(" ", s)
    return s.replace("\r", "\n")


def norm_map(s: str):
    """Letters-and-spaces normalisation of `s`, and for each of its chars the
    index in `s` it came from."""
    out, src = [], []
    for i, ch in enumerate(s):
        if ch in DROP:
            continue
        ch = FOLD.get(ch, ch)
        if "ء" <= ch <= "ي":
            out.append(ch)
            src.append(i)
        elif out and out[-1] != " ":
            out.append(" ")
            src.append(i)
    while out and out[-1] == " ":
        out.pop()
        src.pop()
    return "".join(out), src


def norm(s: str) -> str:
    return norm_map(s)[0]


def positions(hay: str, needle: str):
    """(start, end) of each word-bounded occurrence: a proclitic may stand
    before the needle, and after a short needle only a short suffix."""
    out = []
    for m in re.finditer(re.escape(needle), hay):
        a, b = m.start(), m.end()
        pre = hay[hay.rfind(" ", 0, a) + 1:a]
        if pre not in PROCLITIC:
            continue
        nxt = hay.find(" ", b)
        suf = hay[b:len(hay) if nxt < 0 else nxt]
        if len(needle) >= 4 or " " in needle or suf in ENCLITIC:
            out.append((a, b))
    return out


def terms_span(nrm: str, groups):
    """(start, end) of the first place where every group hits within PROX
    letters of the first group's hit, else None."""
    prox = getattr(groups, "prox", PROX)
    hits = []
    for g in groups:
        h = sorted({x for w in g for x in positions(nrm, norm(w))})
        if not h:
            return None
        hits.append(h)
    for a0, b0 in hits[0]:
        span = [a0, b0]
        for h in hits[1:]:
            near = [x for x in h if abs(x[0] - a0) <= prox]
            if not near:
                break
            x = min(near, key=lambda x: abs(x[0] - a0))
            span = [min(span[0], x[0]), max(span[1], x[1])]
        else:
            return span[0], span[1]
    return None


# ---------------------------------------------------------------------------
# Corpus
# ---------------------------------------------------------------------------
class Book:
    def __init__(self, bid: int):
        cands = [d for cat in SH.iterdir() if cat.is_dir() for d in cat.glob(f"{bid}__*")]
        if not cands:
            raise SystemExit(f"book {bid} not in {SH}")
        self.dir, self.bid = cands[0], bid
        self.meta = json.loads((self.dir / "book_metadata.json").read_text(encoding="utf-8"))
        if "موافق للمطبوع" not in (self.meta.get("betaka_text") or ""):
            raise SystemExit(f"book {bid}: the card does not say its pages are the print's")
        self.web_id = self.meta["shamela_id"]
        self.matn = bid in MATN
        raw = (self.dir / "pages.jsonl").read_bytes()
        self.sha256 = hashlib.sha256(raw).hexdigest()
        self.pages, seq_of_row = [], {}
        for line in raw.decode("utf-8").splitlines():
            if not line.strip():
                continue
            d = json.loads(line)
            part = str(d.get("part") or "").translate(AR_DIGITS)
            p = {"pid": d["shamela_page_id"], "seq": d.get("sequence_num") or d["shamela_page_id"],
                 "part": int(part) if part.isdigit() else None, "page": d.get("page_num")}
            # topic terms are matched in the body (headings out); quotes in
            # the page as displayed, where a book may set a phrase as a heading
            p["segs"] = self._segments(clean(d.get("body")))
            p["segs_full"] = self._segments(clean(d.get("body"), keep_titles=True))
            seq_of_row[d["page_id"]] = p["seq"]
            self.pages.append(p)
        self.pages.sort(key=lambda p: p["seq"])
        self.has_parts = any(p["part"] is not None for p in self.pages)
        toc = [json.loads(l) for l in (self.dir / "toc.jsonl").read_text(encoding="utf-8").splitlines() if l.strip()]
        for t in toc:
            t["seq"] = seq_of_row.get(t["page_id"], 0)
        self.toc = sorted(toc, key=lambda t: t["seq"])

    def _segments(self, text):
        """Where a match may lie: each bayt of a poem (a line with the
        hemistich mark), else the whole page."""
        if not self.matn:
            n, src = norm_map(text)
            return [{"text": text, "lo": 0, "hi": len(text), "norm": n, "src": src}]
        segs, at = [], 0
        for line in text.split("\n"):
            lo, at = at, at + len(line) + 1
            if "..." in line or "…" in line:
                n, src = norm_map(line)
                segs.append({"text": text, "lo": lo, "hi": lo + len(line), "norm": n, "src": [lo + i for i in src]})
        return segs

    def at(self, vol, page):
        return [p for p in self.pages if p["page"] == page
                and (not self.has_parts or vol is None or p["part"] == vol)]

    def url(self, p):
        return f"https://shamela.ws/book/{self.web_id}/{p['pid']}"

    def chapter(self, frag):
        """Pages of the first TOC entry whose title holds `frag`, up to the
        next entry with the same parent."""
        f = norm(frag)
        for i, t in enumerate(self.toc):
            title = norm(t["title_text"])
            if f in title:
                head = title.split(" ")[0]       # "باب", "الباب": the next one of its kind ends it
                end = next((u["seq"] for u in self.toc[i + 1:]
                            if norm(u["title_text"]).split(" ")[0] == head and u["seq"] > t["seq"]), None)
                return [p for p in self.pages if p["seq"] >= t["seq"] and (end is None or p["seq"] <= end)]
        return []


_books: dict[int, Book] = {}


def book(bid: int) -> Book:
    if bid not in _books:
        _books[bid] = Book(bid)
    return _books[bid]


# ---------------------------------------------------------------------------
# Matching
# ---------------------------------------------------------------------------
def bayt_number(b: Book, p, seg):
    if b.bid not in NUMBERED:
        return None
    m = re.match(r"\s*([\d٠-٩]+)\s*-", seg["text"][seg["lo"]:seg["hi"]])
    return int(m.group(1).translate(AR_DIGITS)) if m else None


def seg_hit(seg, quote, groups):
    if quote:
        i = seg["norm"].find(quote)
        return (i, i + len(quote)) if i >= 0 else None
    return terms_span(seg["norm"], groups)


def search(b: Book, pages, quote, groups):
    """First (page, segment, span) in `pages` holding the quote or the terms,
    and how many pages hold them."""
    first, count = None, 0
    for p in pages:
        for seg in p["segs_full" if quote else "segs"]:
            h = seg_hit(seg, quote, groups)
            if h:
                count += 1
                if first is None:
                    first = (p, seg, h)
                break
    return first, count


def excerpt(b: Book, p, seg, span) -> str:
    text = seg["text"]
    if b.matn:
        s = text[seg["lo"]:seg["hi"]]
        s = re.sub(r"^\s*[\d٠-٩]+\s*-\s*", "", s)
    else:
        a = seg["src"][span[0]]
        z = seg["src"][max(span[1] - 1, span[0])] + 1
        lo = max(text.rfind(c, 0, a) for c in ".\n؟!:") + 1
        hi = min([h for h in (text.find(c, z) for c in ".\n؟!") if h >= 0] or [len(text)]) + 1
        if a - lo > 120:
            lo = text.find(" ", a - 120) + 1
        if hi - z > 120:
            hi = text.rfind(" ", z, z + 120)
        if len(text[lo:hi].strip()) < 60:          # a heading-like line: take the sentence after it too
            nxt = min([h for h in (text.find(c, hi) for c in ".؟!") if h >= 0] or [len(text)]) + 1
            hi = nxt if nxt - hi <= 220 else text.rfind(" ", hi, hi + 220)
        s = text[lo:hi]
    return " ".join(s.split()).strip(" .،:")


QUOTE = re.compile(r"«([^»]+)»")
VOLPAGE = re.compile(r"(\d+):(\d+)(?:-(\d+))?")
BAYT = re.compile(r"(?:بيتا?|أبيات)\s+(\d+)(?:-(\d+))?")
BARE = re.compile(r"(?<![\d:])(\d{1,4})(?:-(\d{1,4}))?(?![\d:])")


def token_of(part: str):
    for name in sorted(WORKS, key=len, reverse=True):
        if name in part:
            return name
    return None


def parse(part: str, tok: str):
    quotes = [norm(q.replace("...", " ").replace("…", " ")) for q in QUOTE.findall(part)]
    quote = max(quotes, key=len) if quotes else None
    rest = QUOTE.sub(" ", part).split(tok, 1)[1]
    loci = [(int(v), int(a), int(b or a)) for v, a, b in VOLPAGE.findall(rest)]
    bayts = [(int(a), int(b or a)) for a, b in BAYT.findall(rest)]
    if not loci and not bayts:
        nums = [(int(a), int(b or a)) for a, b in BARE.findall(rest)]
        if nums and all(x in MATN for x in WORKS[tok]):
            bayts = nums                     # a bare number after a poem is a bayt
        elif nums:
            loci = [(None, a, b) for a, b in nums]
    m = re.search(r"\d[\d:،\- ]*", rest)
    cited = re.sub(r"\s+", " ", m.group(0)).strip(" ،-") if m else None
    return quote, loci, bayts, cited


def attempt(b: Book, rule_id, tok, quote, groups, loci, bayts):
    """One edition, one kind of evidence (the quote, else the terms):
    (page, segment, span, match, page_agrees, pages_matching) or a reason."""
    kind = "register_quote" if quote else "topic"
    if bayts and b.bid in NUMBERED:
        want = {n for a, z in bayts for n in range(a, z + 1)}
        for p in b.pages:
            for seg in p["segs_full" if quote else "segs"]:
                if bayt_number(b, p, seg) in want:
                    h = seg_hit(seg, quote, groups)
                    if h:
                        return (p, seg, h, "bayt" if not quote else kind, True, None)
        return "the cited bayts hold neither the quote nor the topic terms"
    if loci and not b.matn:
        for v, a, z in loci:
            pages = [p for n in range(a, z + 1) for p in b.at(v, n)]
            f, _ = search(b, pages, quote, groups)
            if f:
                return (*f, kind, True, None)
        for v, a, z in loci:
            near = [p for n in list(range(a - DRIFT, a)) + list(range(z + 1, z + DRIFT + 1)) for p in b.at(v, n)]
            near.sort(key=lambda p: min(abs(p["page"] - a), abs(p["page"] - z)))
            f, _ = search(b, near, quote, groups)
            if f:
                return (*f, kind, False, None)
        return "the cited page, and the 3 pages on each side, hold neither the quote nor the topic terms"
    frag = CHAPTER.get((rule_id, tok))
    scope = b.chapter(frag) if frag else b.pages
    if frag and not scope:
        return f"no chapter «{frag}» in the table of contents"
    f, count = search(b, scope, quote, groups)
    if f:
        return (*f, kind if quote else "located", None, count)
    where = f"chapter «{frag}»" if frag else "the work"
    return f"{'the quote' if quote else 'the topic terms'} not found in {where}"


def locate(rule_id: str, part: str) -> dict:
    row = {"cited": part}
    tok = token_of(part)
    if tok is None:
        return {**row, "status": "note", "reason": "names a topic or a convention of the mushaf, not a work"}
    quote, loci, bayts, cited = parse(part, tok)
    row["page_cited"] = cited
    groups = TW.get((rule_id, tok)) or T.get(rule_id)
    reasons = []
    for evidence in ([quote, None] if quote else [None]):
        for bid in WORKS[tok]:
            b = book(bid)
            if bayts and b.bid not in NUMBERED and b.matn:
                reasons.append(f"{bid}: this edition prints no bayt numbers; searched the whole work")
            r = attempt(b, rule_id, tok, evidence, None if evidence else groups,
                        loci, bayts if b.bid in NUMBERED else [])
            if isinstance(r, str):
                reasons.append(f"{bid}: {r}")
                continue
            p, seg, span, how, agrees, count = r
            work, author, edition = EDITIONS[b.bid]
            note = REMARK.get((rule_id, tok))
            if bayts and b.bid not in NUMBERED:
                note = ((note + " ") if note else "") + "This edition prints no bayt numbers, so the cited bayt number is not checked."
            if how == "register_quote":
                status = "quoted"
            elif how == "bayt":
                status = "bayt"
            elif how == "topic":
                status = "on_cited_page" if agrees else "candidate"
            else:
                status = "located" if (count == 1 or CHAPTER.get((rule_id, tok))) else "candidate"
            extra = {}
            if quote and how != "register_quote":
                extra["quote_found"] = False
                extra["quote_elsewhere"] = quote_elsewhere(quote)
            return {**row, "status": status, **extra,
                    "work": work, "author": author, "edition": edition,
                    "work_ar": b.meta["title_ar"], "shamela_book": b.web_id,
                    "volume": p["part"] if b.has_parts else None, "page": p["page"],
                    "bayt": bayt_number(b, p, seg), "page_agrees": agrees,
                    "pages_matching": count, "excerpt": excerpt(b, p, seg, span),
                    "url": b.url(p), "remark": note}
    out = {**row, "status": "not_found", "reason": "; ".join(dict.fromkeys(reasons))}
    if quote:
        out["quote_found"] = False
        out["quote_elsewhere"] = quote_elsewhere(quote)
    return out


def quote_elsewhere(quote):
    """Where a quotation the cited work lacks is, in any work cited: the page
    holding the most of its five-word runs (all of them: the whole quotation)."""
    words = quote.split()
    runs = {" ".join(words[i:i + 5]) for i in range(max(1, len(words) - 4))}
    best = (0, None)
    for bid in sorted({x for ids in WORKS.values() for x in ids}):
        b = book(bid)
        for p in b.pages:
            n = sum(1 for r in runs if any(r in seg["norm"] for seg in p["segs_full"]))
            if n > best[0]:
                best = (n, (b, p))
    if not best[1]:
        return None
    b, p = best[1]
    loc = (f"{p['part']}:" if b.has_parts else "") + str(p["page"])
    whole = "the whole quotation" if best[0] == len(runs) else f"{best[0]} of its {len(runs)} five-word runs"
    return f"{EDITIONS[b.bid][0]} {loc} ({whole}), {b.url(p)}"


def run():
    rows = []
    for r in RULINGS:
        parts = [x.strip() for x in r.cite.split("؛") if x.strip()]
        for k, part in enumerate(parts, 1):
            rows.append({"rule_id": r.id, "n": k, **locate(r.id, part)})
    return rows


def editions_rows():
    out = []
    for bid in sorted(_books):
        b = _books[bid]
        work, author, edition = EDITIONS[bid]
        out.append({"shamela_book": b.web_id, "work": work, "author": author, "edition": edition,
                    "work_ar": b.meta["title_ar"], "card_ar": b.meta["betaka_text"].replace("\r", "\n"),
                    "pages_match_print": True, "url": f"https://shamela.ws/book/{b.web_id}",
                    "corpus_book_id": bid, "corpus_pages_sha256": b.sha256})
    return out


FIELDS = ["rule_id", "n", "cited", "status", "work", "author", "edition", "work_ar",
          "shamela_book", "volume", "page", "bayt", "page_cited", "page_agrees", "pages_matching",
          "excerpt", "url", "quote_found", "quote_elsewhere", "remark", "reason"]
SHOWN = ("quoted", "bayt", "on_cited_page", "located")
ORDER = ("quoted", "bayt", "on_cited_page", "located", "candidate", "not_found", "note")


def markdown(rows) -> str:
    """docs/CITATION-PAGES.md: every citation part with the page found."""
    tally = {k: sum(1 for r in rows if r["status"] == k) for k in ORDER}
    rules = {r["rule_id"] for r in rows}
    placed = {r["rule_id"] for r in rows if r["status"] in SHOWN}
    out = [
        "# Citation pages",
        "",
        "Every citation of the rulings register on a page of one named print, with the passage",
        "found there. Generated by `tools/locate_citations.py` from the Shamela library, whose",
        "page numbers for these books are those of the print its card names; each link opens that",
        "page. The data, with the excerpts in full, is `artifacts/citations/rule_citations.jsonl`;",
        "the editions, with their cards, are `artifacts/citations/editions.jsonl`.",
        "",
        f"**{len(rows)} citation parts: " + ", ".join(f"{v} {k}" for k, v in tally.items() if v) +
        f". {len(placed)} of {len(rules)} rulings have at least one page in the first four.**",
        "",
        "The status, strongest first: `quoted`, the citation's own quotation is on the page; `bayt`,",
        "the cited bayt number is printed there and the bayt holds the ruling's terms;",
        "`on_cited_page`, the cited page holds the ruling's terms, and the excerpt is the sentence",
        "that holds them; `located`, the citation names only the work (or a chapter), and the page",
        "is the only one of the work, or the first of the chapter, that holds the terms;",
        "`candidate`, not confirmed: the terms are only on a neighbouring page of the one cited, or",
        "on several pages of a whole work. A page marked `≠` is not the page cited.",
        "",
        "| ruling | as cited | work and edition | vol:page (bayt) | status |",
        "|---|---|---|---|---|",
    ]
    for r in rows:
        if r.get("url"):
            loc = (f"{r['volume']}:" if r.get("volume") else "") + str(r["page"])
            if r.get("bayt"):
                loc += f" (bayt {r['bayt']})"
            if r.get("page_agrees") is False:
                loc += " ≠"
            where = f"[{loc}]({r['url']})"
            work = f"{r['work']}, {r['edition']}"
            how = r["status"]
            if r.get("quote_found") is False:
                how += "; the quotation is not on this page" + (
                    f" (it is in {r['quote_elsewhere'].split(', http')[0]})" if r.get("quote_elsewhere") else "")
        else:
            where, work, how = "", "", f"{r['status']}: {r.get('reason', '')}"
        cited = r["cited"].replace("|", "/")
        out.append(f"| `{r['rule_id']}` | {cited} | {work} | {where} | {how} |")
    return "\n".join(out) + "\n"


def online_check(rows):
    """Fetch every located page and look for the normalised excerpt in it."""
    bad = 0
    for r in rows:
        if not r.get("url"):
            continue
        page, err = "", ""
        req = urllib.request.Request(r["url"], headers={"User-Agent": "Mozilla/5.0 (citation check)"})
        for attempt_no in range(3):
            try:
                page = urllib.request.urlopen(req, timeout=60).read().decode("utf-8", "replace")
                break
            except Exception as e:  # noqa: BLE001
                err = str(e)
                time.sleep(3 * (attempt_no + 1))
        ok = bool(page) and norm(r["excerpt"]) in norm(clean(page, keep_titles=True))
        a = page.find('class="nass')
        served = norm(clean(page[a:page.find('id="appended_pages"', a)])) if a >= 0 else ""
        m = re.search(r'data-page-num="(\d+)"', page)
        if ok:
            r["online"] = "found"
        elif not page:
            r["online"] = "fetch failed: " + err
        elif len(served) < 20 and m and int(m.group(1)) == r["page"]:
            r["online"] = "the web reader shows this page (same page number) without its text"
        elif len(norm(r["excerpt"])) > 80 and norm(r["excerpt"])[:80] in served:
            r["online"] = "the excerpt begins on the web page, which the web reader cuts short"
        else:
            r["online"] = "not found"
        bad += not ok
        time.sleep(0.5)
    return bad


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--online", action="store_true")
    ap.add_argument("--hf", type=Path, help="a quran-tajweed-phonetics folder: write its rule_citations.jsonl "
                                             "and citation_editions.jsonl for the rulings of its rulings.jsonl")
    a = ap.parse_args()
    rows = [{k: r.get(k) for k in FIELDS} for r in run()]
    if a.hf:
        ids = {json.loads(l)["rule_id"] for l in (a.hf / "rulings.jsonl").read_text(encoding="utf-8").splitlines() if l.strip()}
        mine = [r for r in rows if r["rule_id"] in ids]
        used = {r["shamela_book"] for r in mine if r.get("shamela_book")}
        snap = json.loads((SH / "_meta" / "extraction_manifest.json").read_text(encoding="utf-8"))["snapshot_id"]
        with (a.hf / "rule_citations.jsonl").open("w", encoding="utf-8", newline="\n") as f:
            for r in mine:
                f.write(json.dumps({k: v for k, v in r.items() if v is not None}, ensure_ascii=False) + "\n")
        with (a.hf / "citation_editions.jsonl").open("w", encoding="utf-8", newline="\n") as f:
            for e in editions_rows():
                if e["shamela_book"] in used:
                    f.write(json.dumps({**e, "corpus_snapshot": snap}, ensure_ascii=False) + "\n")
        print(f"{a.hf}: {len(mine)} rows for {len(ids)} rulings, {len(used)} editions")
        return
    OUT.mkdir(parents=True, exist_ok=True)
    with (OUT / "rule_citations.jsonl").open("w", encoding="utf-8", newline="\n") as f:
        for r in rows:
            f.write(json.dumps({k: v for k, v in r.items() if v is not None}, ensure_ascii=False) + "\n")
    snap = json.loads((SH / "_meta" / "extraction_manifest.json").read_text(encoding="utf-8"))["snapshot_id"]
    used = {r["shamela_book"] for r in rows if r.get("shamela_book")}
    with (OUT / "editions.jsonl").open("w", encoding="utf-8", newline="\n") as f:
        for e in editions_rows():
            if e["shamela_book"] in used:
                f.write(json.dumps({**e, "corpus_snapshot": snap}, ensure_ascii=False) + "\n")
    (ROOT / "docs" / "CITATION-PAGES.md").write_text(markdown(rows), encoding="utf-8", newline="\n")
    tally = {}
    for r in rows:
        tally[r["status"]] = tally.get(r["status"], 0) + 1
    print(f"{len(rows)} citation parts:", ", ".join(f"{v} {k}" for k, v in sorted(tally.items())))
    if a.online:
        bad = online_check(rows)
        n = sum(1 for r in rows if r.get("url"))
        with (OUT / "online_check.jsonl").open("w", encoding="utf-8", newline="\n") as f:
            for r in rows:
                if r.get("online"):
                    f.write(json.dumps({"rule_id": r["rule_id"], "n": r["n"], "url": r["url"],
                                        "online": r["online"]}, ensure_ascii=False) + "\n")
        print(f"online: {n - bad} of {n} excerpts found at their URL")
        for k in sorted({r["online"] for r in rows if r.get("online")} - {"found"}):
            print(f"  {sum(1 for r in rows if r.get('online') == k)}: {k}")


if __name__ == "__main__":
    main()
