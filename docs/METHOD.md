# How every ruling got here

The pipeline behind each entry in the [rulings register](RULINGS-REGISTER.md),
so a reader can weigh the work rather than take it on trust.

1. **Indexed from the books.** Machine-assisted passes read the classical
   literature page by page (the Shamela prints of the Shatibiyyah and
   its commentaries, al-Nashr, al-Taysir, Hidayat al-Qari, and the rest
   of the bibliography) and indexed every candidate ruling. The index
   is a card catalogue, not an authority: nothing enters the engine on a
   model's word.
2. **Page-verified citations.** Every citation in the rulings register
   is checked against the printed texts themselves: the cited book must
   exist in the corpus, the cited volume:page or bayt must exist in that
   print, and the ruling's subject must appear at that location. Quoted
   matn lines are verified verbatim. The audit is committed at
   `docs/CITATION-AUDIT.md` and regenerable with
   `tools/audit_citations.py`.
3. **A gate-enforced register.** Each engine rule is bound to its
   classical citation and its review rows (`docs/RULINGS-REGISTER.md`);
   the engine refuses to even import if a rule lacks either. Five
   independent oracles, corpus-wide behavioral audits, and seeded-bug
   drills prove the engine implements the register faithfully.
4. **Blinded sanad review, measured rather than assumed, and now
   complete.** An ijazah-holding hafiz (sanad in Hafs 'an 'Asim) ruled
   on all 208 entries from his own talaqqi: **191 confirmed, 17
   confirmed while documenting a second transmitted wajh, zero rulings
   judged wrong.** His independence was measured: in the blind
   screening, deliberately planted errors dressed in the real citation
   format were all caught. Every disagreement raised along the way was
   adjudicated against the cited passages, on the public record
   (`docs/ADJUDICATIONS.md`), and the final tally is generated live
   from the review sheet below.
5. **Sealed at the top of the discipline, twice.** The complete
   register then underwent formal scholarly arbitration (تحكيم علمي)
   by two serving professors of Qira'at at Umm al-Qura University in
   Makkah, the city where the revelation began, each engaged
   separately and blind to every other reviewer and his verdicts. The
   first ruled on all 208 entries from what he received before his own
   teachers and shaykhs («وفق ما تلقيته وقرأته على أساتذتي ومشايخي»,
   his words) and confirmed the register. The second ruled on every
   row of the full instrument, and his independence was measured the
   same way as the first reviewer's: every deliberately planted error
   embedded in his copy was caught and refuted with the classical nass
   cited back. Not one of his notes overturned a phonetic ruling; each
   was folded into the register in his own words. Both are credited by
   rank alone: the work needed their judgment, not their names. Three
   unbroken chains have now examined every ruling independently, and all
   three reached the same answer.
6. **The method is the tradition's own.** الرواية والدراية:
   transmission and verification, at last given machinery. Ibn
   al-Jazari built al-Nashr exactly this way: every written source
   gathered, every reading verified through living chains, nothing
   accepted without both. This project does not argue with that method.
   It implements it. The books give exhaustiveness, the sanad gives
   authority, and the gates let neither stand alone.

**Scope of authority.** The engine rules on text, not on people.
Certifying reciters remains the sanad's work, and learning the Quran
still happens at the mouths of scholars; this project is built to serve
that transmission, not to sit above it. Where it could err, it shows its
sources and its live review, so correction always has a public path.
