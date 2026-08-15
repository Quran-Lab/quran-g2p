# SPEC-180..191 — المدود / Madd Classification

Status: normative. Rules: R180 (tabee'i incl. badal/'iwad {2}), R184 (silah
kubra), R185 (muttasil + muttasil-waqf), R186 (munfasil), R187/R188 (lazim
kalimi/harfi + 'ayn), R189 (aared), R190 (leen), R191 (precedence). Phase 10.

## Classical basis
Tuhfat al-Atfal باب المد: «وَالْمَدُّ أَصْلِيٌّ وَفَرْعِيٌّ لَهُ…»; muttasil
wajib «فَوَاجِبٌ إِنْ جَاءَ هَمْزٌ بَعْدَ مَدْ / فِي كِلْمَةٍ»; munfasil ja'iz
«وَجَائِزٌ مَدٌّ وَقَصْرٌ إِنْ فُصِلْ»; aared «وَمِثْلُ ذَا إِنْ عَرَضَ
السُّكُونُ / وَقْفًا»; badal; lazim «وَلَازِمٌ إِنِ السُّكُونُ أُصِّلَا /
وَصْلًا وَوَقْفًا»; the harfi subtypes and حَيٌّ طَهُرَ two-count letter
names. Hafs 'an 'Asim via Shatibiyyah: muttasil/munfasil 4–5 (تُقصر لا),
lazim 6, aared 2/4/6, 'ayn 4/6.

## Prescription model (SPEC-003)
Every madd carries LengthSpec(kind, allowed, canonical, scoring):
| class | kind | allowed | canonical (config) | scoring |
|---|---|---|---|---|
| tabee'i / badal / 'iwad / silah sughra | fixed | {2} | 2 | {2} |
| muttasil (wasl) | free | {4,5} | madd_muttasil_len | {4,5,6} |
| muttasil (waqf on the hamza) | free | {4,5,6} | madd_muttasil_waqf_len | {4,5,6} |
| munfasil + silah kubra | free | {4,5} | madd_munfasil_len | {2,3,4,5,6} |
| lazim (all subtypes) | fixed | {6} | 6 | {6} |
| aared | free | {2,4,6} | madd_aared_len | {2,3,4,5,6} |
| leen (at waqf) | free | {2,4,6} | min(leen,aared) | {2,3,4,5,6} |
| 'ayn (19:1, 42:2) | free | {4,6} | 4 (CONVENTION: tawassut muqaddam) | {4,5,6} |

`allowed` = Shatibiyyah-legal; `scoring` = attested labeling superset (the
free-choice munfasil/aared sets include the sub-canonical values real
reciters produce — labels describe observation; grading vs `allowed` is a
separate judgment). `realized_len` stays None until forced alignment.

## Detection (typed IR, post-P6/P8)
- next = HAMZA: same word -> muttasil; hamza segment-final with 'arid sukun ->
  muttasil-waqf (R191 strongest-cause: also aared by position; muttasil wins,
  both retained in provenance); cross-word -> munfasil (silah source -> R184).
  Fused ha-tanbih/ya-nida (هَٰٓؤُلَآءِ, يَٰٓأَيُّهَا) classify muttasil by the
  same-word test — identical Shatibiyyah lengths; tagged CONVENTION.
- next geminated -> lazim muthaqqal.
- next sakin: 'ARID (P4 iskan/taa-marbuta provenance) & final -> aared;
  ASLI -> lazim (mukhaffaf آلْآنَ 10:51,91 and every letter-name junction —
  the R011 spell-out makes lazim harfi fall out of the same test).
- otherwise tabee'i.
- Leen: consonant waw/yeh, sakin, after fatha, before the final sakin —
  'arid -> R190; asli (the 'ayn name) -> {4,6}.

## Witness accounting (stats gate)
Every U+0653 madda (5,376) must land in {muttasil, munfasil, lazim, silah
kubra}; the current residue (59 tabee'i-classified + 15 unconsumed) is an
OPEN stats-gate item to triage (candidates: deleted/silent seats, spell-out
spans, junction shortenings).

## Golden tests
tests/test_madd.py — aared (1:1), lazim muthaqqal (1:7), muttasil (2:19),
munfasil with scoring sets (2:4), lazim asli letter-name (2:1), leen (106:4).
