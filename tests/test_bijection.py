"""Old-vocab warm-start map (Part B1 bijection deliverable, plan B4).

artifacts/tokenizer_tj1/bijection_old250.json maps every tj1 token to the
old 250-unit chunk vocab (tarteel-asr phoneme_units.json). Many-to-one is
expected exactly where tj1 splits finer (the '^' tafkheem axis, scoring-
length closure); each mapped row seeds the new token's CTC output row at
warm-start. Blank note: the old FILE says <blank>:0 but the trainer
appends blank at 250 - the manifest records both to keep the footgun dead.
"""
import json
from pathlib import Path

ART = Path(__file__).resolve().parents[1] / "artifacts" / "tokenizer_tj1"


def load():
    with open(ART / "bijection_old250.json", encoding="utf-8") as f:
        return json.load(f)


def test_artifact_exists_with_meta():
    b = load()
    assert b["meta"]["old_vocab_sha256"]
    assert b["meta"]["old_blank_file_id"] == 0
    assert b["meta"]["old_blank_trainer_id"] == 250
    assert b["meta"]["new_blank_id"] == 233


def test_every_observed_token_mapped():
    b = load()
    tokens = {}
    with open(ART / "ayah_tokens.jsonl", encoding="utf-8") as f:
        for line in f:
            row = json.loads(line)
            if "__meta__" in row:
                continue
            for t in row["tokens"]:
                tokens[t] = tokens.get(t, 0) + 1
    mapping = b["map"]
    missing = [t for t in tokens if t not in mapping
               or mapping[t]["provenance"] not in ("observed", "observed_split")]
    assert not missing, missing[:10]


def test_map_is_functional_into_old_vocab():
    b = load()
    old_units = set(b["meta"]["old_units"])
    for tok, ent in b["map"].items():
        if ent["provenance"] == "unmapped":
            assert ent.get("parent_token"), tok  # warm-start parent required
            continue
        assert isinstance(ent["old_unit"], str) and ent["old_unit"] in old_units, tok


def test_observed_positional_consistency_recorded():
    # the builder must certify corpus-wide 1:1 positional alignment
    b = load()
    assert b["meta"]["ayat_aligned"] == 6236
    assert b["meta"]["alignment_mismatches"] == 0
