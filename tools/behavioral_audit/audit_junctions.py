"""Sweep C: concat every consecutive ayah pair and assert the junction
behavior the raw boundary letters demand (expectations derived from the
text + classical letter sets, independently of the engine's own rules)."""
import re
import sys
import unicodedata
from collections import Counter

from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))
from quran_g2p.concat import phonemize_concat
from quran_g2p.phonemize import phonemize
from quran_g2p.ir import Base
from quran_g2p.textbank import AyahRef, TextBank

TB = TextBank.load("tanzil")

TANWEEN = "\u064b\u064c\u064d"
IQLAB_MARK = "\u06e2"
SUKUN = "\u06e1\u0652"
HALQ = set("ءهعحغخأإئؤ")
YARMULUN_GH = set("يومن")
LAMREH = set("لر")

BASE_OF = {"ء": Base.HAMZA}


def last_bare(word):
    # final base letter + its trailing marks
    for i in range(len(word) - 1, -1, -1):
        if not unicodedata.combining(word[i]) and word[i] not in "ـۤۥۦٰ":
            return word[i], word[i + 1:]
    return "", ""


def first_base(word):
    for i, c in enumerate(word):
        if c == "\u0671":  # hamzat wasl: elided in junction; article next
            continue
        if not unicodedata.combining(c) and c != "ـ":
            return c
    return ""


def bases(ph):
    return [p.base for p in ph]


viol = Counter()
ex = {}
count = Counter()
EXC_IZHAR_MUTLAQ = {(36, 1), (68, 1)}
SKIP = {(8, 75), (18, 1), (36, 52), (69, 28), (3, 1)}  # site-handled, golden'd

pairs = 0
cur = None
prev_ref = None
for ref in TB.refs():
    if prev_ref is not None and ref.surah == prev_ref.surah \
            and ref.ayah == prev_ref.ayah + 1:
        if prev_ref.ayah == 0 or (prev_ref.surah, prev_ref.ayah) in SKIP:
            prev_ref = ref
            continue
        t1, t2 = TB.ayah(prev_ref), TB.ayah(ref)
        n1 = max(p.word_index for p in phonemize(t1, edition="tanzil", ref=prev_ref).segments[0].phones) + 1
        try:
            res = phonemize_concat([(prev_ref, t1), (ref, t2)],
                                   edition="tanzil")
        except Exception as e:
            viol["concat-raises"] += 1
            ex.setdefault("concat-raises", f"{prev_ref} {e}")
            prev_ref = ref
            continue
        ph = res.segments[0].phones
        pairs += 1
        lb, tail = last_bare(t1.split(" ")[-1])
        fb = first_base(t2.split(" ")[0])
        tail_ph = [p for p in ph if p.word_index == n1 - 1]
        head_ph = [p for p in ph if p.word_index == n1]
        if not tail_ph or not head_ph:
            flag_base = None
        tail_last = tail_ph[-1] if tail_ph else None
        head_cons = next((p for p in head_ph if p.kind != "vowel"), None)

        def flag(k):
            viol[k] += 1
            ex.setdefault(k, f"{prev_ref}->{ref}")

        noon_end = (lb == "ن" and any(c in SUKUN for c in tail))             or any(c in TANWEEN for c in tail) or IQLAB_MARK in tail
        wasl_next = t2.split(" ")[0].startswith("ٱ")
        if noon_end and fb and tail_last is not None:
            if wasl_next:
                count["wiqaya"] += 1
                noon_kasra = any(p.base is Base.NOON for p in tail_ph[-3:])                     and tail_last.base in (Base.KASRA, Base.NOON)
                if not noon_kasra:
                    flag("wiqaya-pattern-missing")
            elif fb == "ب":
                count["iqlab"] += 1
                if not any(p.base is Base.MEEM_MUKHFAH for p in tail_ph[-2:]):
                    flag("iqlab-missing-meem-mukhfah")
            elif fb in HALQ:
                count["izhar"] += 1
                if not any(p.base is Base.NOON for p in tail_ph[-2:]):
                    flag("izhar-noon-missing")
            elif fb in LAMREH:
                count["bila-ghunna"] += 1
                if tail_ph[-1].base in (Base.NOON, Base.NOON_MUKHFAH):
                    flag("bilaghunna-noon-survives")
                if head_cons is None or not head_cons.geminated:
                    flag("bilaghunna-head-not-geminated")
            elif fb in YARMULUN_GH:
                if (prev_ref.surah, prev_ref.ayah) in EXC_IZHAR_MUTLAQ:
                    count["izhar-mutlaq-junction"] += 1
                    if not any(p.base is Base.NOON for p in tail_ph[-2:]):
                        flag("mutlaq-noon-missing")
                else:
                    count["bi-ghunna"] += 1
                    if tail_ph[-1].base is Base.NOON:
                        flag("bighunna-tail-noon-survives")
                    if fb in "نم":
                        if head_cons is None or not head_cons.geminated                                 or not head_cons.ghunna:
                            flag("bighunna-kamil-head-wrong")
                    else:
                        if head_cons is None or not head_cons.ghunna:
                            flag("bighunna-naqis-no-axis-ghunna")
            else:
                count["ikhfa"] += 1
                if not any(p.base is Base.NOON_MUKHFAH for p in tail_ph[-2:]):
                    flag("ikhfa-missing-mukhfah")
        meem_end = lb == "م" and any(c in SUKUN for c in tail)
        if meem_end and fb and tail_ph:
            if fb == "ب":
                count["ikhfa-shafawi"] += 1
                if not any((p.base is Base.MEEM_MUKHFAH) or
                           (p.base is Base.MEEM and p.ghunna)
                           for p in tail_ph[-2:]):
                    flag("shafawi-ikhfa-missing")
            elif fb == "م":
                count["idgham-mithlayn"] += 1
                if head_cons is None or not (head_cons.base is Base.MEEM
                                             and head_cons.geminated):
                    flag("mithlayn-not-geminated")
    prev_ref = ref

print(f"junction pairs checked: {pairs}")
print("class counts:", dict(count))
if viol:
    for k, n in viol.most_common():
        print(f"  VIOLATION {k}: {n}  e.g. {ex[k]}")
else:
    print("ALL JUNCTION INVARIANTS HOLD")
