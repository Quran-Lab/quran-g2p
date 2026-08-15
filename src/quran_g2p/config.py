"""HafsConfig: the khilaf knobs, frozen, Shatibiyyah-defaulted (SPEC-012).

Every field models a transmitted choice WITHIN Hafs 'an 'Asim min tariq
al-Shatibiyyah. Defaults follow the mashhur reading as printed in the Madinah
mushaf; citations live in the spec files of the rules that consume each knob.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Literal


@dataclass(frozen=True)
class HafsConfig:
    riwaya: Literal["hafs_shatibiyyah"] = "hafs_shatibiyyah"

    # --- seen/sad khilaf words (R012; SPEC-012) -------------------------
    # 2:245 يَبْصُۜطُ: recited with SEEN (mashhur for Hafs/Shatibiyyah).
    bast_2_245_seen: bool = True
    # 7:69 بَصْۜطَةً: recited with SEEN (same basis).
    basta_7_69_seen: bool = True
    # 52:37 ٱلْمُصَۣيْطِرُونَ: wajhan for Hafs/Shatibiyyah, SAD muqaddam
    # (al-Taysir 203; al-Nashr 2:377; Hidayat al-Qari 2:579).
    musaytirun_52_37_seen: bool = False
    # 88:22 بِمُصَيْطِرٍ: SAD single wajh from the Shatibiyyah («وقطع
    # بالصاد في بمصيطر» — al-Nashr via al-Nuwayri 1:310; Lataif 9:266);
    # flipping this knob leaves the tariq.
    musaytir_88_22_seen: bool = False
    # 30:54 ضَعْف ×3: wajhan for Hafs — FATH (the riwaya from 'Asim,
    # muqaddam from the Shatibiyyah) / DAMM (Hafs' own ikhtiyar) —
    # الشاطبية بيت 722-723; التيسير 174-176 «وبالوجهين آخذ»; سراج القارئ
    # 1:235.
    daaf_30_54_damm: bool = False
    # The six istifham+wasl sites (ءَآلذَّكَرَيْنِ 6:143-144، ءَآلْآنَ
    # 10:51/91، ءَآللَّهُ 10:59/27:59): default = IBDAL (pure alif, lazim 6)
    # — muqaddam «فللكل ذا أولى» (الشاطبية 192-194؛ سراج القارئ 1:66-67؛
    # الوافي 1:87؛ النشر 1:377-378). True = TASHEEL bayna-bayna, NO madd
    # and no separating alif (the musahhala is in the weight of a voweled
    # hamza — فتح الوصيد 1:350).
    istifham_tasheel: bool = False

    # --- waqf-ra khilaf words live in v1 (R211; SPEC-210) ---------------
    # SOURCED 2026-08-15 (Hidayat al-Qari 1:133): of the eleven two-wajh
    # waqf raa'at, TEN take tarqeeq muqaddam (القطر، ونذر ×6، يسر،
    # أسر/فأسر) and ONE tafkheem (مصر).
    # وَنُذُرِ (54:16,18,21,30,37,39 ayah-final): TARQEEQ muqaddam — the
    # deleted yaa of نُذُرِي (Hidayat al-Qari 1:132; al-Nashr 2:110).
    nudhur_waqf_tafkheem: bool = False
    # يَسْرِ (89:4 ayah-final): tarqeeq awlaa (al-Nashr 2:110-111).
    yasr_waqf_tafkheem: bool = False
    # فِرْقٍ (26:63) WASL: wajhan jayyidan (al-Dani via Fath al-Wasid 1:526,
    # Siraj al-Qari 1:120); tarqeeq = the later tarjih «المأخوذ به المعول
    # عليه». Generalizes to the weakened MAKSUR isti'la after sakin reh.
    firq_wasl_tafkheem: bool = False
    # P2-full waqf words (unused until mid-ayah stops land): al-Nashr 2:105
    # «وأختار في مصر التفخيم وفي القطر الترقيق نظرًا للوصل وعملًا بالأصل»;
    # أسر/فأسر ×5: tarqeeq muqaddam (kasrat al-binaa, al-Nashr 2:110).
    misr_waqf_tafkheem: bool = True
    qitr_waqf_tafkheem: bool = False
    asr_waqf_tafkheem: bool = False
    # 76:4 سَلَٰسِلَا۟ waqf: wajhan from the Shatibiyyah; the printed
    # round-zero dabt selects HADHF (default); ithbat = the other wajh
    # (النويري 2:603؛ العميد 1:160-161؛ هداية القاري 2:526).
    salasila_waqf_alif: bool = False
    # 27:36 ءَاتَىٰنِۦَ waqf: wajhan; ITHBAT of the sakin yaa muqaddam
    # (هداية القاري 2:544-545؛ الوجيز 1:55-56). False = hadhf wajh.
    aataani_waqf_yaa: bool = True

    # --- madd lengths (P10; SPEC-18x) -----------------------------------
    # Canonical emission choices; allowed/scoring sets live in the rules.
    madd_munfasil_len: int = 4      # {4,5} allowed (Shatibiyyah)
    madd_muttasil_len: int = 4      # {4,5} allowed in wasl
    madd_muttasil_waqf_len: int = 4  # {4,5,6} at waqf on the hamza
    madd_aared_len: int = 4         # {2,4,6}
    madd_leen_len: int = 2          # {2,4,6}, leen <= aared (qasr mashhur)
    # 'ayn of كهيعص/حمعسق: Shatibiyyah wajhan {4,6}, ISHBA' 6 muqaddam
    # (الشاطبية بيت 177 «والطول فضلا»; هداية القاري 1:343). Qasr = Tayyibah only.
    madd_ain_len: int = 6

    def __post_init__(self) -> None:
        checks = [
            ("madd_munfasil_len", {4, 5}),
            ("madd_muttasil_len", {4, 5}),
            ("madd_muttasil_waqf_len", {4, 5, 6}),
            ("madd_aared_len", {2, 4, 6}),
            ("madd_leen_len", {2, 4, 6}),
            ("madd_ain_len", {4, 6}),
        ]
        for name, allowed in checks:
            v = getattr(self, name)
            if v not in allowed:
                raise ValueError(f"{name}={v} not in Shatibiyyah-legal {sorted(allowed)}")
        if self.madd_leen_len > self.madd_aared_len:
            raise ValueError("leen length may not exceed aared length")
