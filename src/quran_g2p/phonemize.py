"""Phone emission: OrthoSeg stream -> Phone stream per waqf segment.

v1 pipeline (rule ids carried in provenance; formal per-rule spec files land
with each phase's completion):

  P2  R100: waqf segmentation (v1: single segment, ayah end)
  P3  R110: ibtida' hamzat-wasl resolution (v1: definite article -> fatha;
            anything else fails closed and drives the word-class table)
  P4  R120: iskan al-waqf (final short vowel dropped)
      R121: tanween handling at waqf ('iwad handled via the seat alef,
            damm/kasr tanween dropped)
      R122: taa marbuta -> heh at pause
  P5  R130: mid-segment hamzat-wasl elision
      R133/R160-class: bare consonant before geminated consonant = kamil
            idgham, first letter deleted (lam shamsiyya, mutamathilayn);
            bare NOON before shadda waw/yeh = naqis idgham with ghunna on
            the target (R141's cross-word case)
      R134: lam al-jalala implicit alif (fixed {2})

Everything else (madd classification, qalqalah, tafkheem, sifat, noon/meem
detail work) lands in later phases operating on the Phone stream.
"""
from __future__ import annotations

from dataclasses import dataclass, field

from .config import HafsConfig
from .ir import Base, LengthSpec, Phone, RuleApp
from .ortho import ConsSeg, DecodeError, MaddSeg, MaddSource, SukunKind, VQ
from .pipeline import run
from .textbank import AyahRef
from .waqf import WaqfSpec

_VOWEL_BASE = {VQ.A: Base.FATHA, VQ.U: Base.DAMMA, VQ.I: Base.KASRA}
_MADD_BASE = {VQ.A: Base.ALEF_MADD, VQ.U: Base.WAW_MADD, VQ.I: Base.YEH_MADD}

_TABEEI = LengthSpec(kind="fixed", allowed=frozenset({2}), canonical=2,
                     scoring=frozenset({2}))


@dataclass
class Segment:
    phones: list[Phone]
    waqf_kind: str  # "ayah_end" (v1)


@dataclass
class PhonemizeResult:
    segments: list[Segment]
    trace: list[RuleApp] = field(default_factory=list)


def phonemize(text: str, edition: str, ref: AyahRef | None = None,
              config: HafsConfig | None = None,
              waqf: WaqfSpec | None = None) -> PhonemizeResult:
    config = config or HafsConfig()
    waqf = waqf or WaqfSpec.ayah_end()
    ctx = run(text, edition=edition, ref=ref, config=config)

    all_segs = list(ctx.segs)
    trace = list(ctx.trace)

    # P2 (R100): split at the reciter's stops FIRST; every contextual
    # phase then runs per breath group, so pausal forms, ibtida', and
    # junction rules all see exactly the context the recitation has.
    n_words = max((s.word_index for s in all_segs), default=0) + 1
    stops = sorted(set(waqf.stops))
    if any(k < 0 or k >= n_words - 1 for k in stops):
        raise ValueError(f"waqf stop out of range for {n_words}-word text: "
                         f"{stops}")
    bounds = stops + [n_words - 1]
    groups: list[list] = [[] for _ in bounds]
    for seg in all_segs:
        for gi, k in enumerate(bounds):
            if seg.word_index <= k:
                groups[gi].append(seg)
                break

    segments = []
    for gi, group in enumerate(groups):
        kind = "ayah_end" if gi == len(groups) - 1 else f"waqf@{bounds[gi]}"
        segments.append(Segment(_run_phases(group, trace, config, ref, ctx),
                                kind))
    return PhonemizeResult(segments=segments, trace=trace)


def _run_phases(segs, trace, config, ref, ctx):
    segs = _p3_ibtida(segs, trace)
    segs = _p3_strip_initial_shadda(segs, trace)
    segs = _p4_pausal(segs, trace)
    phones = _emit(segs, trace, config)
    phones = _p6_p7_noon_meem(phones, trace)
    phones = _p8_mutamathilayn(phones, trace)
    phones = _p10_madd(phones, trace, config)
    phones = _p9_ghunna(phones, trace)
    phones = _p11_qalqalah(phones, trace)
    phones = _p12_tafkheem(phones, trace, config)
    phones = _p12b_waqf_ra_khilaf(phones, trace, config)
    phones = _p13_oneoffs(phones, trace, ref, ctx, config)
    return phones


# --- P3 -----------------------------------------------------------------

def _p3_ibtida(segs, trace):
    if not segs:
        return segs
    head = segs[0]
    if not (isinstance(head, ConsSeg) and head.letter is Base.HAMZAT_WASL):
        return segs
    from .wasl_classes import (is_arida_damma_verb, is_wasl_noun,
                               word_letters_after_wasla)

    nxt = segs[1] if len(segs) > 1 else None
    letters = word_letters_after_wasla(segs, head.word_index)
    # A lam can open a VERB's radicals (form-VIII of lam-initial roots:
    # ٱلْتَقَى، ٱلْتَقَتَا، ٱلْتَقَيْتُمْ — QAC oracle catch). The article
    # before a shamsi letter always assimilates (bare lam + shadda in the
    # dabt), so an explicitly sakin lam followed by an UNshaddad shamsi
    # letter cannot be the article.
    _SHAMSI = {Base.TEH, Base.THEH, Base.DAL, Base.THAL, Base.REH, Base.ZAIN,
               Base.SEEN, Base.SHEEN, Base.SAD, Base.DAD, Base.TAH, Base.ZAH,
               Base.LAM, Base.NOON}
    nxt2 = segs[2] if len(segs) > 2 else None
    lam_is_article = (isinstance(nxt, ConsSeg) and nxt.letter is Base.LAM
                      and not (nxt.vowel is None and nxt.shadda is False
                               and isinstance(nxt2, ConsSeg)
                               and nxt2.letter in _SHAMSI
                               and not nxt2.shadda
                               and nxt2.letter is not Base.LAM))
    if lam_is_article:
        # Definite article: hamza + FATHA (R110).
        vq, note = VQ.A, "article->a"
    elif is_wasl_noun(letters):
        # The seven Quranic sama'i nouns: KASRA wajib (Jazariyya 101-103) —
        # load-bearing for suffixed forms like اسْمُهُ whose third slot is
        # a damma the verb rule would misread.
        vq, note = VQ.I, "noun->i"
    elif is_arida_damma_verb(segs, head.word_index):
        # The five 'arida-damma verbs (Hidayat al-Qari 2:482 hasr): KASRA.
        vq, note = VQ.I, "arida->i"
    else:
        # Verb rule (R110): the third letter's haraka decides — damma asliyya
        # -> hamza+damma, else hamza+kasra. The hamza itself is slot 1; a
        # geminated letter occupies slots 2 and 3 with its vowel on slot 3.
        slot = 1
        third_vowel = None
        for seg in segs[1:]:
            if not isinstance(seg, ConsSeg):
                break
            slot += 2 if seg.shadda else 1
            if slot >= 3:
                third_vowel = seg.vowel or (seg.tanween.quality if seg.tanween else None)
                break
        if third_vowel is None:
            raise DecodeError("R110: cannot find third-letter haraka after hamzat wasl")
        vq = VQ.U if third_vowel is VQ.U else VQ.I
        note = f"verb->{vq.value}"
    resolved = ConsSeg(Base.HAMZA, vq, None, None, False, "wasl",
                       head.madda, False, head.span, head.word_index)
    trace.append(RuleApp("R110_WASL_START", "SPEC-110", head.span, note=note))
    out = [resolved] + segs[1:]
    # Badal at ibtida' (اؤتمن -> أُوتُمِن; ائتوني -> إِيتُوني): the sakin
    # hamza right after the resolved wasl-hamza becomes the madd letter of
    # the resolved vowel's quality.
    if (len(out) > 1 and isinstance(out[1], ConsSeg)
            and out[1].letter is Base.HAMZA and out[1].vowel is None
            and out[1].tanween is None):
        trace.append(RuleApp("R110_BADAL_IBTIDA", "SPEC-110", out[1].span))
        out[1] = MaddSeg(vq, MaddSource.PLAIN_ALEF, False, out[1].span,
                         out[1].word_index)
    return out


def _p3_strip_initial_shadda(segs, trace):
    """R112: an ayah-initial shadda encodes idgham with the PREVIOUS ayah's
    final letter (wasl dabt); at ibtida' it degeminates (لَّيْسَ -> laysa,
    مَّا -> maa, رَّبَّنَا -> rabbanaa)."""
    if not segs:
        return segs
    head = segs[0]
    if isinstance(head, ConsSeg) and head.shadda:
        segs = list(segs)
        segs[0] = ConsSeg(head.letter, head.vowel, head.tanween, head.sukun,
                          False, head.hamza_carrier, head.madda,
                          head.iqlab_mark, head.span, head.word_index)
        trace.append(RuleApp("R112_STRIP_INITIAL_SHADDA", "SPEC-110", head.span))
    return segs


# --- P4 -----------------------------------------------------------------

def _p4_pausal(segs, trace):
    if not segs:
        return segs
    out = list(segs)

    # find last seg; apply pausal transforms (R120-R122)
    last = out[-1]
    if isinstance(last, MaddSeg):
        # R183: silah vanishes at waqf — the heh damir takes iskan.
        if last.source in (MaddSource.SMALL_WAW, MaddSource.SMALL_YEH):
            prev = out[-2]
            out.pop()
            out[-1] = ConsSeg(prev.letter, None, None, SukunKind.MARKED,
                              prev.shadda, prev.hamza_carrier, prev.madda,
                              False, prev.span, prev.word_index)
            trace.append(RuleApp("R183_SILAH_WAQF_DROP", "SPEC-183", prev.span))
            trace.append(RuleApp("R120_ISKAN", "SPEC-120", prev.span))
            return out
        # R121 madd al-'iwad: a final madd seat after tanween-fath replaces
        # the tanween at waqf (هُدًى -> hudaa). Drop the tanween, keep fatha.
        prev = out[-2] if len(out) > 1 else None
        if (isinstance(prev, ConsSeg) and prev.tanween is not None
                and prev.tanween.quality is VQ.A):
            out[-2] = ConsSeg(prev.letter, VQ.A, None, None, prev.shadda,
                              prev.hamza_carrier, prev.madda, False,
                              prev.span, prev.word_index)
            trace.append(RuleApp("R121_MADD_EWAD", "SPEC-121", prev.span))
        return out  # ends in a madd letter (aared/'iwad classified in P10)
    if not isinstance(last, ConsSeg):
        return out

    vowel, tanween = last.vowel, last.tanween
    letter = last.letter
    if letter is Base.TEH_MARBUTA:
        letter = Base.HEH
        vowel, tanween = None, None
        trace.append(RuleApp("R122_TAA_MARBUTA_WAQF", "SPEC-122", last.span))
    elif tanween is not None:
        if tanween.quality is VQ.A:
            # R121 'iwad WITHOUT a written seat (إِنشَآءً: hamza after a madd
            # letter carries the tanween, no trailing alef): fatha + synthesized
            # 'iwad madd {2}.
            out[-1] = ConsSeg(letter, VQ.A, None, None, last.shadda,
                              last.hamza_carrier, last.madda, False,
                              last.span, last.word_index)
            out.append(MaddSeg(VQ.A, MaddSource.PLAIN_ALEF, False,
                               last.span, last.word_index))
            trace.append(RuleApp("R121_MADD_EWAD", "SPEC-121", last.span,
                                 note="seatless"))
            return out
        # damm/kasr tanween drop at waqf (R120).
        tanween = None
        trace.append(RuleApp("R120_ISKAN", "SPEC-120", last.span, note="tanween"))
    elif vowel is not None:
        vowel = None
        trace.append(RuleApp("R120_ISKAN", "SPEC-120", last.span))
    out[-1] = ConsSeg(letter, vowel, tanween, last.sukun or SukunKind.MARKED,
                      last.shadda, last.hamza_carrier, last.madda,
                      last.iqlab_mark, last.span, last.word_index)
    out[-1] = _mark_pausal(out[-1])
    return out


def _mark_pausal(seg: ConsSeg) -> ConsSeg:
    return seg  # pausal_role lands on phones during emission


# --- P5 + emission -------------------------------------------------------

def _emit(segs, trace, config: HafsConfig) -> list[Phone]:
    phones: list[Phone] = []
    pending_ghunna: set[int] = set()   # seg indices, per call
    pending_apps: dict[int, RuleApp] = {}
    n = len(segs)
    for idx, seg in enumerate(segs):
        nxt = segs[idx + 1] if idx + 1 < n else None
        if isinstance(seg, MaddSeg):
            if seg.waqf_only and idx != n - 1:
                continue  # silent in wasl (R014/06E0); pronounced only at pause
            prev = segs[idx - 1] if idx > 0 else None
            if (isinstance(prev, ConsSeg) and prev.tanween is not None):
                # 'iwad seat after tanween-fath: silent in wasl (R121); at
                # waqf P4 already converted the tanween so this branch only
                # sees true wasl contexts.
                trace.append(RuleApp("R121_EWAD_SEAT_SILENT", "SPEC-121", seg.span))
                continue
            # Provisional tabee'i {2}; P10 reclassifies (muttasil/lazim/aared…)
            # and the madd-sign witness accounting catches anything it misses.
            note = f"src:{seg.source.value}" + ("+madda" if seg.madda else "")
            phones.append(_phone(_MADD_BASE[seg.quality], "madd", seg,
                                 length=_TABEEI, note=note))
            continue

        if seg.letter is Base.HAMZAT_WASL:
            # mid-segment wasl: elided (R130) — with the two R131 iltiqa'
            # al-sakinayn junction effects the elision exposes:
            trace.append(RuleApp("R130_WASL_ELISION", "SPEC-130", seg.span))
            if phones and phones[-1].kind == "madd":
                # madd letter meets the article/verb sakin: shortened away
                # (قَالُوا ٱدْعُ, فِي ٱلْأَرْضِ, ٱهْدِنَا ٱلصِّرَٰطَ).
                phones.pop()
                trace.append(RuleApp("R131_MADD_SHORTENING", "SPEC-131", seg.span))
            elif phones and _is_tanween_noon(phones[-1]):
                # tanween before wasl: noon al-wiqaya takes kasra
                # (خَيْرًا ٱلْوَصِيَّةُ -> khayran i-l-wasiyyah). The kasra
                # belongs to the noon's word, not the wasla's.
                prev = phones[-1]
                kasra = Phone(Base.KASRA, "vowel", False, None, None, None,
                              "moraqaq", False, None, (), prev.src_span,
                              prev.word_index)
                phones.append(kasra)
                trace.append(RuleApp("R131_NOON_WIQAYA", "SPEC-131", seg.span))
            continue

        if seg.sukun is SukunKind.BARE and isinstance(nxt, ConsSeg) and nxt.shadda:
            if seg.letter is Base.NOON and nxt.letter in (Base.WAW, Base.YEH):
                # R141 naqis idgham: noon deleted, ghunna rides the target.
                trace.append(RuleApp("R141_IDGHAM_GHUNNA_NAQIS", "SPEC-141", seg.span))
                pending_ghunna.add(idx + 1)
                continue
            # kamil idgham: article lam / mutamathilayn first letter (R133/R160)
            app = RuleApp("R133_R160_IDGHAM_KAMIL", "SPEC-133", seg.span)
            trace.append(app)
            if seg.word_index != nxt.word_index:
                pending_apps[idx + 1] = app  # cross-word: mark the target
            continue

        letter = seg.letter
        if letter is Base.TEH_MARBUTA:
            letter = Base.TEH  # wasl value (R018)

        ghunna = "idgham" if idx in pending_ghunna else None
        pending_ghunna.discard(idx)
        note_parts = []
        if seg.iqlab_mark:
            note_parts.append("iqlab_witness")
        if seg.sukun is not None:
            note_parts.append(f"sukun:{seg.sukun.value}")
        cons_phone = _phone(letter, "consonant", seg, geminated=seg.shadda,
                            ghunna=ghunna, note="+".join(note_parts))
        if idx in pending_apps:
            from dataclasses import replace as _replace
            cons_phone = _replace(cons_phone,
                                  provenance=cons_phone.provenance + (pending_apps.pop(idx),))
        phones.append(cons_phone)

        if seg.vowel is not None:
            phones.append(_phone(_VOWEL_BASE[seg.vowel], "vowel", seg))
        elif seg.tanween is not None:
            phones.append(_phone(_VOWEL_BASE[seg.tanween.quality], "vowel", seg))
            noon_note = "tanween_noon+iqlab" if seg.iqlab_mark else "tanween_noon"
            phones.append(_phone(Base.NOON, "consonant", seg, note=noon_note))

        # R134: lam al-jalala implicit alif — the word must BE the ism Allah:
        # its consonant letters end (…LAM, LAM, HEH) with the heh word-final
        # (excludes كُلَّهَا whose lams collapse into one seg, and ٱللَّهْو
        # whose waw follows the heh).
        if (seg.letter is Base.LAM and seg.shadda and seg.vowel is VQ.A
                and isinstance(nxt, ConsSeg) and nxt.letter is Base.HEH
                and _is_jalala_word(segs, seg.word_index)):
            phones.append(Phone(Base.ALEF_MADD, "madd", False, _TABEEI, None,
                                None, "moraqaq", False, None,
                                (RuleApp("R134_LAM_JALALA_ALIF", "SPEC-134", seg.span),),
                                seg.span, seg.word_index))
            trace.append(RuleApp("R134_LAM_JALALA_ALIF", "SPEC-134", seg.span))
    return phones


def _phone(base: Base, kind: str, seg, geminated: bool = False,
           length: LengthSpec | None = None, ghunna=None, note: str = "") -> Phone:
    prov = (RuleApp("EMIT", "SPEC-003", seg.span, note=note),) if note else ()
    return Phone(base, kind, geminated, length, ghunna, None, "moraqaq", False,
                 None, prov, seg.span, seg.word_index)


def _is_jalala_word(segs, word: int) -> bool:
    letters = [s.letter for s in segs
               if isinstance(s, ConsSeg) and s.word_index == word]
    if len(letters) >= 3 and tuple(letters[-3:]) == (Base.LAM, Base.LAM, Base.HEH):
        return True
    # اللَّهُمَّ (allaahumma) keeps the jalala madd with its meem suffix
    return (len(letters) >= 4
            and tuple(letters[-4:]) == (Base.LAM, Base.LAM, Base.HEH, Base.MEEM))


def _note(p: Phone) -> str:
    return p.provenance[0].note if p.provenance else ""


def _is_tanween_noon(p: Phone) -> bool:
    return p.base is Base.NOON and _note(p).startswith("tanween_noon")


# --- P6/P7: noon sakinah & tanween 4-way, meem sakinah 3-way -------------

_HALQI = {Base.HAMZA, Base.HEH, Base.AIN, Base.HAH, Base.GHAIN, Base.KHAH}
_IDGHAM_GHUNNA_TARGETS = {Base.YEH, Base.WAW, Base.NOON, Base.MEEM}
_IDGHAM_PLAIN_TARGETS = {Base.LAM, Base.REH}


def _p6_p7_noon_meem(phones: list[Phone], trace) -> list[Phone]:
    from dataclasses import replace as _replace

    out = list(phones)
    i = 0
    while i < len(out):
        p = out[i]
        nxt = out[i + 1] if i + 1 < len(out) else None
        is_sakin_cons = (p.kind == "consonant" and not p.geminated
                         and (nxt is None or nxt.kind != "vowel"))
        if not is_sakin_cons or nxt is None:
            i += 1
            continue

        if p.base is Base.NOON and p.ghunna is None:
            tgt = nxt
            cross_word = tgt.word_index != p.word_index or _is_tanween_noon(p)
            # Dabt-driven gate (SPEC-002): a MARKED sukun on the noon is the
            # mushaf's izhar witness (halqi neighbours, the sakt sites 75:27
            # etc., and the يس/ن letter-name junctions). Only BARE noons and
            # tanween noons undergo the assimilation branches.
            if "sukun:marked" in _note(p):
                out[i] = _with_prov(_replace(p, ghunna="asl"), p,
                                    "R140_IZHAR", "SPEC-140", trace)
                i += 1
                continue
            if tgt.base in _HALQI:
                out[i] = _with_prov(_replace(p, ghunna="asl"), p,
                                    "R140_IZHAR_HALQI", "SPEC-140", trace)
            elif tgt.base is Base.BEH:
                out[i] = _with_prov(
                    _replace(p, base=Base.MEEM_MUKHFAH, ghunna="ikhfa"), p,
                    "R143_IQLAB", "SPEC-143", trace)
            elif tgt.base in _IDGHAM_GHUNNA_TARGETS and cross_word:
                # trace keyed by the NOON's span (the rule's trigger); the
                # target phone's provenance records the same application.
                # KAMIL targets (noon/meem) geminate — ن+م -> مّ (طسٓمٓ keeps
                # its lazim context through the merge); waw/yeh stay naqis.
                app = RuleApp("R141_IDGHAM_GHUNNA", "SPEC-141", p.src_span)
                trace.append(app)
                kamil = tgt.base in (Base.NOON, Base.MEEM)
                out[i + 1] = _replace(tgt, ghunna="idgham",
                                      geminated=tgt.geminated or kamil,
                                      provenance=tgt.provenance + (app,))
                del out[i]
                continue
            elif tgt.base in _IDGHAM_GHUNNA_TARGETS:
                # same-word noon + waw/yeh: izhar mutlaq (دنيا بنيان صنوان قنوان)
                out[i] = _with_prov(_replace(p, ghunna="asl"), p,
                                    "R141_IZHAR_MUTLAQ", "SPEC-141", trace)
            elif tgt.base in _IDGHAM_PLAIN_TARGETS and cross_word:
                app = RuleApp("R142_IDGHAM_BILA_GHUNNA", "SPEC-142", p.src_span)
                trace.append(app)
                out[i + 1] = _replace(tgt, provenance=tgt.provenance + (app,))
                del out[i]
                continue
            else:
                out[i] = _with_prov(
                    _replace(p, base=Base.NOON_MUKHFAH, ghunna="ikhfa"), p,
                    "R144_IKHFA", "SPEC-144", trace)
        elif p.base is Base.MEEM and p.ghunna is None:
            if nxt.base is Base.BEH:
                out[i] = _with_prov(
                    _replace(p, base=Base.MEEM_MUKHFAH, ghunna="ikhfa"), p,
                    "R150_IKHFA_SHAFAWI", "SPEC-150", trace)
            # else izhar shafawi: nothing to change (R152)
        i += 1
    return out


def _with_prov(newp: Phone, old: Phone, rule_id: str, spec: str, trace) -> Phone:
    from dataclasses import replace as _replace
    app = RuleApp(rule_id, spec, old.src_span)
    trace.append(app)
    return _replace(newp, provenance=old.provenance + (app,))


# --- P8: mutamathilayn saghir at the phone level (SPEC-160) ---------------

def _p8_mutamathilayn(phones: list[Phone], trace) -> list[Phone]:
    """Identical letters, first sakin -> one geminated phone. The dabt marks
    most sites with shadda (handled at seg level); this pass catches the
    unmarked junctions the spell-out creates (لَامْ مِيمْ in الم etc.).
    Sakt blocks the merge; madd letters never merge (قَالُوا وَ… exception is
    structural: madd phones are not consonants)."""
    from dataclasses import replace as _replace
    out = list(phones)
    i = 0
    while i + 1 < len(out):
        p, nxt = out[i], out[i + 1]
        if (p.kind == "consonant" and nxt.kind == "consonant"
                and p.base is nxt.base and not p.geminated
                and not p.sakt_after
                and (i + 2 < len(out) and out[i + 2].kind == "vowel")):
            app = RuleApp("R160_MUTAMATHILAYN", "SPEC-160", p.src_span)
            trace.append(app)
            out[i + 1] = _replace(nxt, geminated=True,
                                  provenance=nxt.provenance + (app,))
            del out[i]
            continue
        i += 1
    return out


# --- P9: ghunna grades (SPEC-170) ----------------------------------------

#: Ghunna duration prescription (CONVENTION: ~2 harakat; scoring admits the
#: attested 1..3 range for alignment-derived labels/grading).
_GHUNNA_LEN = LengthSpec("fixed", frozenset({2}), 2, frozenset({1, 2, 3}))


def _p9_ghunna(phones: list[Phone], trace) -> list[Phone]:
    from dataclasses import replace as _replace
    out = list(phones)
    for i, p in enumerate(out):
        if (p.kind == "consonant" and p.geminated
                and p.base in (Base.NOON, Base.MEEM) and p.ghunna is None):
            p = _with_prov(_replace(p, ghunna="mushaddadah"), p,
                           "R170_GHUNNA_MUSHADDADAH", "SPEC-170", trace)
            out[i] = p
        # Every ghunna-bearing consonant carries the duration prescription so
        # S3 alignment fills realized ghunna lengths through the same
        # machinery as madd (rule_index completeness for tajweed grading).
        if (out[i].kind == "consonant" and out[i].length is None
                and out[i].ghunna in ("mushaddadah", "idgham", "ikhfa")):
            out[i] = _replace(out[i], length=_GHUNNA_LEN)
    return out


# --- P11: qalqalah (SPEC-200..202) ---------------------------------------

_QALQALAH = {Base.QAF, Base.TAH, Base.BEH, Base.JEEM, Base.DAL}


def _p11_qalqalah(phones: list[Phone], trace) -> list[Phone]:
    from dataclasses import replace as _replace
    out = list(phones)
    n = len(out)
    for i, p in enumerate(out):
        if p.kind != "consonant" or p.base not in _QALQALAH:
            continue
        sakin = i + 1 >= n or out[i + 1].kind != "vowel"
        if not sakin:
            continue
        nxt = out[i + 1] if i + 1 < n else None
        # naqis-idgham retention (بَسَطتَ class): tah kept sakin before teh —
        # itbaq retained, qalqalah suppressed (SPEC-161).
        if p.base is Base.TAH and nxt is not None and nxt.base is Base.TEH:
            trace.append(RuleApp("R161_NAQIS_TA_NO_QALQALAH", "SPEC-161", p.src_span))
            continue
        if i == n - 1:
            grade = "akbar" if p.geminated else "kubra"
            rule = "R202_QALQALAH_AKBAR" if p.geminated else "R201_QALQALAH_KUBRA"
        else:
            grade, rule = "sughra", "R200_QALQALAH_SUGHRA"
        out[i] = _with_prov(_replace(p, qalqalah=grade), p, rule, "SPEC-200", trace)
    return out


# --- P12: tafkheem / tarqeeq (SPEC-210..214) ------------------------------

_ISTILA = {Base.KHAH, Base.SAD, Base.DAD, Base.GHAIN, Base.TAH, Base.QAF, Base.ZAH}


def _p12_tafkheem(phones: list[Phone], trace, config: HafsConfig) -> list[Phone]:
    from dataclasses import replace as _replace
    out = list(phones)
    n = len(out)

    def next_vowel(i):
        return out[i + 1].base if i + 1 < n and out[i + 1].kind == "vowel" else None

    def prev_vowel_base(i):
        for j in range(i - 1, -1, -1):
            if out[j].kind == "vowel":
                return out[j].base, out[j], j
            if out[j].kind == "madd":
                return out[j].base, out[j], j
            return None, out[j], j
        return None, None, None

    def rank_of(i, level):
        """Classical maraatib al-tafkheem (Ibn al-Jazari; SPEC-210):
        1 fath+alif, 2 fath, 3 damm, 4 sukun, 5 kasr (= low_mofakham)."""
        if level == "low_mofakham":
            return 5
        nv = next_vowel(i)
        if nv is Base.FATHA:
            has_alef = (i + 2 < n and out[i + 2].kind == "madd"
                        and out[i + 2].base in (Base.ALEF_MADD, Base.ALEF_IMALA))
            return 1 if has_alef else 2
        if nv is Base.DAMMA:
            return 3
        if nv is None:
            return 4
        return 2

    # pass A: consonants
    for i, p in enumerate(out):
        if p.kind != "consonant":
            continue
        level = None
        rule = None
        if p.base in _ISTILA:
            level = "low_mofakham" if next_vowel(i) is Base.KASRA else "mofakham"
            rule = "R210_ISTILA"
        elif p.base is Base.REH:
            level, rule = _reh_level(out, i, n, config), "R211_REH"
        elif p.base is Base.LAM and p.geminated and any(
                a.rule_id == "R134_LAM_JALALA_ALIF" for a in
                (out[i + 2].provenance if i + 2 < n else ())):
            pv, _, _ = prev_vowel_base(i)
            level = "moraqaq" if pv in (Base.KASRA, Base.YEH_MADD) else "mofakham"
            rule = "R212_LAM_JALALA"
        elif p.base is Base.NOON_MUKHFAH:
            nxt = out[i + 1] if i + 1 < n else None
            if nxt is not None and nxt.base in _ISTILA:
                level, rule = "mofakham", "R214_IKHFA_TAFKHEEM"
        if level is not None:
            rank = rank_of(i, level) if level != "moraqaq" else None
            if level != p.tafkheem or rank != p.tafkheem_rank:
                out[i] = _with_prov(
                    _replace(p, tafkheem=level, tafkheem_rank=rank),
                    p, rule, "SPEC-210", trace)

    # pass B: vowels and madds inherit from their host consonant (R213)
    for i, p in enumerate(out):
        if p.kind == "consonant":
            continue
        for j in range(i - 1, -1, -1):
            if out[j].kind == "consonant":
                if (out[j].tafkheem != p.tafkheem
                        or out[j].tafkheem_rank != p.tafkheem_rank):
                    out[i] = _replace(p, tafkheem=out[j].tafkheem,
                                      tafkheem_rank=out[j].tafkheem_rank)
                break
    return out


# --- P13: Hafs one-off events (SPEC-132, 220, 221, 222) -------------------

def _p13_oneoffs(phones: list[Phone], trace, ref, ctx,
                 config: HafsConfig | None = None) -> list[Phone]:
    from dataclasses import replace as _replace
    from . import codepoints as cp

    if ref is None:
        return phones
    key = (ref.surah, ref.ayah)
    out = list(phones)

    def mark_positions(markset):
        pos = []
        for c in ctx.clusters:
            for k, m in enumerate(c.marks):
                if m in markset:
                    pos.append(c.span[0] + 1 + k)
        return pos

    def covering(pos):
        return [i for i, p in enumerate(out)
                if p.src_span[0] <= pos < max(p.src_span[1], p.src_span[0] + 1)
                or p.src_span[0] == pos - 1]

    # R132 — the mid-ayah sakt sites (witnessed by KFGQPC small seen; Tanzil
    # site-keyed). 18:1 and 69:28 are ayah-final sakts (wasl into the next
    # ayah) and land with concat/waqf support.
    sakt_targets = {
        (75, 27): (Base.NOON, 1),   # وَقِيلَ(0) مَنْ(1)ۜ رَاقٍ
        (83, 14): (Base.LAM, 1),    # كَلَّا(0) بَلْ(1)ۜ رَانَ — the SAKIN lam
        (36, 52): (None, 5),        # مِن مَّرْقَدِنَا(5)ۜ هَٰذَا
    }
    if key in sakt_targets:
        base, word = sakt_targets[key]
        def _sakin(i):
            return i + 1 >= len(out) or out[i + 1].kind != "vowel"
        idxs = [i for i, p in enumerate(out)
                if p.word_index == word and (base is None or p.base is base)
                and (base is None or _sakin(i))]
        if not idxs:
            return out  # site word not in this waqf segment (sakt is wasl-only)
        i = idxs[-1] if base is None else idxs[0]
        app = RuleApp("R132_SAKT", "SPEC-132", out[i].src_span)
        trace.append(app)
        out[i] = _replace(out[i], sakt_after=True,
                          provenance=out[i].provenance + (app,))

    # R221 — imala 11:41 (U+06EA witness): reh's fatha -> fatha_imala, the
    # dagger madd -> alef_imala, reh itself moraqaq.
    if key == (11, 41):
        pos = mark_positions({cp.EMPTY_CENTRE_LOW_STOP})
        assert pos, "imala witness missing"
        # The imala mark occupies the reh's vowel slot in the rasm, so the reh
        # decoded bare with the dagger madd right after: reh -> reh,
        # +FATHA_IMALA inserted, madd -> ALEF_IMALA, all moraqaq.
        reh_i = next((i for i, p in enumerate(out)
                      if p.base is Base.REH and p.src_span[0] == pos[0] - 1),
                     None)
        if reh_i is None:
            return out  # site in the other waqf segment
        app = RuleApp("R221_IMALA", "SPEC-221", out[reh_i].src_span)
        trace.append(app)
        host = out[reh_i]
        madd = out[reh_i + 1]
        assert madd.kind == "madd", "expected the dagger madd after the imala reh"
        out[reh_i:reh_i + 2] = [
            _replace(host, tafkheem="moraqaq", provenance=host.provenance + (app,)),
            Phone(Base.FATHA_IMALA, "vowel", False, None, None, None, "moraqaq",
                  False, None, (app,), host.src_span, host.word_index),
            _replace(madd, base=Base.ALEF_IMALA, tafkheem="moraqaq",
                     provenance=madd.provenance + (app,)),
        ]

    # R222 — tasheel 41:44: the marked alef seat is a hamza musahhala + fatha.
    if key == (41, 44):
        pos = mark_positions({cp.ROUNDED_HIGH_STOP_WITH_FILLED_CENTRE,
                              cp.EMPTY_CENTRE_HIGH_STOP})
        assert pos, "tasheel witness missing"
        target = next((i for i, p in enumerate(out)
                       if p.kind == "madd"
                       and pos[0] - 1 <= p.src_span[0] <= pos[0] + 1),
                      None)
        if target is None:
            return out  # site in the other waqf segment
        app = RuleApp("R222_TASHEEL", "SPEC-222", out[target].src_span)
        trace.append(app)
        host = out[target]
        out[target:target + 1] = [
            Phone(Base.HAMZA_MUSAHHALA, "consonant", False, None, None, None,
                  "moraqaq", False, None, host.provenance + (app,),
                  host.src_span, host.word_index),
            Phone(Base.FATHA, "vowel", False, None, None, None, "moraqaq",
                  False, None, (app,), host.src_span, host.word_index),
        ]

    # R014b — istifham+wasl tasheel wajh (six sites): replace the ibdal
    # alif (lazim 6) with HAMZA_MUSAHHALA + fatha — no madd (فتح الوصيد
    # 1:350 «المسهلة في زنة المحركة... لم يقع مع التسهيل اجتماع ساكنين»).
    ISTIFHAM_SITES = {(6, 143), (6, 144), (10, 51), (10, 59), (10, 91), (27, 59)}
    if key in ISTIFHAM_SITES and ctx.config.istifham_tasheel:
        for i, p in enumerate(out):
            if (p.kind == "madd" and p.base is Base.ALEF_MADD
                    and p.length is not None
                    and p.length.allowed == frozenset({6})
                    and i >= 2 and out[i - 2].base is Base.HAMZA):
                app = RuleApp("R014B_ISTIFHAM_TASHEEL", "SPEC-012", p.src_span)
                trace.append(app)
                out[i:i + 1] = [
                    Phone(Base.HAMZA_MUSAHHALA, "consonant", False, None, None,
                          None, "moraqaq", False, None, p.provenance + (app,),
                          p.src_span, p.word_index),
                    Phone(Base.FATHA, "vowel", False, None, None, None,
                          "moraqaq", False, None, (app,), p.src_span,
                          p.word_index),
                ]
                break

    # R012b — ضعف 30:54 ×3: damm wajh (Hafs' ikhtiyar; fath = the riwaya,
    # muqaddam — Shatibiyya 722-723, al-Taysir 174-176). Vowel substitution
    # on the dad of the three ضعف words when the knob flips.
    if key == (30, 54) and ctx.config.daaf_30_54_damm:
        for i, p in enumerate(out):
            if (p.base is Base.DAD and i + 1 < len(out)
                    and out[i + 1].kind == "vowel"
                    and out[i + 1].base is Base.FATHA):
                nxt_cons = next((q for q in out[i + 2:] if q.kind == "consonant"), None)
                if nxt_cons is not None and nxt_cons.base is Base.AIN:
                    app = RuleApp("R012B_DAAF_DAMM", "SPEC-012", p.src_span)
                    trace.append(app)
                    out[i + 1] = _replace(out[i + 1], base=Base.DAMMA)

    # R220 — ishmam 12:11 (Tanzil U+06EB; KFGQPC U+06EC): attribute event on
    # the geminated noon of ta'manna.
    if key == (12, 11):
        noon_i = next((i for i, p in enumerate(out)
                       if p.base is Base.NOON and p.geminated), None)
        if noon_i is not None:
            app = RuleApp("R220_ISHMAM", "SPEC-220", out[noon_i].src_span)
            trace.append(app)
            out[noon_i] = _replace(out[noon_i],
                                   provenance=out[noon_i].provenance + (app,))

    # R190B — سَلَٰسِلَا۟ 76:4 waqf wajhan (SPEC-184): the printed dabt is
    # hadhf (default); the ithbat wajh appends the itlaq alif on the lam.
    if (key == (76, 4) and config is not None and config.salasila_waqf_alif
            and len(out) >= 3 and out[-1].base is Base.LAM
            and out[-1].kind == "consonant"
            and out[-2].base is Base.KASRA and out[-3].base is Base.SEEN):
        app = RuleApp("R190B_SALASILA_ITHBAT", "SPEC-184", out[-1].src_span)
        trace.append(app)
        lam = out[-1]
        out.append(Phone(base=Base.FATHA, kind="vowel", geminated=False,
                         length=None, ghunna=None, qalqalah=None,
                         tafkheem="moraqaq", sakt_after=False,
                         pausal_role="pausal", provenance=(app,),
                         src_span=lam.src_span, word_index=lam.word_index))
        out.append(Phone(base=Base.ALEF_MADD, kind="madd", geminated=False,
                         length=_TABEEI, ghunna=None, qalqalah=None,
                         tafkheem="moraqaq", sakt_after=False,
                         pausal_role="pausal", provenance=(app,),
                         src_span=lam.src_span, word_index=lam.word_index))

    # R190C — ءَاتَىٰنِۦَ 27:36 waqf wajhan (SPEC-184): ithbat of the sakin
    # yaa is muqaddam (default, the yaa stands as the madd letter); the
    # hadhf wajh stops on the sakin noon.
    if (key == (27, 36) and config is not None and not config.aataani_waqf_yaa
            and len(out) >= 3 and out[-1].base is Base.YEH_MADD
            and out[-2].base is Base.KASRA and out[-3].base is Base.NOON):
        app = RuleApp("R190C_AATAANI_HADHF", "SPEC-184", out[-1].src_span)
        trace.append(app)
        out = out[:-2]
        out[-1] = _replace(out[-1], provenance=out[-1].provenance + (app,))
    return out


def _p12b_waqf_ra_khilaf(phones: list[Phone], trace, config: HafsConfig) -> list[Phone]:
    """R211 khilaf words at pausal ra (SPEC-210): نُذُرِ and يَسْرِ end ayat in
    v1 scope; both carry transmitted wajhan — the knob picks the wajh."""
    from dataclasses import replace as _replace
    out = list(phones)
    if not out or out[-1].base is not Base.REH or out[-1].kind != "consonant":
        return out
    word = out[-1].word_index
    letters = tuple(p.base for p in out
                    if p.kind == "consonant" and p.word_index == word)
    prev = out[-2] if len(out) > 1 else None
    knob = None
    # discriminate by the phone actually preceding the reh: نُذُرِ has the
    # dhal's DAMMA there; نَذِير has a yaa madd (definitive tarqeeq, no
    # khilaf). Same for يَسْرِ (sakin seen) vs يَسِير (yaa madd).
    # the khilaf is scoped to the six وَنُذُرِ refrains (deleted-yaa 'illa);
    # the article plural النُّذُر (geminated noon after the assimilated lam)
    # stays on the general rule (tafkheem after damma).
    gem_noon = any(p.base is Base.NOON and p.geminated and p.word_index == word
                   for p in out)
    if (letters[-3:] == (Base.NOON, Base.THAL, Base.REH) and not gem_noon
            and prev is not None and prev.base is Base.DAMMA):
        knob = config.nudhur_waqf_tafkheem
        note = "nudhur"
    elif (letters[-3:] == (Base.YEH, Base.SEEN, Base.REH)
            and prev is not None and prev.base is Base.SEEN):
        knob = config.yasr_waqf_tafkheem
        note = "yasr"
    elif (letters[-3:] == (Base.MEEM, Base.SAD, Base.REH)
            and prev is not None and prev.base is Base.SAD):
        # definite مِصْرَ (the tanween form ends in 'iwad alif and never
        # reaches here): tafkheem is al-Nashr's ikhtiyar (2:105)
        knob = config.misr_waqf_tafkheem
        note = "misr"
    elif (letters[-3:] == (Base.HAMZA, Base.SEEN, Base.REH)
            and prev is not None and prev.base is Base.SEEN):
        # أَسْرِ / فَأَسْرِ: tarqeeq muqaddam (kasrat al-binaa, al-Nashr
        # 2:110)
        knob = config.asr_waqf_tafkheem
        note = "asr"
    if knob is None:
        return out
    level = "mofakham" if knob else "moraqaq"
    rank = 4 if knob else None
    if out[-1].tafkheem != level:
        app = RuleApp("R211_WAQF_KHILAF", "SPEC-210", out[-1].src_span, note=note)
        trace.append(app)
        out[-1] = _replace(out[-1], tafkheem=level, tafkheem_rank=rank,
                           provenance=out[-1].provenance + (app,))
    return out


def _reh_level(out, i, n, config) -> str:
    """R211 — the reh decision table (khilaf-word knobs land in config later)."""
    has_vowel = i + 1 < n and out[i + 1].kind == "vowel"
    if has_vowel:
        return "moraqaq" if out[i + 1].base is Base.KASRA else "mofakham"
    # sakin reh: look back
    prev = out[i - 1] if i > 0 else None
    if prev is None:
        return "mofakham"
    if prev.kind == "vowel":
        if prev.base is Base.KASRA:
            # kasra 'arida (the resolved ibtida' hamza at segment start —
            # ٱرْجِعُوا -> irji'u with mofakham reh) keeps tafkheem.
            host = out[i - 2] if i > 1 else None
            if i - 2 == 0 and host is not None and host.base is Base.HAMZA:
                return "mofakham"
            # same-word isti'la after the sakin reh -> tafkheem (قِرْطَاس
            # مِرْصَاد); a MAKSUR isti'la letter is weakened and the wajhan
            # run (فِرْقٍ 26:63, the sole site — wajhan jayyidan per al-Dani,
            # tarqeeq the later tarjih; knob flips):
            j = i + 1
            if j < n and out[j].kind == "consonant" and out[j].base in _ISTILA \
                    and out[j].word_index == out[i].word_index:
                weakened = (j + 1 < n and out[j + 1].kind == "vowel"
                            and out[j + 1].base is Base.KASRA)
                if weakened:
                    return "mofakham" if config.firq_wasl_tafkheem else "moraqaq"
                return "mofakham"
            return "moraqaq"
        return "mofakham"
    if prev.kind == "madd":
        return "moraqaq" if prev.base is Base.YEH_MADD else "mofakham"
    # sakin before sakin reh (rare; e.g. after another sakin cons): default
    # by the vowel before that
    for j in range(i - 1, -1, -1):
        if out[j].kind == "vowel":
            return "moraqaq" if out[j].base is Base.KASRA else "mofakham"
        if out[j].kind == "madd":
            return "moraqaq" if out[j].base is Base.YEH_MADD else "mofakham"
    return "mofakham"


# --- P10: madd classification (SPEC-180..191) ----------------------------

def _free(allowed, canonical, scoring):
    return LengthSpec("free", frozenset(allowed), canonical, frozenset(scoring))


def _p10_madd(phones: list[Phone], trace, config: HafsConfig) -> list[Phone]:
    from dataclasses import replace as _replace

    # 'arid sakins: final consonants whose sukun came from P4 (iskan of a
    # vowel/tanween, or taa-marbuta conversion) — separates aared from lazim.
    arid_spans = {a.trigger_span for a in trace
                  if a.rule_id in ("R120_ISKAN", "R122_TAA_MARBUTA_WAQF")}

    out = list(phones)
    n = len(out)

    def is_sakin_at(j):
        if j >= n or out[j].kind != "consonant":
            return False
        return j + 1 >= n or out[j + 1].kind != "vowel"

    def classify(i):
        p = out[i]
        nxt = out[i + 1] if i + 1 < n else None
        note = _note(p)
        if nxt is None:
            # segment-final madd: 'iwad and plain tabee'i endings share the
            # fixed {2} class (the R182 split is a provenance refinement that
            # lands with full P2 waqf variants).
            return _TABEEI, "R180_TABEEI", "SPEC-180"
        if nxt.kind == "consonant":
            if nxt.base is Base.HAMZA:
                hamza_final_arid = (i + 1 == n - 1 and nxt.src_span in arid_spans)
                if hamza_final_arid:
                    return (_free({4, 5, 6}, config.madd_muttasil_waqf_len, {4, 5, 6}),
                            "R185_MUTTASIL_WAQF", "SPEC-185")
                if nxt.word_index == p.word_index:
                    return (_free({4, 5}, config.madd_muttasil_len, {4, 5, 6}),
                            "R185_MUTTASIL", "SPEC-185")
                if "src:small_waw" in note or "src:small_yeh" in note:
                    return (_free({4, 5}, config.madd_munfasil_len, {2, 3, 4, 5, 6}),
                            "R184_SILAH_KUBRA", "SPEC-184")
                return (_free({4, 5}, config.madd_munfasil_len, {2, 3, 4, 5, 6}),
                        "R186_MUNFASIL", "SPEC-186")
            if nxt.geminated:
                return (LengthSpec("fixed", frozenset({6}), 6, frozenset({6})),
                        "R187_LAZIM_MUTHAQQAL", "SPEC-187")
            if is_sakin_at(i + 1):
                if i + 1 == n - 1 and nxt.src_span in arid_spans:
                    return (_free({2, 4, 6}, config.madd_aared_len, {2, 3, 4, 5, 6}),
                            "R189_AARED", "SPEC-189")
                return (LengthSpec("fixed", frozenset({6}), 6, frozenset({6})),
                        "R187_R188_LAZIM", "SPEC-187")
        return _TABEEI, "R180_TABEEI", "SPEC-180"

    for i in range(n):
        if out[i].kind != "madd":
            continue
        length, rule_id, spec = classify(i)
        # R181 provenance refinement: hamza + vowel + madd = badal ({2},
        # same class; the rule_index distinction matters for grading).
        if (rule_id == "R180_TABEEI" and i >= 2
                and out[i - 1].kind == "vowel"
                and out[i - 2].kind == "consonant"
                and out[i - 2].base is Base.HAMZA):
            rule_id = "R181_BADAL"
        app = RuleApp(rule_id, spec, out[i].src_span)
        trace.append(app)
        out[i] = _replace(out[i], length=length,
                          provenance=out[i].provenance + (app,))

    # Pausal glide (R180): a final yeh/waw that took 'arid iskan after its OWN
    # quality vowel becomes a plain madd letter at waqf (فَنَسِيَ -> nasii).
    # NOT aared — aared needs a consonant AFTER the madd; here nothing follows.
    if (n >= 2 and out[-1].kind == "consonant"
            and out[-1].base in (Base.YEH, Base.WAW)
            and not out[-1].geminated
            and out[-1].src_span in arid_spans
            and out[-2].kind == "vowel"
            and ((out[-1].base is Base.YEH and out[-2].base is Base.KASRA)
                 or (out[-1].base is Base.WAW and out[-2].base is Base.DAMMA))):
        p = out[-1]
        app = RuleApp("R180_PAUSAL_GLIDE", "SPEC-180", p.src_span)
        trace.append(app)
        madd_base = Base.YEH_MADD if p.base is Base.YEH else Base.WAW_MADD
        out[-1] = _replace(
            p, base=madd_base, kind="madd", length=_TABEEI,
            provenance=p.provenance + (app,))

    # Leen (R190): consonant waw/yeh, sakin, after a fatha, before the final
    # sakin — 'arid final -> {2,4,6}; asli final (the 'ayn letter-name) -> {4,6}.
    for i in range(n):
        p = out[i]
        if p.kind != "consonant" or p.base not in (Base.WAW, Base.YEH):
            continue
        if p.geminated or p.ghunna is not None:
            continue
        if not (i > 0 and out[i - 1].kind == "vowel" and out[i - 1].base is Base.FATHA):
            continue
        if not is_sakin_at(i):
            continue
        j = i + 1
        if j >= n:
            continue
        nxt = out[j]
        nxt_sakin_or_mukhfah = (is_sakin_at(j)
                                or nxt.base in (Base.NOON_MUKHFAH, Base.MEEM_MUKHFAH))
        if not nxt_sakin_or_mukhfah:
            continue
        if j == n - 1 and nxt.src_span in arid_spans:
            length = _free({2, 4, 6}, min(config.madd_leen_len, config.madd_aared_len),
                           {2, 3, 4, 5, 6})
            rule_id = "R190_LEEN"
        else:
            # asli sakin (or an ikhfa carrier holding the 'ayn-name junction):
            # مد لين لازم حرفي مخفف of عين — Shatibiyyah wajhan {4,6},
            # ishba' 6 muqaddam (الشاطبية بيت 177 «والطول فضلا»; النشر 1:348;
            # هداية القاري 1:343 «الإشباع هو الأفضل والمقدم»). Scoring covers
            # the three madhahib of al-Nashr incl. Tayyibah qasr.
            length = _free({4, 6}, config.madd_ain_len, {2, 4, 6})
            rule_id = "R188_AIN_LEEN_LAZIM"
        app = RuleApp(rule_id, "SPEC-190", p.src_span)
        trace.append(app)
        out[i] = _replace(p, length=length, provenance=p.provenance + (app,))
    return out
