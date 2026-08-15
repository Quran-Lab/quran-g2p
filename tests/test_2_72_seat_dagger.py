"""2:72 فَادَّارَأْتُمْ — the seat-dagger ruling (DV-002 RESOLVED by sources).

The word's third written alif is the hamza's chair (سرج الهمزة), never
pronounced: fa-ddaa-RA'-tum with a plain fatha on the reh and the hamza
sakinah directly after it. Sources: Dalil al-Hayran 1:415 («التي بعد الراء
وهي صورة الهمزة»), Ward al-Taif 1:230 («الثالثة سرجٌ للهمزة الساكنة»),
al-Qastallani Lataif 2:216. Both prior engines were wrong here (ours
muttasil-4, the reference engine's phantom tabee'i-2); cpfair marks madd only on the dal's
alif, agreeing with the books.
"""
from quran_g2p.ir import Base
from quran_g2p.phonemize import phonemize
from quran_g2p.textbank import AyahRef, TextBank


def test_2_72_no_madd_after_the_reh():
    for edition in ("tanzil", "kfgqpc"):
        tb = TextBank.load(edition)
        ref = AyahRef(2, 72)
        (seg,) = phonemize(tb.ayah(ref), edition=edition, ref=ref).segments
        ph = seg.phones
        # locate the geminated dal of iddaara'tum
        i = next(k for k, p in enumerate(ph)
                 if p.base is Base.DAL and p.geminated)
        # d* a A r a ' t u m — madd ONLY after the dal; reh has plain fatha;
        # hamza sakinah follows the fatha directly
        assert ph[i + 1].base is Base.FATHA
        assert ph[i + 2].kind == "madd" and ph[i + 2].length.canonical == 2
        assert ph[i + 3].base is Base.REH
        assert ph[i + 4].base is Base.FATHA
        assert ph[i + 5].base is Base.HAMZA, edition
        assert ph[i + 6].base is Base.TEH  # hamza is sakin: no vowel between


def test_seat_dagger_suppression_is_unique_to_2_72():
    from quran_g2p import codepoints as cp
    from quran_g2p.cluster import cluster
    from quran_g2p.decode import _SUKUN_MARK
    for edition in ("tanzil", "kfgqpc"):
        tb = TextBank.load(edition)
        hits = []
        for ref in tb.refs():
            cs = cluster(tb.ayah(ref))
            for i, c in enumerate(cs):
                marks = list(c.marks)
                for k in range(len(marks) - 1):
                    if (marks[k] == cp.SUPERSCRIPT_ALEF
                            and marks[k + 1] in (cp.HAMZA_ABOVE, cp.HAMZA_BELOW)):
                        hits.append((ref.surah, ref.ayah))
                if (cp.SUPERSCRIPT_ALEF in marks and cp.MADDAH_ABOVE not in marks
                        and i + 1 < len(cs) and cs[i + 1].base == cp.HAMZA
                        and _SUKUN_MARK[edition] in cs[i + 1].marks):
                    hits.append((ref.surah, ref.ayah))
        assert hits == [(2, 72)], (edition, hits)
