"""R012 — seen/sad khilaf words (SPEC-012).

Written saad, recited seen at 2:245 and 7:69 (Hafs/Shatibiyyah mashhur, small
seen mark as witness); 52:37 saad muqaddam (mark records the option); 88:22
plain saad. Config knobs flip each site.
"""
from quran_g2p.config import HafsConfig
from quran_g2p.ir import Base
from quran_g2p.ortho import ConsSeg
from quran_g2p.pipeline import run
from quran_g2p.textbank import AyahRef, TextBank


def letters(ctx):
    return [s.letter for s in ctx.segs if isinstance(s, ConsSeg)]


def run_ref(ref, edition="tanzil", config=None):
    tb = TextBank.load(edition)
    return run(tb.ayah(ref), edition=edition, ref=ref, config=config or HafsConfig())


def test_2_245_yabsut_recited_with_seen_both_editions():
    for ed in ("tanzil", "kfgqpc"):
        ls = letters(run_ref(AyahRef(2, 245), ed))
        assert Base.SEEN in ls, ed
        assert Base.SAD not in ls, ed  # 2:245 has no other saad word


def test_7_69_bastatan_recited_with_seen():
    ls = letters(run_ref(AyahRef(7, 69)))
    assert Base.SEEN in ls


def test_52_37_musaytirun_keeps_sad_by_default():
    ls = letters(run_ref(AyahRef(52, 37)))
    assert Base.SAD in ls


def test_config_flip_restores_sad_at_2_245():
    cfg = HafsConfig(bast_2_245_seen=False)
    ls = letters(run_ref(AyahRef(2, 245), config=cfg))
    assert Base.SAD in ls


def test_88_22_musaytir_untouched():
    ls = letters(run_ref(AyahRef(88, 22)))
    assert Base.SAD in ls
