"""Concat phase (SPEC-005): consecutive ayat phonemized in wasl.

Each ayah is DECODED with its own ref (site tables, dabt, muqatta'at),
then the seg streams are merged with char/word offsets and the phase
chain runs once over the whole breath group, so every junction rule
fires across ayah boundaries exactly as it does across words.

Three cross-ayah junctions carry transmitted specials the general rules
cannot know (register entries with sources):

- 3:1 -> 3:2  الٓمٓ + ٱللَّهُ: the meem's connective haraka is FATHA
  (not the iltiqa kasra) and the jalala keeps tafkheem; the meem-name's
  lazim madd keeps its length (السبعة 1:199؛ غيث النفع 1:129-130).
- 18:1 -> 18:2  عِوَجَا ۜ قَيِّمًا: the 'iwad alif stands EVEN IN WASL
  and carries the sakt; no tanween junction rules fire (الشاطبية
  830-831؛ النشر 1:240-241).
- 69:28 -> 69:29  مَالِيَهْ هَلَكَ: izhar WITH sakt muqaddam — the two
  haas do not idgham (النشر 2:21-22؛ هداية القاري 1:236-237).

Basmala policy is compositional: include (1,1) in the item list for
wasl-al-jamee' (join #3); make two calls for stop-then-join (join #2).
NEVER compose the forbidden fourth join (previous surah's end joined to
the basmala with a stop on the basmala: الشاطبية بيت 107).
"""
from __future__ import annotations

from dataclasses import replace as _replace
from types import SimpleNamespace

from .config import HafsConfig
from .ir import Base, LengthSpec, Phone, RuleApp
from .pipeline import run
from .textbank import AyahRef

_IWAD = LengthSpec(kind="fixed", allowed=frozenset({2}), canonical=2,
                   scoring=frozenset({2}))


def phonemize_concat(items: list[tuple[AyahRef, str]], edition: str,
                     config: HafsConfig | None = None):
    from .phonemize import PhonemizeResult, Segment, _run_phases
    config = config or HafsConfig()

    # R136_BASMALA_JOINS: a breath group that joins anything to the basmala
    # and then STOPS on it composes the forbidden fourth wajh — وصل البسملة
    # بآخر السورة والوقف عليها (الشاطبية بيت 107 «ومهما تصلها مع أواخر
    # سورة فلا تقفن الدهر فيها»; هداية القاري الباب الثامن عشر). The three
    # legal joins compose as documented in the module docstring.
    rule_id = "R136_BASMALA_JOINS"
    if len(items) >= 2 and items[-1][0] == AyahRef(1, 1):
        raise ValueError(
            f"{rule_id}: a group must not END on the basmala after "
            "joining it to a preceding item (the forbidden fourth wajh, "
            "al-Shatibiyyah bayt 107); stop before the basmala (two "
            "calls) or include the next surah's opening in the group")

    merged_segs = []
    merged_clusters = []
    trace: list[RuleApp] = []
    word_offsets: dict[tuple[int, int], int] = {}
    boundaries: list[int] = []  # word offset of each item
    char_off = 0
    word_off = 0
    refs = []
    for ref, text in items:
        ctx = run(text, edition=edition, ref=ref, config=config)
        refs.append(ref)
        word_offsets[(ref.surah, ref.ayah)] = word_off
        boundaries.append(word_off)
        for c in ctx.clusters:
            merged_clusters.append(_replace(
                c, span=(c.span[0] + char_off, c.span[1] + char_off)))
        n_words = 0
        for seg in ctx.segs:
            n_words = max(n_words, seg.word_index + 1)
            merged_segs.append(_replace(
                seg,
                span=(seg.span[0] + char_off, seg.span[1] + char_off),
                word_index=seg.word_index + word_off))
        trace.extend(ctx.trace)
        char_off += len(text) + 1
        word_off += n_words

    mctx = SimpleNamespace(clusters=merged_clusters, config=config,
                           segs=merged_segs, word_offsets=word_offsets)
    phones = _run_phases(merged_segs, trace, config, tuple(refs), mctx)
    phones = _junction_specials(phones, trace, refs, word_offsets)
    return PhonemizeResult(segments=[Segment(phones, "ayah_end")],
                           trace=trace)


def _adjacent(refs, a, b):
    for i in range(len(refs) - 1):
        if (refs[i].surah, refs[i].ayah) == a and \
                (refs[i + 1].surah, refs[i + 1].ayah) == b:
            return True
    return False


def _junction_specials(phones, trace, refs, word_offsets):
    out = list(phones)

    # الٓمٓ + ٱللَّهُ: the iltiqa gave the meem a KASRA and the jalala
    # went muraqqaq after it; the transmitted junction is FATHA with the
    # jalala mofakham (the meem-name's lazim madd is untouched upstream).
    if _adjacent(refs, (3, 1), (3, 2)):
        for i in range(len(out) - 2):
            if (out[i].base is Base.YEH_MADD and out[i + 1].base is Base.MEEM
                    and out[i + 2].base is Base.LAM and out[i + 2].geminated):
                app = RuleApp("R135_MEEM_ALLAH", "SPEC-011",
                              out[i + 1].src_span)
                trace.append(app)
                out.insert(i + 2, Phone(base=Base.FATHA, kind="vowel",
                                        geminated=False, length=None,
                                        ghunna=None, qalqalah=None,
                                        tafkheem="moraqaq", sakt_after=False,
                                        pausal_role=None, provenance=(app,),
                                        src_span=out[i + 1].src_span,
                                        word_index=out[i + 1].word_index))
                j = i + 3
                while j < len(out) and out[j].word_index == out[i + 3].word_index:
                    if out[j].base in (Base.LAM, Base.FATHA, Base.ALEF_MADD):
                        out[j] = _replace(out[j], tafkheem="mofakham",
                                          provenance=out[j].provenance + (app,))
                        j += 1
                    else:
                        break
                break

    # مَالِيَهْ هَلَكَ: R160 idghamed the two haas; the muqaddam is izhar
    # with a sakt on the first haa.
    if _adjacent(refs, (69, 28), (69, 29)):
        w2 = word_offsets[(69, 29)]
        for i, p in enumerate(out):
            if (p.base is Base.HEH and p.geminated
                    and p.word_index == w2):
                app = RuleApp("R132_MALIYAH_SAKT", "SPEC-132", p.src_span)
                trace.append(app)
                first = Phone(base=Base.HEH, kind="consonant",
                              geminated=False, length=None, ghunna=None,
                              qalqalah=None, tafkheem="moraqaq",
                              sakt_after=True, pausal_role=None,
                              provenance=(app,), src_span=p.src_span,
                              word_index=p.word_index - 1)
                out[i] = _replace(p, geminated=False,
                                  provenance=p.provenance + (app,))
                out.insert(i, first)
                break
    return out
