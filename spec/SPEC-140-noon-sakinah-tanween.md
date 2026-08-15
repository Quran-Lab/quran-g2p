# SPEC-140..144 — أحكام النون الساكنة والتنوين / Noon Sakinah & Tanween

Status: normative. Rules: R140_IZHAR(_HALQI), R141_IDGHAM_GHUNNA(+naqis, izhar
mutlaq), R142_IDGHAM_BILA_GHUNNA, R143_IQLAB, R144_IKHFA. Phase 6.

## Classical basis
Tuhfat al-Atfal (الجمزوري), باب النون الساكنة والتنوين:
«لِلنُّونِ إِنْ تَسْكُنْ وَلِلتَّنْوِينِ … أَرْبَعُ أَحْكَامٍ فَخُذْ تَبْيِينِي»
— izhar before the six throat letters «هَمْزٌ فَهَاءٌ ثُمَّ عَيْنٌ حَاءُ /
مُهْمَلَتَانِ ثُمَّ غَيْنٌ خَاءُ»; idgham in يرملون with ghunna in ينمو and
without in ل ر; iqlab at ب «وَالثَّالِثُ الإِقْلابُ عِنْدَ البَاءِ / مِيمًا
بِغُنَّةٍ مَعَ الإِخْفَاءِ»; ikhfa at the remaining fifteen. Al-Jazariyyah,
باب أحكام النون الساكنة والتنوين, concurs. Izhar mutlaq for same-word
noon+waw/yaa: الدنيا، بنيان، صنوان، قنوان (Tuhfa: «إِلَّا إِذَا كَانَا بِكِلْمَةٍ
فَلَا تُدْغِمْ»).

## Trigger (typed IR)
A sakin NOON phone (explicit noon sakinah or the tanween's noon, which
emission materializes as vowel-phone + noon-phone) whose following consonant
phone decides the branch.

## Dabt gate (SPEC-002; this engine's addition)
The mushaf's pointing already carries the verdict and is asserted, not merely
consumed: MARKED sukun on the noon = izhar witness (halqi neighbours, the
sakt-blocked sites, the يس/ن letter-name junctions) — such a noon is NEVER
assimilated. BARE noon and tanween noons take the 4-way branch. KFGQPC's
open/closed/iqlab tanween forms are asserted corpus-wide by
`tests/test_dabt_agreement.py` (pausal position exempt: witnesses describe
wasl into the following ayah).

## Transformations
| branch | condition | IR delta |
|---|---|---|
| izhar | next ∈ {ء ه ع ح غ خ} or MARKED sukun | ghunna="asl", phone kept |
| idgham bi-ghunna kamil | next ∈ {ن م} cross-word | noon deleted; target (dabt-geminated) carries ghunna via P9 |
| idgham bi-ghunna naqis | next ∈ {ي و} cross-word | noon deleted; target gets ghunna="idgham", no gemination requirement |
| izhar mutlaq | next ∈ {ي و} same word | ghunna="asl" (the four words) |
| idgham bila ghunna | next ∈ {ل ر} cross-word | noon deleted |
| iqlab | next = ب | base -> MEEM_MUKHFAH, ghunna="ikhfa"; witness = small meem mark (Tanzil 06E2/06ED; KFGQPC haraka+06E2), canonicalized in decode |
| ikhfa | remaining 15 | base -> NOON_MUKHFAH, ghunna="ikhfa"; tafkheem follows the trigger letter (R214) |

## Interactions
Sakt blocks assimilation (75:27 مَنْ رَاقٍ) — structurally enforced twice:
the rasm marks the noon's sukun (izhar witness) and R132 sets `sakt_after`.
Iltiqa' al-sakinayn converts a tanween noon before hamzat-wasl into noon
al-wiqaya with kasra (R131, SPEC-131) before this phase sees it.

## Sites & counts (corpus, Tanzil edition)
Tanween total 8,893 (census 064B/C/D). Iqlab witnesses: 06E2 ×510 + 06ED ×99.
Exact per-branch counts tracked by the stats gate.

## Golden tests
tests/test_noon_rules.py — 1:7 (izhar), 2:8 (naqis+ghunna), 2:10 (iqlab),
107:4 (kamil into lam), 107:5 (ikhfa), 2:180 (noon wiqaya). Corpus-level:
tests/test_dabt_agreement.py.

## Differential notes
reference engine: ikhfa carriers ں/۾ repeated (length convention parametrized in
oracle/expand.py); words merge across assimilation junctions.
