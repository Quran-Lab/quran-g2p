"""Write artifacts/tokenizer_tj3 (tokens.txt, vocab_manifest.json) from tokenlayer_tj3.

  python tools/export_tj3.py
"""
import hashlib, json, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from quran_g2p import tokenlayer_tj3 as T  # noqa: E402

OFF_AXIS = {
    "timing_head": ["madd and leen counts", "gemination (shadda: the consonant held, one token)", "ghunna length",
                    "rawm (the vowel token, reduced)", "sakt (a pause)"],
    "attribute_heads": ["tafkheem (reh, lam, vowels)", "qalqalah", "ghunna class incl. naqis idgham on waw / yeh",
                        "imala", "tasheel"],
    "not_audible": ["ishmam (its audio is the sukun form's)"],
}


def main():
    out = ROOT / "artifacts/tokenizer_tj3"
    out.mkdir(parents=True, exist_ok=True)
    blob = "".join(f"{t} {i}\n" for i, t in enumerate(T.TOKENS)).encode("utf-8")
    (out / "tokens.txt").write_bytes(blob)
    m = {"schema_version": 3, "vocab_id": T.VOCAB_ID, "vocab_sha256": hashlib.sha256(blob).hexdigest(),
         "size": len(T.TOKENS), "blank_id": T.INDEX[T.BLANK], "word_id": T.INDEX[T.WORD],
         "foreign_id": T.INDEX[T.FOREIGN], "parent_vocab": "tj2", "off_axis": OFF_AXIS,
         "long_vowels": {"aa": "fatha + alef (and the 11:41 imala alef)", "uu": "damma + small waw",
                         "ii": "kasra + small yeh"},
         "consonant_merges": {"meem_mukhfah": "م", "hamza_musahhala": "ء"}, "ikhfa_nasal": T.IKHFA}
    (out / "vocab_manifest.json").write_text(json.dumps(m, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print(m["vocab_id"], m["size"], m["vocab_sha256"])
    # tj3g (the geminate-token comparison arm): tj3 plus a held token per consonant, ids 38..65
    og = ROOT / "artifacts/tokenizer_tj3g"
    og.mkdir(parents=True, exist_ok=True)
    blob = "".join(f"{t} {i}\n" for i, t in enumerate(T.TOKENS_G)).encode("utf-8")
    (og / "tokens.txt").write_bytes(blob)
    mg = dict(m, vocab_id="tj3g", vocab_sha256=hashlib.sha256(blob).hexdigest(), size=len(T.TOKENS_G),
              parent_vocab="tj3", geminate_ids=[T.INDEX_G[t] for t in T.GEMINATE],
              off_axis=dict(OFF_AXIS, timing_head=[x for x in OFF_AXIS["timing_head"] if not x.startswith("gemination")]))
    (og / "vocab_manifest.json").write_text(json.dumps(mg, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print(mg["vocab_id"], mg["size"], mg["vocab_sha256"])


if __name__ == "__main__":
    main()
