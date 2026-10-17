"""Write artifacts/tokenizer_tj2 (tokens.txt, vocab_manifest.json, tj1_to_tj2.json) from the engine.

  python tools/export_tj2.py [--b8 C:/Users/Anon/research/tarteel-asr/data/v4_phonetics/v4_tokenizer_labeler.json]
"""
import argparse, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from quran_g2p.export_vocab_tj2 import build_tj2, write_tj2  # noqa: E402


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--b8", default="C:/Users/Anon/research/tarteel-asr/data/v4_phonetics/v4_tokenizer_labeler.json")
    a = ap.parse_args()
    v = build_tj2(ROOT / "artifacts/tokenizer_tj1/tokens.txt", progress=True)
    m = write_tj2(v, ROOT / "artifacts/tokenizer_tj2", a.b8 if Path(a.b8).exists() else None)
    print(m["vocab_id"], m["size"], m["counts"], m["vocab_sha256"])


if __name__ == "__main__":
    main()
