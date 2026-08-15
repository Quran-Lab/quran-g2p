"""Corpus invariant: derived tanween treatment vs KFGQPC dabt witnesses
(R021 / SPEC-002 — "derive phonologically, then assert against the dabt").

KFGQPC encodes every tanween's fate in its written form: closed = izhar (or
pausal position), open = idgham/ikhfa follows, haraka+meem = iqlab. The P6
rules must reproduce that verdict at every witnessed site, with pausal
position (the tanween word ends the segment; witnesses describe wasl into
the next ayah) as the one systematic exemption.
"""
from quran_g2p.ortho import ConsSeg, TanweenMode
from quran_g2p.phonemize import phonemize
from quran_g2p.pipeline import run as prun
from quran_g2p.textbank import TextBank

P6_RULES = {
    "R140_IZHAR_HALQI", "R141_IDGHAM_GHUNNA", "R142_IDGHAM_BILA_GHUNNA",
    "R143_IQLAB", "R144_IKHFA", "R131_NOON_WIQAYA", "R141_IZHAR_MUTLAQ",
}


def test_tanween_dabt_agreement_whole_corpus():
    tb = TextBank.load("kfgqpc")
    violations = []
    for ref in tb.refs():
        text = tb.ayah(ref)
        res = phonemize(text, edition="kfgqpc", ref=ref)
        span2rules = {}
        for app in res.trace:
            if app.rule_id in P6_RULES:
                span2rules.setdefault(app.trigger_span, set()).add(app.rule_id)
        ctx = prun(text, edition="kfgqpc", ref=ref)
        cons = [s for s in ctx.segs if isinstance(s, ConsSeg)]
        last_cons_span = cons[-1].span if cons else None
        for seg in ctx.segs:
            if not isinstance(seg, ConsSeg) or seg.tanween is None:
                continue
            fired = span2rules.get(seg.span, set())
            pausal = seg.span == last_cons_span
            mode = seg.tanween.mode
            if mode is TanweenMode.IZHAR:
                ok = fired <= {"R140_IZHAR_HALQI", "R131_NOON_WIQAYA"}
            elif mode is TanweenMode.OPEN:
                ok = pausal or bool(fired & {
                    "R141_IDGHAM_GHUNNA", "R142_IDGHAM_BILA_GHUNNA", "R144_IKHFA"})
            elif mode is TanweenMode.IQLAB:
                ok = pausal or "R143_IQLAB" in fired
            else:
                continue
            if not ok:
                violations.append((f"{ref.surah}:{ref.ayah}", mode.value, sorted(fired)))
                if len(violations) > 12:
                    break
    assert not violations, violations
