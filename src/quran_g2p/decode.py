"""P1 orthographic decoder: cluster stream -> OrthoSeg stream (SPEC-002).

Per-edition mark tables, one shared output language. Fail-closed: any cluster
shape outside the decode tables raises DecodeError with the site — unknown
orthography is investigated and specified, never skipped.

v1 scope: letters, vowel states (incl. KFGQPC open tanween), sukun/silent
conventions, madd-letter resolution, dagger alif, small waw/yeh, floating
hamza segments, iqlab witnesses, pause-mark/ornament skipping. Special-word
seen/sad marks and imala/ishmam/tasheel site marks pass through untouched
here; the P13 one-off rules own them (they are per-site, not conventions).
"""
from __future__ import annotations

from dataclasses import dataclass

from . import codepoints as cp
from .cluster import SEGMENT_CARRIERS, Cluster, cluster
from .ir import Base
from .ortho import (
    ConsSeg,
    DecodeError,
    DecodeResult,
    MaddSeg,
    MaddSource,
    SukunKind,
    Tanween,
    TanweenMode,
    VQ,
)

_PLAIN_CONS = {
    cp.BEH: Base.BEH, cp.TEH: Base.TEH, cp.THEH: Base.THEH, cp.JEEM: Base.JEEM,
    cp.HAH: Base.HAH, cp.KHAH: Base.KHAH, cp.DAL: Base.DAL, cp.THAL: Base.THAL,
    cp.REH: Base.REH, cp.ZAIN: Base.ZAIN, cp.SEEN: Base.SEEN, cp.SHEEN: Base.SHEEN,
    cp.SAD: Base.SAD, cp.DAD: Base.DAD, cp.TAH: Base.TAH, cp.ZAH: Base.ZAH,
    cp.AIN: Base.AIN, cp.GHAIN: Base.GHAIN, cp.FEH: Base.FEH, cp.QAF: Base.QAF,
    cp.KAF: Base.KAF, cp.LAM: Base.LAM, cp.MEEM: Base.MEEM, cp.NOON: Base.NOON,
    cp.HEH: Base.HEH,
}

_HAMZA_SEATS = {
    cp.HAMZA: "line",
    cp.ALEF_WITH_HAMZA_ABOVE: "alef",
    cp.WAW_WITH_HAMZA_ABOVE: "waw",
    cp.ALEF_WITH_HAMZA_BELOW: "alef_below",
    cp.YEH_WITH_HAMZA_ABOVE: "yeh",
}

_VOWELS = {cp.FATHA: VQ.A, cp.DAMMA: VQ.U, cp.KASRA: VQ.I}

# Tanween tables per edition. Tanzil: unified forms, mode PLAIN.
# KFGQPC: closed forms = IZHAR (izhar or pre-pause); open forms = OPEN
# (idgham/ikhfa follows) — quality mapping verified against 2:2/2:5/2:7/2:10/
# 2:17/2:19/2:20 (SPEC-002).
_TANWEEN = {
    "tanzil": {
        cp.FATHATAN: (VQ.A, TanweenMode.PLAIN),
        cp.DAMMATAN: (VQ.U, TanweenMode.PLAIN),
        cp.KASRATAN: (VQ.I, TanweenMode.PLAIN),
    },
    "kfgqpc": {
        cp.FATHATAN: (VQ.A, TanweenMode.IZHAR),
        cp.DAMMATAN: (VQ.U, TanweenMode.IZHAR),
        cp.KASRATAN: (VQ.I, TanweenMode.IZHAR),
        cp.INVERTED_DAMMA: (VQ.A, TanweenMode.OPEN),
        cp.FATHA_WITH_TWO_DOTS: (VQ.U, TanweenMode.OPEN),
        cp.SUBSCRIPT_ALEF: (VQ.I, TanweenMode.OPEN),
    },
}

# Sukun / silent-letter conventions per edition (SPEC-001 delta table).
_SUKUN_MARK = {"tanzil": cp.SUKUN, "kfgqpc": cp.SMALL_HIGH_DOTLESS_HEAD_OF_KHAH}
_SILENT_MARK = {"tanzil": cp.SMALL_HIGH_ROUNDED_ZERO, "kfgqpc": cp.SUKUN}

_IQLAB_MARKS = {cp.SMALL_HIGH_MEEM_ISOLATED_FORM, cp.SMALL_LOW_MEEM}
_MADDA_MARKS = {cp.MADDAH_ABOVE, cp.SMALL_HIGH_MADDA}

# Annotations that decode to nothing (pause marks, sajdah, ayah ornaments,
# rare site marks owned by P13 rules).
_IGNORED_MARKS = {
    cp.SMALL_HIGH_LIGATURE_SAD_WITH_LAM_WITH_ALEF_MAKSURA,
    cp.SMALL_HIGH_LIGATURE_QAF_WITH_LAM_WITH_ALEF_MAKSURA,
    cp.SMALL_HIGH_MEEM_INITIAL_FORM,
    cp.SMALL_HIGH_JEEM,
    cp.SMALL_HIGH_THREE_DOTS,
    cp.SMALL_HIGH_SEEN, cp.SMALL_LOW_SEEN,
    cp.EMPTY_CENTRE_LOW_STOP, cp.EMPTY_CENTRE_HIGH_STOP,
    cp.ROUNDED_HIGH_STOP_WITH_FILLED_CENTRE,
}

_WORD_BREAK_BASES = {cp.SPACE, cp.NO_BREAK_SPACE}
_ORNAMENT_BASES = {cp.START_OF_RUB_EL_HIZB, cp.PLACE_OF_SAJDAH}


_WAQF_ONLY_MARK = cp.SMALL_HIGH_UPRIGHT_RECTANGULAR_ZERO


@dataclass
class _SegBuilder:
    kind: str                     # "letter" | "hamza" | "small_waw" | "small_yeh" | "small_high_yeh" | "small_noon"
    letter_cp: str | None
    span: tuple[int, int]
    vowel: VQ | None = None
    tanween: Tanween | None = None
    sukun_marked: bool = False
    shadda: bool = False
    silent: bool = False
    madda: bool = False
    iqlab: bool = False
    waqf_only: bool = False
    dagger_at: int | None = None


def decode_text(text: str, edition: str) -> DecodeResult:
    return decode(cluster(text), edition, text)


def decode(clusters: list[Cluster], edition: str, text: str) -> DecodeResult:
    segs: list = []
    word = 0
    started_word = False
    prev_vq: VQ | None = None      # vowel context for bare madd letters

    def site(c: Cluster) -> str:
        lo = max(0, c.span[0] - 8)
        hi = min(len(text), c.span[1] + 8)
        return f"…{text[lo:hi]}… span={c.span} cps=" + " ".join(
            f"U+{ord(x):04X}" for x in text[c.span[0]:c.span[1]]
        )

    for ci, c in enumerate(clusters):
        if c.base in _WORD_BREAK_BASES:
            if started_word:
                word += 1
                started_word = False
            prev_vq = None
            continue
        if c.base in _ORNAMENT_BASES:
            continue

        builders = _split_builders(c, edition, site)
        # Seat-dagger, cross-cluster form (فَادَّارَأْتُمْ 2:72): a dagger
        # WITHOUT a madda witness whose next cluster is a line-hamza with
        # sukun is the hamza's chair (سرج الهمزة) — written, never pronounced.
        # (The in-cluster combining-hamza form is handled in _split_builders.)
        prim = builders[0]
        if (prim.dagger_at is not None and not prim.madda
                and ci + 1 < len(clusters)):
            nc = clusters[ci + 1]
            if (nc.base == cp.HAMZA
                    and _SUKUN_MARK[edition] in nc.marks):
                prim.dagger_at = None
        for b in builders:
            emitted = _emit(b, c, edition, word, prev_vq, site)
            for seg in emitted:
                segs.append(seg)
                if isinstance(seg, ConsSeg):
                    prev_vq = seg.vowel or (seg.tanween.quality if seg.tanween else None)
                else:
                    prev_vq = seg.quality
            if emitted:
                started_word = True

    return DecodeResult(segs=segs, n_words=word + (1 if started_word else 0))


def _split_builders(c: Cluster, edition: str, site) -> list[_SegBuilder]:
    """Partition a cluster's marks into the primary segment and carrier segments."""
    kinds = {
        cp.HAMZA_ABOVE: "hamza", cp.HAMZA_BELOW: "hamza",
        cp.SMALL_WAW: "small_waw", cp.SMALL_YEH: "small_yeh",
        cp.SMALL_HIGH_YEH: "small_high_yeh", cp.SMALL_HIGH_NOON: "small_noon",
    }
    # The primary segment SPANS its whole cluster up to the first carrier
    # mark: its vowel/tanween/dabt marks are part of it (coverage honesty —
    # a tanween noon inherits the span that includes the tanween sign).
    first_carrier = None
    for k, m in enumerate(c.marks):
        if m in SEGMENT_CARRIERS:
            first_carrier = c.span[0] + 1 + k
            break
    primary_end = first_carrier if first_carrier is not None else c.span[1]
    primary = _SegBuilder(kind="letter", letter_cp=c.base, span=(c.span[0], primary_end))
    builders = [primary]
    cur = primary
    for k, m in enumerate(c.marks):
        pos = c.span[0] + 1 + k
        if m in SEGMENT_CARRIERS:
            cur = _SegBuilder(kind=kinds[m], letter_cp=None, span=(pos, c.span[1]))
            builders.append(cur)
            continue
        _apply_mark(cur, m, pos, edition)
    # A dagger alif immediately preceding a combining-hamza segment in the
    # same cluster is the hamza's SEAT (سرج الهمزة، صورة الهمزة) — written,
    # never pronounced. Sole corpus site: فَادَّارَأْتُمْ 2:72, where the
    # spoken form is fa-ddaa-RA'-tum with a PLAIN fatha on the reh (Dalil
    # al-Hayran 1:415; Ward al-Taif 1:230; al-Qastallani, Lataif 2:216).
    if primary.dagger_at is not None:
        for k, m in enumerate(c.marks):
            pos = c.span[0] + 1 + k
            if pos == primary.dagger_at + 1 and m in (cp.HAMZA_ABOVE, cp.HAMZA_BELOW):
                primary.dagger_at = None
                break
    return builders


def _apply_mark(b: _SegBuilder, m: str, pos: int, edition: str) -> None:
    if m in _VOWELS:
        b.vowel = _VOWELS[m]
    elif m in _TANWEEN[edition]:
        q, mode = _TANWEEN[edition][m]
        b.tanween = Tanween(q, mode)
    elif m == _SUKUN_MARK[edition]:
        b.sukun_marked = True
    elif m == _SILENT_MARK[edition]:
        b.silent = True
    elif m == cp.SHADDA:
        b.shadda = True
    elif m in _MADDA_MARKS:
        b.madda = True
    elif m in _IQLAB_MARKS:
        b.iqlab = True
    elif m == cp.SUPERSCRIPT_ALEF:
        b.dagger_at = pos
    elif m == _WAQF_ONLY_MARK:
        b.waqf_only = True
    elif m == cp.TATWEEL:
        pass  # transparent extender (see cluster.MARKS)
    elif m in _IGNORED_MARKS:
        pass
    else:  # pragma: no cover - fail-closed on anything unclassified
        raise DecodeError(f"unhandled mark U+{ord(m):04X} in {edition}")


def _emit(b: _SegBuilder, c: Cluster, edition: str, word: int, prev_vq: VQ | None, site) -> list:
    out: list = []
    if b.silent:
        # Silent letter: contributes nothing (dagger on a silent seat would be
        # a contradiction; fail if seen).
        if b.dagger_at is not None:
            raise DecodeError(f"dagger on silent letter at {site(c)}")
        return out

    if b.kind == "letter":
        out.extend(_emit_letter(b, c, edition, word, prev_vq, site))
    elif b.kind == "hamza":
        out.append(_cons(b, Base.HAMZA, word, carrier="floating"))
    elif b.kind == "small_waw":
        out.append(_madd_or_cons(b, VQ.U, MaddSource.SMALL_WAW, Base.WAW, word))
    elif b.kind == "small_yeh":
        out.append(_madd_or_cons(b, VQ.I, MaddSource.SMALL_YEH, Base.YEH, word))
    elif b.kind == "small_high_yeh":
        # voweled small-high-yeh is a consonant yaa (نُحْـِۧي class), like the
        # other small carriers; bare = the Ibrahim-type madd.
        out.append(_madd_or_cons(b, VQ.I, MaddSource.SMALL_HIGH_YEH, Base.YEH, word))
    elif b.kind == "small_noon":
        out.append(ConsSeg(Base.NOON, None, None, SukunKind.BARE, False, None,
                           b.madda, b.iqlab, b.span, word))
    # dagger alif emits after its host segment
    if b.dagger_at is not None:
        out.append(MaddSeg(VQ.A, MaddSource.DAGGER_ALEF, b.madda,
                           (b.dagger_at, b.dagger_at + 1), word))
    return out


def _emit_letter(b: _SegBuilder, c: Cluster, edition: str, word: int,
                 prev_vq: VQ | None, site) -> list:
    ch = b.letter_cp
    has_vstate = b.vowel is not None or b.tanween is not None or b.sukun_marked

    # Seat rule (SPEC-002): a bare waw/yeh/alef/maksura is a silent hamza seat
    # ONLY when the combining hamza is its FIRST mark (KFGQPC تِلۡقَآيِٕ). If
    # madda/vowel marks precede the carrier, the letter is real and the hamza
    # is a separate floating segment (خَطِيٓـَٔتُهُ: yeh is the madd letter).
    if (not has_vstate and b.dagger_at is None
            and ch in (cp.WAW, cp.YEH, cp.ALEF, cp.ALEF_MAKSURA)
            and c.marks and c.marks[0] in (cp.HAMZA_ABOVE, cp.HAMZA_BELOW)):
        return []

    if ch in _PLAIN_CONS:
        return [_cons(b, _PLAIN_CONS[ch], word)]
    if ch in _HAMZA_SEATS:
        if not has_vstate and b.madda:
            # KFGQPC أٓ: hamza seat + madda, no haraka, no separate alef ≡
            # Tanzil ءَا (hamza+fatha+alef). Decode to HAMZA(a) + madd(a).
            hamza = ConsSeg(Base.HAMZA, VQ.A, None, None, b.shadda,
                            _HAMZA_SEATS[ch], True, b.iqlab, b.span, word)
            return [hamza, MaddSeg(VQ.A, MaddSource.PLAIN_ALEF, True, b.span, word)]
        return [_cons(b, Base.HAMZA, word, carrier=_HAMZA_SEATS[ch])]
    if ch == cp.ALEF_WASLA:
        # Hamzat wasl has no vowel state of its own: it is resolved at ibtida'
        # (P3) or elided in wasl (P5) — the BARE-consonant default is wrong here.
        return [_cons(b, Base.HAMZAT_WASL, word, bare_default=False)]
    if ch == cp.TEH_MARBUTA:
        return [_cons(b, Base.TEH_MARBUTA, word)]
    if ch == cp.WAW:
        if has_vstate:
            return [_cons(b, Base.WAW, word)]
        if b.dagger_at is not None:
            return []  # waw is a silent seat for the dagger alif (e.g. الصلوٰة)
        if prev_vq is VQ.U:
            return [MaddSeg(VQ.U, MaddSource.BARE_WAW, b.madda, b.span, word)]
        if prev_vq is VQ.A:
            # Leen waw left bare = assimilated into a following waw
            # (KFGQPC عَصَوا۟ وَّ… class; SPEC-002 finding).
            return [_cons(b, Base.WAW, word)]
        raise DecodeError(f"bare waw with prev={prev_vq} at {site(c)}")
    if ch == cp.YEH:
        if has_vstate:
            return [_cons(b, Base.YEH, word)]
        if b.dagger_at is not None:
            return []  # yeh seat for dagger alif
        if prev_vq is VQ.I:
            return [MaddSeg(VQ.I, MaddSource.BARE_YEH, b.madda, b.span, word)]
        if prev_vq is VQ.A:
            # Leen yeh left bare = assimilated (mirror of the waw case).
            return [_cons(b, Base.YEH, word)]
        if prev_vq is None:
            # Word-initial bare yeh occurs exactly twice in the corpus — the
            # muqatta'at letter-names in 19:1 (كهيعص) and 36:1 (يس). Emit a
            # BARE consonant; R011 owns the spell-out.
            return [_cons(b, Base.YEH, word)]
        raise DecodeError(f"bare yeh with prev={prev_vq} at {site(c)}")
    if ch == cp.ALEF_MAKSURA:
        if has_vstate:
            # Tanzil writes consonant yaa dotless (شَىْءٍ, هِىَ, أَىِّ):
            # a maksura with any vowel state is a plain consonant YEH.
            return [_cons(b, Base.YEH, word)]
        if b.dagger_at is not None:
            return []  # maksura seat for dagger alif (عَلَىٰ)
        if prev_vq is VQ.I:
            return [MaddSeg(VQ.I, MaddSource.ALEF_MAKSURA, b.madda, b.span, word)]
        if prev_vq is VQ.A:
            return [MaddSeg(VQ.A, MaddSource.ALEF_MAKSURA, b.madda, b.span, word)]
        raise DecodeError(f"bare alef maksura with prev={prev_vq} at {site(c)}")
    if ch == cp.ALEF:
        if has_vstate:
            raise DecodeError(f"alef with vowel state at {site(c)}")
        if b.dagger_at is not None:
            return []  # alef seat carrying explicit dagger
        return [MaddSeg(VQ.A, MaddSource.PLAIN_ALEF, b.madda, b.span, word,
                        waqf_only=b.waqf_only)]
    raise DecodeError(f"unhandled letter U+{ord(ch):04X} at {site(c)}")


def _cons(b: _SegBuilder, base: Base, word: int, carrier: str | None = None,
          bare_default: bool = True) -> ConsSeg:
    vowel, tanween = b.vowel, b.tanween
    # Iqlab canonicalization (SPEC-002): both editions mark iqlab with a small
    # meem; Tanzil keeps the tanween form (tanween+meem), KFGQPC reduces it to
    # a single haraka (haraka+meem). Canonical state: Tanween(quality, IQLAB).
    if b.iqlab:
        if tanween is not None:
            tanween = Tanween(tanween.quality, TanweenMode.IQLAB)
        elif vowel is not None:
            tanween = Tanween(vowel, TanweenMode.IQLAB)
            vowel = None
        # bare letter + iqlab mark = noon-sakinah iqlab: no tanween involved.
    sukun = SukunKind.MARKED if b.sukun_marked else None
    if bare_default and vowel is None and tanween is None and not b.sukun_marked:
        sukun = SukunKind.BARE
    return ConsSeg(base, vowel, tanween, sukun, b.shadda, carrier,
                   b.madda, b.iqlab, b.span, word)


def _madd_or_cons(b: _SegBuilder, q: VQ, src: MaddSource, cons_base: Base, word: int):
    if b.vowel is not None or b.tanween is not None or b.sukun_marked:
        return _cons(b, cons_base, word)
    return MaddSeg(q, src, b.madda, b.span, word)
