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


if __name__ == "__main__":
    main()
