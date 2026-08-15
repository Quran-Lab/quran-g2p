"""Regenerate src/quran_g2p/codepoints.py from the pinned editions' censuses.

Run after pinning a new edition or refreshing a census. The module is generated
(not hand-edited) so the no-hand-typed-Arabic guarantee extends to codepoints.py
itself: values are emitted as backslash-u escapes.
"""
import json
import unicodedata
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def const_name(cp_hex: str) -> str:
    ch = chr(int(cp_hex, 16))
    try:
        n = unicodedata.name(ch)
    except ValueError:
        return f"CP_{cp_hex}"
    n = n.replace("ARABIC LETTER ", "").replace("ARABIC ", "")
    n = n.replace("-", " ").replace(" ", "_")
    if n[0].isdigit():
        n = "CP_" + n
    return n


#: Phonetic-layer symbols that never occur in the source texts but are part
#: of the token/oracle conventions (qalqalah marker, mukhfah carriers, tasheel
#: hamza, ikhtilas damma).
EXTRA_PHONETIC = ["0619", "0672", "0687", "06BA", "06FE"]


def main() -> None:
    union: set[str] = set(EXTRA_PHONETIC)
    for f in sorted((ROOT / "data").glob("census-*.json")):
        union |= set(json.loads(f.read_text(encoding="utf-8")))

    lines = [
        '"""Every Arabic codepoint used anywhere in this project, as named constants.',
        "",
        "Generated from the union of the pinned editions' censuses; regenerate via",
        "tools/gen_codepoints.py when a new edition is pinned. The values are written",
        "as backslash-u escapes on purpose: no hand-typed Arabic anywhere in the repo.",
        '"""',
        "",
    ]
    mapping: dict[str, str] = {}
    for cp_hex in sorted(union):
        name = const_name(cp_hex)
        assert name not in mapping.values(), (cp_hex, name)
        mapping[cp_hex] = name
        uname = unicodedata.name(chr(int(cp_hex, 16)), "?")
        esc = "\\" + "u" + cp_hex.lower()
        lines.append(f'{name} = "{esc}"  # U+{cp_hex} {uname}')
    lines += ["", "ALL = {"]
    for cp_hex, name in sorted(mapping.items(), key=lambda kv: kv[1]):
        lines.append(f'    "{name}": {name},')
    lines += ["}", "", 'NAME_BY_CP = {f"{ord(v):04X}": k for k, v in ALL.items()}', ""]
    (ROOT / "src" / "quran_g2p" / "codepoints.py").write_text("\n".join(lines), encoding="utf-8")
    print(f"wrote {len(mapping)} constants")


if __name__ == "__main__":
    main()
