"""Label text (oracle.expand) joins two words only across a cross-word
assimilation, never at a sun-letter article.

Two regressions this pins, both silent in every other gate because the token
stream was untouched:
  * full attribution (a16d59f) put R133 on the article lam of ٱللَّهِ, and
    the expander read any R133 as a cross-word idgham: "bismi llaahi" became
    one word in 3,440 ayat;
  * naqis idgham got its own id (R141_IDGHAM_GHUNNA_NAQIS) and the expander's
    list was never told, so tanween into waw/yeh stopped joining (2,430 joins).
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT))

from oracle.expand import expand                  # noqa: E402
from quran_g2p.phonemize import phonemize         # noqa: E402
from quran_g2p.textbank import AyahRef, TextBank  # noqa: E402

TB = TextBank.load("tanzil")


def text(s, a):
    ref = AyahRef(s, a)
    (seg,) = phonemize(TB.ayah(ref), edition="tanzil", ref=ref).segments
    return expand(seg.phones)


def test_sun_letter_article_keeps_the_word_space():
    # bismi | llaahi | rrahmaani | rrahiim: four words, three spaces
    assert text(1, 1).count(" ") == 3


def test_cross_word_idgham_joins():
    t = text(2, 7)   # ghishaawatun wa-lahum: naqis idgham into waw joins
    assert "تُووو" in t      # ...tu + www, no space
    # qul lakum: lam into lam across the word boundary joins as "qullakum"
    assert "قُللَكُم" in text(2, 33)
