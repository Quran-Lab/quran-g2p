# Note: maraatib al-tafkheem, and an external corpus that grades them

> **Outside the register.** Nothing in this file is a ruling, carries a rule
> id, or changes a phone. It records one external comparison and one open
> question about the *implementation* of a ruling that is already reviewed.
> The citations below that are not already in the register are **not
> page-verified** and must not be treated as if they were. Do not fold any of
> it into `registry.py` without putting it through review.

## What the register already says

`R210_ISTILA` (السبب: المقدمة الجزرية باب صفات الحروف؛ النويري 1:237-238) is
reviewed, and the grading is stated by the golden row `sup2-tafkheem-maratib`
(التمهيد لابن الجزري باب التفخيم؛ جهد المقل للمرعشي؛ هداية القاري 1:116-118),
which reads:

> مراتب التفخيم خمس على قولٍ مشهور؛ المفتوح وبعده ألف، فالمفتوح، فالمضموم،
> فالساكن (بحسب حركة ما قبله)، فالمكسور؛ وعلى القول الثاني هي أربع بإسقاط
> مرتبة الساكن لأن حكمه تبع لحركة ما قبله

So the register already carries both views: five ranks, and the second view of
four in which the sakin has no rank of its own because it follows the vowel
before it. `expert_reviewed: true`.

## The external comparison

`quran-ws/quran-tajweed` (rule corpus from `tajweed.quranpedia.net`, MIT
engine, CC BY data) publishes tafkheem grading as span annotations under two
named schools, ابن الجزري with five ranks and ابن الطحان الأندلسي with three.
On paper that is a wider schema than ours, since it attributes each ladder to
a school. As shipped it is narrower in what it delivers, and the gaps are
instructive rather than damaging:

| | their corpus |
|---|---|
| Jazarī rank 2 (مفتوح وليس بعده ألف) | `status: "disabled"`, 3,915 ayat unserved |
| Ibn al-Ṭaḥḥān, sakin after fath / damm / kasr | all three `disabled`; two match 0 ayat as written |
| scope | the seven isti'la letters only; راء, لام الجلالة and غنة الإخفاء carry no rank |
| propagation | the rank sits on the letter, not on the alif that follows it |

Their notation cannot express "fatha **not** followed by alif", which is why
rank 2 is off, and the three Ibn al-Ṭaḥḥān rules that are off are precisely
the ones carrying that school's distinctive claim: that a sakin isti'la letter
takes its rank from the **preceding** vowel. With those disabled, their
Ibn al-Ṭaḥḥān ladder reduces to the letter's own haraka and is no longer that
school's doctrine.

The observation worth keeping is therefore the opposite of the one it first
looks like. Our register states the preceding-vowel mechanism and theirs has
it turned off; what they have and we do not is the *attribution by name*,
which is a labelling convenience, not a ruling.

## The open question

`_p12_tafkheem.rank_of` in `src/quran_g2p/phonemize.py` returns rank 4 for
every sakin, unconditionally:

```python
if nv is None:
    return 4
```

Read against the five-rank ordering, that is faithful: the sakin *is* the
fourth rank, and the parenthesis (بحسب حركة ما قبله) describes its quality
rather than renumbering it. Read against the second view in the same row,
where the sakin has no rank of its own, a sakin would instead take the rank of
the vowel before it.

Both readings are defensible and the row states both, so this is a question
about which the engine should compute, not about which is correct. Changing it
would move `tafkheem_rank` on every sakin isti'la phone, and therefore move
`artifacts/tokenizer_tj1/rule_index.jsonl` and the span export, so it is the
maintainer's call. It is recorded here and nowhere else.

`tests/test_classical_upgrades.py::test_tafkheem_ranks_follow_maraatib` pins
the current behaviour (110:1 نَصْرُ, sad sakin, rank 4).
