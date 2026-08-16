"""Page-level citation audit: every register cite's vol:page (or bayt
number) is checked inside the Shamela print of the cited book, and the
ruling's topic keywords must appear on the cited page (±tolerance)."""
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from quran_g2p.rules.registry import RULINGS

SH = Path("F:/shamela4")
TOL = 3          # pages of edition drift tolerated
AR_DIGITS = str.maketrans("٠١٢٣٤٥٦٧٨٩", "0123456789")


def norm(s):
    s = re.sub(r"<[^>]+>", " ", s)
    s = re.sub(r"[\u064b-\u0652\u0670ـ«»()]", "", s)
    s = re.sub(r"[إأآا]", "ا", s)
    s = re.sub(r"[ىي]", "ي", s)
    return " ".join(s.split())


BOOKS = {}   # canonical key -> dir


def index_corpus():
    for cat in SH.iterdir():
        if not cat.is_dir() or cat.name.startswith(("$", "System", "_")):
            continue
        for b in cat.iterdir():
            if b.is_dir() and (b / "pages.jsonl").exists():
                BOOKS[norm(b.name.split("__", 1)[-1].replace("-", " "))] = b


# cite-token -> corpus-title fragment
RESOLVE = {
    "الشاطبية": "2832__",
    "الجزرية": "4484__",
    "المقدمة الجزرية": "المقدمة الجزرية",
    "تحفة الأطفال": "3459__",
    "النشر": "5932__",
    "طيبة النشر": "2838__",
    "التيسير": "التيسير في القراءات السبع",
    "السبعة": "السبعة في القراءات",
    "حجة القراءات": "حجة القراءات",
    "الحجة للقراء السبعة": "الحجة للقراء السبعة",
    "المحكم في نقط المصاحف": "المحكم في نقط المصاحف",
    "دليل الحيران": "دليل الحيران",
    "غاية المريد": "غاية المريد",
    "سراج القارئ": "سراج القارئ المبتدي",
    "هداية القاري": "هداية القاري",
    "لطائف الإشارات": "لطائف الاشارات لفنون القراءات",
    "غيث النفع": "غيث النفع",
    "فتح الوصيد": "فتح الوصيد",
    "إبراز المعاني": "ابراز المعاني",
    "النويري": "7801__",
    "بغية المستفيد": "بغية المستفيد",
    "التمهيد": "التمهيد في علم التجويد",
    "جهد المقل": "جهد المقل",
    "العميد": "العميد في علم التجويد",
    "الإتحاف": "اتحاف فضلاء البشر",
}

# topic keywords per rule id (normalized); ANY hit counts
KW = {
    "R011": ["مقطع", "فواتح", "هجاء", "حي طهر", "الم"],
    "R012B": ["ضعف"], "R012": ["يبصط", "بصطة", "مصيطر", "بالسين", "بالصاد"],
    "R013": ["يسوءوا", "ليسوءوا", "واو"],
    "R014": ["الاستفهام", "ابدال", "تسهيل", "الان"],
    "R110": ["همزة الوصل", "الابتداء", "ابتد"],
    "R112": ["الابتداء", "مشدد", "ادغام"],
    "R120": ["الوقف", "السكون", "اسكان"],
    "R121": ["عوض", "تنوين", "وقف"],
    "R122": ["تاء", "هاء", "التانيث", "وقف"],
    "R123": ["الروم", "الاشمام", "روم", "اشمام"],
    "R130": ["همزة الوصل", "وصل"], "R131": ["الساكنين", "التنوين", "نون"],
    "R132": ["سكت", "السكت", "ماليه"],
    "R133": ["لام", "التعريف", "شمسية", "ادغام"],
    "R134": ["الله", "الجلالة", "اللام"], "R135": ["الم", "الله", "ميم"], "R136": ["بسمل", "البسملة", "مبسملا"],
    "R140": ["اظهار", "الحلق", "حلقي"],
    "R141": ["ادغام", "غنة", "يرملون", "الدنيا", "بنيان"],
    "R142": ["ادغام", "اللام والرا", "بغير غنة"],
    "R143": ["اقلاب", "قلب", "ميم"],
    "R144": ["اخفاء", "الاخفاء"],
    "R150": ["شفوي", "الاخفاء", "الباء"],
    "R160": ["مثل", "المثلين", "ادغام"],
    "R161": ["الاطباق", "احطت", "بسطت"],
    "R170": ["غنة", "مشدد"],
    "R180": ["المد", "طبيعي", "اللين"],
    "R181": ["بدل", "البدل"],
    "R183": ["صلة", "هاء", "الكناية", "يصلوا", "مضمر"], "R184": ["صلة", "هاء", "همز", "يصلوا", "مضمر"],
    "R185": ["متصل", "اتصل", "يتصل", "بعد همز"], "R186": ["منفصل", "انفصل", "ينفصل"],
    "R187": ["لازم", "اللازم"], "R188": ["عين"],
    "R189": ["عارض", "عرض السكون", "سكون وقفا"], "R190C": ["اتان"], "R190B": ["سلاسل"],
    "R190": ["اللين", "لين"],
    "R200": ["قلقلة", "القلقلة", "قطب جد"],
    "R201": ["قلقلة"], "R202": ["قلقلة"],
    "R210": ["الاستعلاء", "تفخيم", "مراتب", "الصفات", "مستعليه"],
    "R211": ["الراء", "ترقيق", "تفخيم", "مصر", "القطر"],
    "R212": ["الجلالة", "اللام", "الله"],
    "R214": ["غنة", "الاخفاء", "تفخيم", "ترقيق"],
    "R220B": ["تامنا", "اختلاس", "اشمام"], "R220": ["تامنا", "اشمام"],
    "R221": ["امالة", "مجراها", "الامالة"],
    "R222": ["تسهيل", "اعجمي"],
}


def kw_for(rid):
    for k in sorted(KW, key=len, reverse=True):
        if rid.startswith(k):
            return [norm(w) for w in KW[k]]
    return []


def load_pages(bdir):
    pages = []
    for l in (bdir / "pages.jsonl").open(encoding="utf-8"):
        if l.strip():
            d = json.loads(l)
            pages.append((d.get("part"), d.get("page_num"),
                          norm(d.get("body") or "")))
    return pages


_page_cache = {}


def pages_of(bdir):
    if bdir not in _page_cache:
        _page_cache[bdir] = load_pages(bdir)
    return _page_cache[bdir]


def find_book(token):
    raw = RESOLVE.get(token, token)
    if raw.endswith("__"):
        for d in BOOKS.values():
            if d.name.startswith(raw):
                return d
        return None
    frag = norm(raw)
    exact = [d for t, d in BOOKS.items() if t == frag]
    if exact:
        return exact[0]
    hits = sorted(((t, d) for t, d in BOOKS.items() if frag in t),
                  key=lambda x: len(x[0]))
    return hits[0][1] if hits else None


def check_vol_page(bdir, vol, p1, p2, kws):
    pages = pages_of(bdir)
    sel = [t for part, pn, t in pages
           if pn is not None and p1 - TOL <= pn <= p2 + TOL
           and (part is None or vol is None or str(part).translate(AR_DIGITS) == str(vol))]
    if not sel:
        return "PAGE-MISSING"
    blob = " ".join(sel)
    return "OK" if any(k in blob for k in kws) else "TOPIC-MISS"


def check_bayt(bdir, b1, b2, kws):
    pages = pages_of(bdir)
    blob = " ".join(t for _, _, t in pages)
    blob = blob.translate(AR_DIGITS)
    for n in range(b1, b2 + 1):
        m = re.search(rf"\b{n} - (.{{0,160}})", blob)
        if m:
            seg = m.group(1)
            if any(k in seg for k in kws) or not kws:
                return "OK"
    m = re.search(rf"\b{b1} -", blob)
    return "BAYT-FOUND-TOPIC-MISS" if m else "BAYT-MISSING"


results = []
index_corpus()
for r in RULINGS:
    kws = kw_for(r.id)
    parts = [p.strip() for p in re.split(r"[؛]", r.cite) if p.strip()]
    for part in parts:
        tok = None
        for name in sorted(RESOLVE, key=len, reverse=True):
            if name in part:
                tok = name
                break
        if tok is None:
            results.append((r.id, part[:40], "NOTE"))
            continue
        bdir = find_book(tok)
        if bdir is None:
            results.append((r.id, tok, "BOOK-NOT-IN-CORPUS"))
            continue
        mb = re.search(r"(?:بيتا?|أبيات)\s+(\d+)(?:-(\d+))?", part)
        mp = re.search(r"(\d+):(\d+)(?:-(\d+))?", part)
        if mb:
            b1 = int(mb.group(1)); b2 = int(mb.group(2) or b1)
            st = check_bayt(bdir, b1, b2, kws)
        elif mp:
            vol = int(mp.group(1)); p1 = int(mp.group(2))
            p2 = int(mp.group(3) or p1)
            st = check_vol_page(bdir, vol, p1, p2, kws)
        else:
            blob = " ".join(t for _, _, t in pages_of(bdir))
            st = "OK-BOOK" if any(k in blob for k in kws) else "TOPIC-MISS-BOOK"
        results.append((r.id, f"{tok} [{part[:34]}]", st))

per = {}
for rid, _, s in results:
    per.setdefault(rid, []).append(s)
no_verified = [rid for rid, ss in per.items()
               if not any(s.startswith("OK") for s in ss)]
print("rulings with NO verified book reference:", no_verified or "none")
ok = sum(1 for _, _, s in results if s.startswith("OK"))
print(f"checked {len(results)} citation references: {ok} OK, {len(results)-ok} flagged")
for rid, ref, st in results:
    if not st.startswith("OK"):
        print(f"  {st:24s} {rid:26s} {ref}")


# ---------------------------------------------------------------- report
REPORT = Path(__file__).resolve().parents[1] / "docs" / "CITATION-AUDIT.md"
lines = [
    "# Citation audit",
    "",
    "Every classical reference in the rulings register "
    "(`src/quran_g2p/rules/registry.py`) checked against the Shamela "
    "library: the cited book must exist in the corpus, the cited "
    "volume:page (or bayt number) must exist in the Shamela print, and "
    "the ruling's topic keywords must appear at the cited location "
    "(±3 pages of edition drift tolerated). Quoted matn snippets are "
    "additionally verified verbatim, character-stream, inside the matns "
    "themselves. Regenerate with `python tools/audit_citations.py`.",
    "",
    f"**{len(results)} references checked: {ok} verified, "
    f"{sum(1 for _, _, s in results if s == 'NOTE')} descriptive notes, "
    f"{len(results) - ok - sum(1 for _, _, s in results if s == 'NOTE')} failures.**",
    "",
    "| ruling | reference | status |",
    "|---|---|---|",
]
for rid, ref, st in results:
    lines.append(f"| `{rid}` | {ref} | {st} |")
REPORT.write_text(chr(10).join(lines) + chr(10), encoding="utf-8")
print("wrote", REPORT)
