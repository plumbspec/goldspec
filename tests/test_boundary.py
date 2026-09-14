"""The methodology does not reach into the tool, and nothing here may make it start.

`plumb` proves the other direction — `test_nothing_shipped_imports_the_methodology` asserts that
nothing it ships imports `goldspec`. This is the mirror, and it is the half that was missing: the
dependency was one-way by intention and by nothing else, and an intention is what `status.py`
quietly broke when the methodology moved out and carried an import of
`plumb.adapters.python.archetypes` with it.

Both halves matter for different reasons. Plumb importing goldspec would make the tool require a
spec. Goldspec importing plumb makes a spec unrunnable without the tool installed — which is
`ch9-1`'s refusal, and it fails at exactly the moment somebody is writing their first chapter with
nothing else set up yet.

Read as source, never imported: importing is the thing being forbidden, so a test that imports to
find out would be doing it.
"""

import ast
import inspect
from pathlib import Path

SRC = Path(__file__).resolve().parent.parent / "src"


def _imported_roots(module: Path) -> set[str]:
    tree = ast.parse(module.read_text(encoding="utf-8"))
    roots: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            roots.update(alias.name.split(".")[0] for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.level == 0 and node.module:
            roots.add(node.module.split(".")[0])
    return roots


def test_nothing_here_imports_the_tool():
    reaching = {
        module.relative_to(SRC).as_posix(): sorted(
            r for r in _imported_roots(module) if r == "plumb")
        for module in sorted(SRC.rglob("*.py"))
        if "plumb" in _imported_roots(module)
    }
    assert not reaching, (
        "the methodology imports the tool, so a spec can no longer be run by a project that has "
        f"not installed plumb (ch9-1): {reaching}"
    )


#: The only functions this package may export, and what qualifies one.
#:
#: A gate entry point is called **about** a spec directory, by whoever is checking it — the command,
#: or a project holding its own spec to the gates from its suite. A *vocabulary* is called **from
#: inside** a spec, by the spec, to declare itself. The first is the method doing its job; the
#: second is the method demanding that a spec be a module in a language it chose.
#:
#: The list is asserted by equality rather than by membership, so a new export fails here and is
#: added deliberately or not at all. Adding one means answering the question above in a sentence.
GATE_ENTRY_POINTS = ["check_spec_directory", "conventions_for", "find_config"]


def test_a_spec_needs_no_vocabulary_to_import():
    """Nothing here is callable *from* a spec, and there must never be again.

    A subject is declared by its row in a chapter's trace table. `story()` was the last thing a
    spec had to import, and while it existed a spec had to be a module somebody's runner collects
    — which is a language, imposed by a method that has no business naming one. It is also how the
    tool got imported: the parameter that reached back for `declare` was on that function.

    Checked as *absence of an export*, which is the shape the next one would arrive in.

    `conventions_for` and `find_config` joined the list when a project's conventions got one home:
    both take a spec directory and answer a question about it from the outside, which is the gate's
    side of the line. Neither is reachable from a chapter, because a chapter is markdown.
    """
    import goldspec

    callable_exports = sorted(name for name in goldspec.__all__
                              if inspect.isfunction(getattr(goldspec, name, None)))
    assert callable_exports == sorted(GATE_ENTRY_POINTS), (
        "goldspec exports a function a spec could call — a spec declares itself in prose, and a "
        f"vocabulary is how that stopped being true last time: {callable_exports}"
    )
