"""Folding a batch of new tests into the suite that already exists.

Naive concatenation looks fine and silently loses tests: two files that both
define `test_empty_input` produce one file where the second definition shadows
the first, and pytest reports the smaller number without complaining. Dropping
the collision explicitly is the difference between a suite that grows and a suite
that appears to grow.
"""

from __future__ import annotations

import ast


def _defined_names(tree: ast.Module) -> set[str]:
    names: set[str] = set()
    for node in tree.body:
        if isinstance(node, ast.FunctionDef | ast.AsyncFunctionDef | ast.ClassDef):
            names.add(node.name)
        elif isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name):
                    names.add(target.id)
    return names


def _segment(source: str, node: ast.stmt) -> str:
    lines = source.splitlines(keepends=True)
    start = node.lineno
    decorators = getattr(node, "decorator_list", [])
    if decorators:
        start = min(start, min(d.lineno for d in decorators))
    end = node.end_lineno or node.lineno
    return "".join(lines[start - 1 : end]).rstrip()


def merge_suites(existing: str, new: str) -> tuple[str, list[str]]:
    """Append the parts of `new` that do not already exist.

    Returns the merged source and the names that were skipped as duplicates.
    """
    if not existing.strip():
        return new, []
    try:
        existing_tree = ast.parse(existing)
        new_tree = ast.parse(new)
    except SyntaxError:
        return existing, []

    imports = {ast.unparse(n) for n in existing_tree.body if isinstance(n, ast.Import | ast.ImportFrom)}
    names = _defined_names(existing_tree)

    chunks: list[str] = []
    skipped: list[str] = []

    for node in new_tree.body:
        if isinstance(node, ast.Import | ast.ImportFrom):
            text = ast.unparse(node)
            if text in imports:
                continue
            imports.add(text)
            chunks.append(text)
            continue

        if isinstance(node, ast.FunctionDef | ast.AsyncFunctionDef | ast.ClassDef):
            if node.name in names:
                skipped.append(node.name)
                continue
            names.add(node.name)

        chunks.append(_segment(new, node))

    if not chunks:
        return existing, skipped

    merged = existing.rstrip() + "\n\n\n" + "\n\n\n".join(c for c in chunks if c.strip()) + "\n"
    return merged, skipped
