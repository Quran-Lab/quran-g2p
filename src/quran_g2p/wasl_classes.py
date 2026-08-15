"""Hamzat-wasl word classes (SPEC-110; sourced 2026-08-15).

Nouns with wajib KASRA at ibtida' — the seven Quranic of the ten sama'i
(al-Muqaddima al-Jazariyya 101-103; Hidayat al-Qari 2:488; al-Mizan 1:234;
است/ابنم/ايمن are not in the tanzil): matched by the post-wasla consonant
skeleton PREFIX so suffixed forms (اسْمُهُ, ابْنَتَيَّ, اثْنَتَا عَشْرَةَ)
resolve — load-bearing because e.g. اسْمُهُ has a damma third slot that the
verb rule would misread as damm.

Verbs whose third-slot damma is 'ARIDA (kasra at ibtida'): exactly FIVE in
the Quran (Hidayat al-Qari 2:482 «ليس في القرآن غير هذه الأفعال الخمسة»;
al-Rawda al-Nadiyya 126-127; Fath al-Aqfal 162): امشوا ابنوا اقضوا امضوا
ائتوا/ائتوني — the damma migrated from the elided yaa (اقضِيُوا -> اقضوا).

Ibtida' on ٱؤْـ/ٱئْـ (badal): the resolved wasl-hamza's vowel converts the
following sakin hamza into the matching madd letter (اؤتمن -> أُوتُمِن;
ائذن/ائتوني -> إِيذَن/إِيتُوني).
"""
from __future__ import annotations

from .ir import Base

B = Base

#: post-wasla consonant-skeleton PREFIXES of the seven Quranic wasl nouns.
NOUN_SKELETONS: tuple[tuple[Base, ...], ...] = (
    (B.SEEN, B.MEEM),                    # اسم + suffixes (باسم has no wasla start)
    (B.BEH, B.NOON),                     # ابن / ابنة / ابنت + suffixes
    (B.MEEM, B.REH, B.HAMZA),            # امرؤ / امرأ / امرئ / امرأة / امرأت
    (B.THEH, B.NOON),                    # اثنين / اثنتين / اثنا / اثنتا …
)

#: first-two radicals of the five 'arida-damma verbs (kasra at ibtida').
#: The decisive signature is the PLURAL WAW: the second radical must be
#: followed by a U-quality madd seg (اقضِيُوا -> اقضوا) — this is what
#: separates ائتوا (kasra) from ٱؤْتُمِنَ (asliyya damm, no waw).
ARIDA_DAMMA_RADICALS: tuple[tuple[Base, ...], ...] = (
    (B.MEEM, B.SHEEN),                   # امشوا
    (B.BEH, B.NOON),                     # ابنوا
    (B.QAF, B.DAD),                      # اقضوا
    (B.MEEM, B.DAD),                     # امضوا (never ibtida-able in tilawa:
                                         #   always preceded by waw — kept for
                                         #   completeness per the sources)
    (B.HAMZA, B.TEH),                    # ائتوا / ائتوني
)


def word_letters_after_wasla(segs, word: int) -> tuple[Base, ...]:
    from .ortho import ConsSeg
    letters = [s.letter for s in segs
               if isinstance(s, ConsSeg) and s.word_index == word]
    # drop the leading HAMZAT_WASL itself
    if letters and letters[0] is B.HAMZAT_WASL:
        letters = letters[1:]
    return tuple(letters)


def is_wasl_noun(letters: tuple[Base, ...]) -> bool:
    return any(letters[: len(sk)] == sk for sk in NOUN_SKELETONS)


def is_arida_damma_verb(segs, word: int) -> bool:
    from .ortho import ConsSeg, MaddSeg, VQ
    cons = []
    for i, s in enumerate(segs):
        if s.word_index != word:
            continue
        if isinstance(s, ConsSeg) and s.letter is not B.HAMZAT_WASL:
            cons.append((i, s.letter))
        if len(cons) == 2:
            break
    if len(cons) < 2:
        return False
    radicals = (cons[0][1], cons[1][1])
    if radicals not in ARIDA_DAMMA_RADICALS:
        return False
    j = cons[1][0] + 1
    return (j < len(segs) and isinstance(segs[j], MaddSeg)
            and segs[j].quality is VQ.U)
