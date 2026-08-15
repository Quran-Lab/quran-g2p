"""Grapheme clustering: text -> typed Cluster stream.

Purely orthographic: each non-mark character opens a cluster and absorbs the
run of mark characters after it. No tajweed knowledge lives here.

Mark membership is an EXPLICIT project decision (SPEC-002), not Unicode
category: the small waw/yaa (U+06E5/06E6) are category Lm but phonologically
extend the preceding letter, so they are marks here. Pause marks (U+06D6-06DB)
are combining and attach to the preceding cluster; the P1 decoder deletes them
with a reason code.

Stack validation here is the minimal orthographic layer: duplicate identical
marks are illegal, and the vowel slot (harakat / tanween forms / sukun forms)
admits at most one occupant per cluster. Anything the corpus proves legal that
this rejects is a spec bug to fix WITH a documented finding — fail-closed
discovery, not silent tolerance.
"""
from __future__ import annotations

from dataclasses import dataclass

from . import codepoints as cp


class IllegalStackError(Exception):
    """Orthographically impossible mark stack (or mark with no base)."""


#: Characters that attach to the preceding base character.
#: TATWEEL is here deliberately: it is a transparent extender whose riding
#: marks belong to the preceding letter (KFGQPC كـَلَّا writes the kaf's fatha
#: on the kasheeda; Tanzil rides dagger alifs and the 21:88 small noon on it).
MARKS = frozenset({
    cp.TATWEEL,
    cp.FATHATAN, cp.DAMMATAN, cp.KASRATAN,
    cp.FATHA, cp.DAMMA, cp.KASRA,
    cp.SHADDA, cp.SUKUN,
    cp.MADDAH_ABOVE, cp.HAMZA_ABOVE, cp.HAMZA_BELOW,
    cp.SUBSCRIPT_ALEF, cp.INVERTED_DAMMA, cp.FATHA_WITH_TWO_DOTS,
    cp.SUPERSCRIPT_ALEF,
    cp.SMALL_HIGH_LIGATURE_SAD_WITH_LAM_WITH_ALEF_MAKSURA,
    cp.SMALL_HIGH_LIGATURE_QAF_WITH_LAM_WITH_ALEF_MAKSURA,
    cp.SMALL_HIGH_MEEM_INITIAL_FORM,
    cp.SMALL_HIGH_JEEM, cp.SMALL_HIGH_THREE_DOTS,
    cp.SMALL_HIGH_SEEN, cp.SMALL_LOW_SEEN,
    cp.SMALL_HIGH_ROUNDED_ZERO, cp.SMALL_HIGH_UPRIGHT_RECTANGULAR_ZERO,
    cp.SMALL_HIGH_DOTLESS_HEAD_OF_KHAH,
    cp.SMALL_HIGH_MEEM_ISOLATED_FORM, cp.SMALL_LOW_MEEM,
    cp.SMALL_HIGH_MADDA,
    cp.SMALL_WAW, cp.SMALL_YEH, cp.SMALL_HIGH_YEH, cp.SMALL_HIGH_NOON,
    cp.EMPTY_CENTRE_LOW_STOP, cp.EMPTY_CENTRE_HIGH_STOP,
    cp.ROUNDED_HIGH_STOP_WITH_FILLED_CENTRE,
})

#: At most one of these per SEGMENT (the vowel/sukun slot).
VOWEL_SLOT = frozenset({
    cp.FATHATAN, cp.DAMMATAN, cp.KASRATAN,
    cp.FATHA, cp.DAMMA, cp.KASRA,
    cp.SUKUN, cp.SMALL_HIGH_DOTLESS_HEAD_OF_KHAH,
    cp.INVERTED_DAMMA, cp.FATHA_WITH_TWO_DOTS, cp.SUBSCRIPT_ALEF,
})

#: Marks that are phonological SEGMENTS in their own right and may carry their
#: own vowel-slot mark. Discovered from the corpus, sites recorded in SPEC-002:
#: small yeh with own fatha at 27:36 (both editions); floating combining hamza
#: with own sukun in Tanzil 2:72. Small waw/noon and hamza-below included by
#: the same principle.
SEGMENT_CARRIERS = frozenset({
    cp.HAMZA_ABOVE, cp.HAMZA_BELOW,
    cp.SMALL_WAW, cp.SMALL_YEH, cp.SMALL_HIGH_YEH, cp.SMALL_HIGH_NOON,
})


@dataclass(frozen=True)
class Cluster:
    base: str
    marks: tuple[str, ...]
    span: tuple[int, int]


def cluster(text: str) -> list[Cluster]:
    out: list[Cluster] = []
    i = 0
    n = len(text)
    while i < n:
        ch = text[i]
        if ch in MARKS:
            raise IllegalStackError(f"mark U+{ord(ch):04X} at {i} has no base")
        j = i + 1
        marks: list[str] = []
        while j < n and text[j] in MARKS:
            marks.append(text[j])
            j += 1
        _validate(ch, marks, i)
        out.append(Cluster(ch, tuple(marks), (i, j)))
        i = j
    return out


def uncluster(clusters: list[Cluster]) -> str:
    return "".join(c.base + "".join(c.marks) for c in clusters)


def _validate(base: str, marks: list[str], pos: int) -> None:
    # Both checks are per-segment: a segment-carrier mark (floating hamza,
    # small waw/yeh/noon) opens a fresh segment with its own vowel slot.
    seen: set[str] = set()
    vowel_slot_count = 0
    for m in marks:
        if m in SEGMENT_CARRIERS:
            seen = set()
            vowel_slot_count = 0
        if m in seen:
            raise IllegalStackError(
                f"duplicate mark U+{ord(m):04X} on base U+{ord(base):04X} at {pos}"
            )
        seen.add(m)
        if m in VOWEL_SLOT:
            vowel_slot_count += 1
            if vowel_slot_count > 1:
                raise IllegalStackError(
                    f"multiple vowel-slot marks on base U+{ord(base):04X} at {pos}"
                )
