"""Render the canonical rulings register to docs/RULINGS-REGISTER.md.

The document is generated, never hand-edited; a freshness test compares
it against this renderer so it can never drift from the register.
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from quran_g2p.rules.registry import RULINGS  # noqa: E402

PHASE_TITLES = {
    "P1": "P1 - Orthographic decode",
    "P3": "P3 - Ibtida'",
    "P4": "P4 - Pausal (waqf)",
    "P5": "P5 - Junction (wasl)",
    "P6": "P6 - Noon sakinah and tanween",
    "P7": "P7 - Meem sakinah",
    "P8": "P8 - General idgham",
    "P9": "P9 - Ghunna",
    "P10": "P10 - Madd",
    "P11": "P11 - Qalqalah",
    "P12": "P12 - Tafkheem",
    "P13": "P13 - One-offs",
}


def render() -> str:
    lines = [
        "# The rulings register",
        "",
        "Generated from `src/quran_g2p/rules/registry.py` by",
        "`tools/export_register.py`; a test keeps this file in sync, and a",
        "second test keeps the register itself equal to the set of rules the",
        "engine can actually cite. Every ruling is stated for the expert",
        "reviewer by the golden rows listed in its **review** column",
        "(`tests/goldens/`), each of which carries the fuller citation.",
        "",
        f"{len(RULINGS)} rules. Ids are stable and append-only.",
        "",
    ]
    for phase, title in PHASE_TITLES.items():
        rules = [r for r in RULINGS if r.phase == phase]
        if not rules:
            continue
        lines += [f"## {title}", "",
                  "| id | الحكم | sources | review |", "|---|---|---|---|"]
        for r in rules:
            rows = ", ".join(f"`{c}`" for c in r.covered_by)
            note = f" *({r.note})*" if r.note else ""
            lines.append(
                f"| `{r.id}` | {r.name_ar} — {r.name_en} | {r.cite} |"
                f" {rows}{note} |")
        lines.append("")
    return "\n".join(lines).replace(" — ", " / ") + ""


def main() -> None:
    out = ROOT / "docs" / "RULINGS-REGISTER.md"
    out.parent.mkdir(exist_ok=True)
    out.write_text(render(), encoding="utf-8")
    print(f"wrote {out} ({len(RULINGS)} rules)")


if __name__ == "__main__":
    main()
