"""TextBank: pinned, fail-closed loading of the vendored Quran text editions.

Assertions use numeric codepoints, never hand-typed Arabic literals: hand-typed
Arabic has already produced false test failures in this project's history
(U+0622 vs decomposed forms), and the whole repo bans Arabic literals outside
codepoints.py.
"""
import shutil
from pathlib import Path

import pytest

from quran_g2p.textbank import AyahRef, PinnedTextError, TextBank

REPO_DATA = Path(__file__).resolve().parents[1] / "data"


def test_tanzil_loads_all_6236_ayat():
    tb = TextBank.load("tanzil")
    assert tb.n_ayat == 6236
    assert tb.edition == "tanzil"


def test_tanzil_1_1_starts_with_bismi_codepoints():
    tb = TextBank.load("tanzil")
    text = tb.ayah(AyahRef(1, 1))
    # ب ِ س ْ م ِ  = BEH, KASRA, SEEN, SUKUN(U+0652), MEEM, KASRA
    assert [ord(c) for c in text[:6]] == [0x628, 0x650, 0x633, 0x652, 0x645, 0x650]


def test_tanzil_last_ayah_ref_is_114_6():
    tb = TextBank.load("tanzil")
    refs = list(tb.refs())
    assert refs[0] == AyahRef(1, 1)
    assert refs[-1] == AyahRef(114, 6)
    assert len(refs) == 6236


def test_kfgqpc_loads_6236_and_strips_ayah_number_suffix():
    tb = TextBank.load("kfgqpc")
    assert tb.n_ayat == 6236
    text = tb.ayah(AyahRef(1, 1))
    # The raw field ends with NBSP + Arabic-Indic digit(s); both must be stripped.
    assert "\xa0" not in text
    assert not any(0x660 <= ord(c) <= 0x669 for c in text)
    # Still starts with BEH + KASRA + SEEN (sukun codepoint differs by edition on char 4).
    assert [ord(c) for c in text[:3]] == [0x628, 0x650, 0x633]


def test_tampered_file_fails_closed(tmp_path):
    src = REPO_DATA / "tanzil-uthmani.txt"
    dst_dir = tmp_path
    dst = dst_dir / "tanzil-uthmani.txt"
    shutil.copy(src, dst)
    with open(dst, "a", encoding="utf-8") as f:
        f.write("tampered\n")
    with pytest.raises(PinnedTextError):
        TextBank.load("tanzil", data_dir=dst_dir)


def test_unknown_edition_rejected():
    with pytest.raises(ValueError):
        TextBank.load("warsh")


def test_tanzil_basmala_stripped_from_surah_initial_ayat():
    # Tanzil embeds the basmala in every surah's first ayah except 1 and 9;
    # canonical ayah numbering (and KFGQPC) exclude it. The loader strips it.
    tb = TextBank.load("tanzil")
    basmala = tb.ayah(AyahRef(1, 1))
    assert not tb.ayah(AyahRef(2, 1)).startswith(basmala)
    assert not tb.ayah(AyahRef(114, 1)).startswith(basmala)
    # 1:1 IS the basmala; 9:1 legitimately has none and keeps its own text
    assert tb.ayah(AyahRef(1, 1)) == basmala
    assert len(tb.ayah(AyahRef(2, 1))) < 12  # الم only

