"""Audit the review rows' Arabic labels against their own content.

The adjudication-#1 defect class: a row's human-facing label (rule_ar)
contradicting its own example, ayah, or expect block. The golden harness
verifies expect-vs-engine; nothing verified label-vs-row. This auditor
closes that gap with mechanical checks; the LLM coherence sweep
(scratchpad) adds a prose-level second net.

Checks
  P1  every quoted parenthetical part in rule_ar occurs in the row's
      ayah (rasm-skeleton match; commentary parts are filtered by
      vocabulary and the no-harakat rule; rows whose quotes are
      transformed forms - pausal, ibtida, spelled-out letters, family
      lists - are allowlisted with the reason)
  L1  idgham rows that name a swallowing letter agree with the expect
      block's bases
  L2  idgham kamil/naqis wording agrees with the expect block's
      geminated flag
  L3  qalqalah rows that name a letter have that letter in expect
"""
import re
import sys
from pathlib import Path

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from quran_g2p.textbank import AyahRef, TextBank

GOLDENS = Path(__file__).resolve().parents[1] / "tests" / "goldens"

LETTER_BASE = {
    "الهمزة": "hamza", "الباء": "beh", "التاء": "teh", "الثاء": "theh",
    "الجيم": "jeem", "الحاء": "hah", "الخاء": "khah", "الدال": "dal",
    "الذال": "thal", "الراء": "reh", "الزاي": "zain", "السين": "seen",
    "الشين": "sheen", "الصاد": "sad", "الضاد": "dad", "الطاء": "tah",
    "الظاء": "zah", "العين": "ain", "الغين": "ghain", "الفاء": "feh",
    "القاف": "qaf", "الكاف": "kaf", "اللام": "lam", "الميم": "meem",
    "النون": "noon", "الهاء": "heh", "الواو": "waw", "الياء": "yeh",
}

# rows whose label DOCUMENTS a second transmitted wajh whose behavior the
# expect deliberately does not assert (the muqaddam is asserted instead).
# Each entry carries the review provenance that authorized the wording.
SECOND_WAJH_DOC_OK = {
    "mutaqarib-qaf-kaf": "S1 supplementary answer (Shaikh Sami Almadani): "
                         "state the khilaf; kamil is the asserted muqaddam, "
                         "naqis documented per al-Nashr 1:221",
}

# rows whose parenthetical is legitimately NOT verbatim mushaf text
TRANSFORMED_OK = {
    "qlq-kubra-ahad": "pausal form after tanween drop",
    "sup2-ibtida-shadda": "ibtida form",
    "madd-harfi-laam": "spelled-out letter names",
    "madd-harfi-meem": "spelled-out letter names",
    "madd-harfi-kaf-19-1": "spelled-out letter names",
    "madd-harfi-sad-19-1": "spelled-out letter names",
    "madd-harfi-ha-two": "spelled-out letter names",
    "madd-ain-19-1": "spelled-out letter name",
    "muq-taha": "spelled-out letter names",
    "muq-yaseen-seen": "spelled-out letter names",
    "muq-hameem": "spelled-out letter names",
    "sup-alm-allah": "spelled-out letter names",
    "sup-naql-49-11": "naql ibtida form",
    "alif7-lakinna-wasl-drop": "wasl form of lakinna",
    "alif7-ana-wasl-drop": "wasl transform note",
    "sup-sakt-class": "multi-site list spans four ayat",
    "sup-haa-sakt-wasl": "family list spans ayat",
    "sup2-ittikhadh-izhar": "family list spans many ayat",
    "sup2-hadhf-ithbat": "family list spans many ayat",
    "ikhfa-jeem": "contrast note (najjaynakum vs anjaynakum)",
    "wasl-verb-unzur-damm": "ibtida form",
    "sup2-istifham-tasheel": "sister-sites list spans ayat",
    "sup2-lamat-sawakin": "multi-site statement row",
}

# vocabulary marking a parenthetical part as commentary, not a quote
_PROSE = ("المقدَّم", "المقدم", "وجه", "لحفص", "حفص", "رواية", "النشر",
          "الشاطبية", "رأس", "انفراد", "اختيار", "الأداء", "أخوات",
          "يسميه", "المفتاح", "الإطلاق", "تبع", "طور", "نحو", "حالان",
          "مقدار", "الموضع", "داخل", "حذف", "بعد", "عند", "وصل", "وقف",
          "لا ", "بل ", "الوجه", "الاستعلاء", "الأولى", "مفخمة",
          "الموقوف", "القصر", "الضم", "تصل", "علامة", "ضبط", "الجزرية", "الباب", "وأصل")

_MARKS = re.compile("[ً-ٰۖ-ۭـ]")
_HARAKA = re.compile("[ً-ْٰ]")


def skeleton(s: str) -> str:
    s = _MARKS.sub("", s)
    s = (s.replace("ٱ", "ا").replace("آ", "ا")
          .replace("أ", "ا").replace("إ", "ا")
          .replace("ى", "ي"))
    return "".join(s.split())


def parentheticals(label: str):
    return [p.strip() for p in re.findall(r"\(([^)]+)\)", label)]


def quote_parts(frag: str):
    """Split a parenthetical into candidate quoted parts; keep only the
    ones that look like vocalized mushaf text."""
    parts = re.split(r"[;:؛،—?؟]|\.\.\.|…", frag)
    out = []
    for p in parts:
        p = p.strip()
        if not p or not _HARAKA.search(p):
            continue
        if any(w in p for w in _PROSE):
            continue
        if re.search(r"[0-9]", p):
            continue
        if len(skeleton(p)) >= 3:
            out.append(p)
    return out


def check_rows(rows, tb):
    fails = []
    for r in rows:
        label = r.get("rule_ar", "")
        rid = r["id"]
        surah, ayah = r.get("surah"), r.get("ayah")
        expects = r.get("expect") or []
        bases = {e.get("base") for e in expects if isinstance(e, dict)}
        text = tb.ayah(AyahRef(surah, ayah)) if surah and ayah else ""
        sk_text = skeleton(text)

        if text and rid not in TRANSFORMED_OK:
            for frag in parentheticals(label):
                for part in quote_parts(frag):
                    if skeleton(part) not in sk_text:
                        fails.append((rid, "P1",
                                      f"'{part}' not in {surah}:{ayah}"))

        if label.startswith("إدغام") and expects:
            named = [b for name, b in LETTER_BASE.items()
                     if f"في {name}" in label]
            if named and not set(named) & bases:
                fails.append((rid, "L1",
                              f"label names {named}, expect {sorted(bases)}"))
            gem = {e.get("geminated") for e in expects
                   if isinstance(e, dict) and "geminated" in e}
            if "كامل" in label and True not in gem:
                fails.append((rid, "L2", "kamil label, no geminated:true"))
            if ("ناقص" in label and False not in gem
                    and rid not in SECOND_WAJH_DOC_OK):
                fails.append((rid, "L2", "naqis label, no geminated:false"))

        if label.startswith("قلقلة") and expects:
            named = [b for name, b in LETTER_BASE.items()
                     if f"لل{name[2:]}" in label or f" {name} " in label]
            if named and not set(named) & bases:
                fails.append((rid, "L3",
                              f"label names {named}, expect {sorted(bases)}"))
    return fails


def main() -> int:
    tb = TextBank.load("tanzil")
    rows = []
    for f in sorted(GOLDENS.glob("*.yaml")):
        rows += yaml.safe_load(f.read_text(encoding="utf-8"))
    fails = check_rows(rows, tb)
    print(f"rows audited: {len(rows)}")
    for rid, code, msg in fails:
        print(f"  FAIL {code} [{rid}] {msg}")
    if not fails:
        print("ALL LABEL CHECKS PASS")
    return 1 if fails else 0


if __name__ == "__main__":
    raise SystemExit(main())
