"""Waqf-variant enumeration (plan A2 VariantPolicy; SPEC-123/183/184).

The canonical stream stops with pure sukun. This module surfaces the
other transmitted realizations as tagged alternates, per segment:

- rawm: the dropped haraka returns as a partial vowel (damm/kasr classes
  only, five-sanf exclusions per `waqf.isharah_modes`); the 'aared madd
  reverts to qasr and the final letter loses its qalqalah (it is no
  longer fully sakin).
- ishmam: the sukun phones unchanged, the final letter tagged with the
  visual lip-rounding (damm class only).
- site wajhs: ta'manna ikhtilas (12:11), salasila ithbat (76:4),
  aataani hadhf (27:36) — the config-flip alternates, tagged.

Ambiguity is enumerated, never averaged; every variant carries its rule
provenance.
"""
from __future__ import annotations

from dataclasses import dataclass, replace as _replace

from .config import HafsConfig
from .ir import Base, LengthSpec, Phone, RuleApp
from .textbank import AyahRef
from .waqf import WaqfSpec, isharah_modes

_QASR = LengthSpec(kind="fixed", allowed=frozenset({2}), canonical=2,
                   scoring=frozenset({2}))

_HARAKA = {"a": Base.FATHA, "u": Base.DAMMA, "i": Base.KASRA}


@dataclass(frozen=True)
class WaqfVariant:
    mode: str                 # "sukun" | "rawm" | "ishmam"
    phones: tuple[Phone, ...]
    tags: tuple[str, ...] = ()


def _iskan_info(seg_phones, trace):
    """(haraka Base | None, ta_marbuta, pronoun_haa) for the final word,
    recovered from the P4 rule notes whose spans sit inside that word."""
    if not seg_phones:
        return None, False, False
    word = seg_phones[-1].word_index
    spans = [p.src_span for p in seg_phones if p.word_index == word]
    lo = min(s[0] for s in spans)
    hi = max(max(s) for s in spans)

    def in_word(app):
        return lo <= app.trigger_span[0] <= hi

    haraka = None
    ta_marbuta = False
    pronoun = False
    for app in trace:
        if not in_word(app):
            continue
        if app.rule_id == "R122_TAA_MARBUTA_WAQF":
            ta_marbuta = True
        elif app.rule_id == "R183_SILAH_WAQF_DROP":
            pronoun = True
        elif app.rule_id == "R120_ISKAN" and app.note:
            for prefix in ("iskan:", "tanween:", "silah:"):
                if app.note.startswith(prefix):
                    haraka = _HARAKA.get(app.note[len(prefix):])
    if not pronoun and seg_phones[-1].base is Base.HEH:
        prev = seg_phones[-2] if len(seg_phones) > 1 else None
        if prev is not None and prev.kind in ("vowel", "madd"):
            # conservative: a final haa after a vowel or madd is treated
            # as the pronoun (withholds isharah, never emits it illegally)
            pronoun = True
    return haraka, ta_marbuta, pronoun


def _rawm(seg_phones, haraka):
    word = seg_phones[-1].word_index
    app = RuleApp("R123_RAWM", "SPEC-123", seg_phones[-1].src_span)
    out = []
    for p in seg_phones:
        if p.word_index == word and p.length is not None \
                and p.length.kind == "free" and 2 in p.length.allowed:
            p = _replace(p, length=_QASR, provenance=p.provenance + (app,))
        out.append(p)
    # the final letter is no longer fully sakin: qalqalah off
    out[-1] = _replace(out[-1], qalqalah=None,
                       provenance=out[-1].provenance + (app,))
    out.append(Phone(base=haraka, kind="vowel", geminated=False, length=None,
                     ghunna=None, qalqalah=None,
                     tafkheem=out[-1].tafkheem, sakt_after=False,
                     pausal_role="rawm", provenance=(app,),
                     src_span=out[-1].src_span,
                     word_index=out[-1].word_index))
    return tuple(out)


def _ishmam(seg_phones):
    app = RuleApp("R123_ISHMAM", "SPEC-123", seg_phones[-1].src_span)
    out = list(seg_phones)
    out[-1] = _replace(out[-1], pausal_role="ishmam",
                       provenance=out[-1].provenance + (app,))
    return tuple(out)


def _taamanna_ikhtilas(seg_phones):
    """12:11: break the idgham, ikhtilas damma on the first noon (the
    wajh al-Marsafi prefers; the printed dabt's ishmam is canonical)."""
    app = RuleApp("R220B_TAAMANNA_IKHTILAS", "SPEC-013b", (0, 0))
    for i, p in enumerate(seg_phones):
        if p.base is Base.NOON and p.geminated:
            first = _replace(p, geminated=False, ghunna=None,
                             provenance=p.provenance + (app,))
            mukhtalasa = Phone(base=Base.DAMMA_MUKHTALASA, kind="consonant",
                               geminated=False, length=None, ghunna=None,
                               qalqalah=None, tafkheem=p.tafkheem,
                               sakt_after=False, pausal_role=None,
                               provenance=(app,), src_span=p.src_span,
                               word_index=p.word_index)
            second = _replace(p, geminated=False, ghunna=None,
                              provenance=p.provenance + (app,))
            return tuple(list(seg_phones[:i]) + [first, mukhtalasa, second]
                         + list(seg_phones[i + 1:]))
    return None


def enumerate_variants(text: str, edition: str, ref: AyahRef | None = None,
                       config: HafsConfig | None = None,
                       waqf: WaqfSpec | None = None
                       ) -> list[list[WaqfVariant]]:
    from .phonemize import phonemize
    config = config or HafsConfig()
    res = phonemize(text, edition=edition, ref=ref, config=config, waqf=waqf)

    per_segment: list[list[WaqfVariant]] = []
    for si, seg in enumerate(res.segments):
        variants = [WaqfVariant("sukun", tuple(seg.phones))]
        haraka, ta_marbuta, pronoun = _iskan_info(seg.phones, res.trace)
        if haraka is not None:
            prev = seg.phones[-2] if len(seg.phones) > 1 else None
            modes = isharah_modes(haraka, prev, pronoun_haa=pronoun,
                                  ta_marbuta=ta_marbuta)
            if "rawm" in modes:
                variants.append(WaqfVariant("rawm",
                                            _rawm(seg.phones, haraka)))
            if "ishmam" in modes:
                variants.append(WaqfVariant("ishmam", _ishmam(seg.phones)))

        if ref is not None:
            key = (ref.surah, ref.ayah)
            if key == (12, 11):
                alt = _taamanna_ikhtilas(seg.phones)
                if alt is not None:
                    variants.append(WaqfVariant("sukun", alt,
                                                ("taamanna_ikhtilas",)))
            final_word_ends_segment = bool(seg.phones)
            if key == (76, 4) and final_word_ends_segment \
                    and not config.salasila_waqf_alif \
                    and seg.phones[-1].base is Base.LAM:
                alt = phonemize(text, edition=edition, ref=ref, waqf=waqf,
                                config=_flip(config, salasila_waqf_alif=True)
                                ).segments[si].phones
                if alt and alt[-1].base is Base.ALEF_MADD:
                    variants.append(WaqfVariant("sukun", tuple(alt),
                                                ("salasila_ithbat",)))
            if key == (27, 36) and final_word_ends_segment \
                    and config.aataani_waqf_yaa \
                    and seg.phones[-1].base is Base.YEH_MADD:
                alt = phonemize(text, edition=edition, ref=ref, waqf=waqf,
                                config=_flip(config, aataani_waqf_yaa=False)
                                ).segments[si].phones
                if alt and alt[-1].base is Base.NOON:
                    variants.append(WaqfVariant("sukun", tuple(alt),
                                                ("aataani_hadhf",)))
        per_segment.append(variants)
    return per_segment


def _flip(config: HafsConfig, **kw) -> HafsConfig:
    from dataclasses import asdict
    d = asdict(config)
    d.update(kw)
    return HafsConfig(**d)
