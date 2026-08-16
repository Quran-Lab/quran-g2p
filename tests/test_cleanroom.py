"""Clean-room guarantee, enforced structurally.

src/quran_g2p must never import the oracle quarantine or the reference-engine package
(quran_transcript), and must never contain Arabic-block string literals outside
codepoints.py. These are the two structural bans that make "clean-room" and
"no hand-typed Arabic" testable claims instead of intentions.
"""
import ast
from pathlib import Path

SRC = Path(__file__).resolve().parents[1] / "src" / "quran_g2p"

BANNED_IMPORT_ROOTS = {"quran_transcript", "oracle", "quran_phones"}

# Arabic-script blocks whose literals are banned outside codepoints.py.
_ARABIC_RANGES = [(0x0600, 0x06FF), (0x0750, 0x077F), (0x08A0, 0x08FF), (0xFB50, 0xFDFF), (0xFE70, 0xFEFF)]


def _is_arabic(ch: str) -> bool:
    return any(lo <= ord(ch) <= hi for lo, hi in _ARABIC_RANGES)


def _iter_src_files():
    files = sorted(SRC.rglob("*.py"))
    assert files, f"no source files found under {SRC}"
    return files


def test_src_never_imports_oracle_or_reference():
    violations = []
    for path in _iter_src_files():
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                roots = [alias.name.split(".")[0] for alias in node.names]
            elif isinstance(node, ast.ImportFrom):
                roots = [(node.module or "").split(".")[0]]
            else:
                continue
            for root in roots:
                if root in BANNED_IMPORT_ROOTS:
                    violations.append(f"{path.name}:{node.lineno} imports {root}")
    assert not violations, violations


def _docstring_linenos(tree):
    linenos = set()
    for node in ast.walk(tree):
        if isinstance(node, (ast.Module, ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)):
            body = getattr(node, "body", [])
            if body and isinstance(body[0], ast.Expr) and isinstance(body[0].value, ast.Constant) \
                    and isinstance(body[0].value.value, str):
                linenos.add(body[0].value.lineno)
    return linenos


def test_no_arabic_literals_outside_codepoints():
    # Docstrings are exempt: Arabic RULE NAMES in prose aid review and never
    # enter logic. The ban targets literals used as values/comparisons.
    # rules/registry.py is likewise exempt: its Arabic strings are the
    # rulings' names and classical citations (display/review metadata,
    # asserted by the register gate to never feed engine logic) — the
    # engine's phonological literals remain confined to codepoints.py.
    violations = []
    for path in _iter_src_files():
        if path.name == "codepoints.py":
            continue
        if path.name == "registry.py" and path.parent.name == "rules":
            continue
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        doclines = _docstring_linenos(tree)
        for node in ast.walk(tree):
            if isinstance(node, ast.Constant) and isinstance(node.value, str):
                if node.lineno in doclines:
                    continue
                if any(_is_arabic(c) for c in node.value):
                    violations.append(f"{path.name}:{node.lineno} Arabic literal {node.value!r:.40}")
    assert not violations, violations
