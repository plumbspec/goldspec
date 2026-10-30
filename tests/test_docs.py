"""The documentation is held to the tool, not trusted to agree with it.

Two things are checked and they fail in opposite directions.

**The worked example is run through the real gate.** `docs/getting-started.md` walks one chapter
part by part, and that chapter ships beside it under `docs/example/` so a reader can copy it. An
example that fails when copied is worse than no example: it teaches the conventions wrongly, and it
does so to somebody who has no way yet to tell.

**The closed sets the tutorial enumerates are compared against the code.** The page lists the four
provenance values, the three enforcement values and the six columns, because an author who cannot
find them invents worse ones. Prose cannot notice a constant changing underneath it, so this does.
It is checked as *the doc mentions each value*, not as an exact list — the page is prose and may say
them in any order or wording, but it may not silently stop naming one.
"""

from pathlib import Path

import pytest

from goldspec import check_spec_directory, conventions_for
from goldspec.review import _MADE, _SUPPLIED
from goldspec.nodes import SECTIONS

DOCS = Path(__file__).resolve().parent.parent / "docs"
EXAMPLE = DOCS / "example" / "spec"
TUTORIAL = DOCS / "getting-started.md"


def test_the_worked_example_passes_the_gate_a_reader_would_run():
    """Through the same call the command makes, over the files as shipped."""
    report = check_spec_directory(EXAMPLE, conventions_for(EXAMPLE), cited_from=EXAMPLE.parent)

    assert report.problems == [], (
        "the example published beside the tutorial does not pass:\n  "
        + "\n  ".join(report.problems))
    assert report.checked, "a run that checked nothing is not a pass"



def test_the_example_is_a_main_flow_with_a_drill_down_held_to_one_tree():
    """The first corpus a reader sees is the shape every corpus takes: one main flow, named so the
    gate holds the tree, and a chapter that drills into one of its steps — never two top-level flows
    side by side, which is what a reader copying the example would otherwise learn."""
    conv = conventions_for(EXAMPLE)
    assert conv.main_flow == "chapter-01-ordering.md"
    flows = sorted(p.name for p in (EXAMPLE / conv.flow_dir).glob(conv.flow_glob))
    assert flows == ["chapter-01-ordering.md", "chapter-01.3-charging.md"]
    tutorial = TUTORIAL.read_text(encoding="utf-8")
    opening = tutorial[:tutorial.index("## 1.")]
    assert "one main flow" in opening and "chapter-01.3-charging.md" in opening, (
        "the tutorial shows the tree before it walks a chapter")



def test_the_example_actually_exercises_the_checks():
    """Correspondence over an empty spec proves nothing, and 0 subjects is itself a fault the gate
    reports — so the count is asserted rather than the absence of problems alone."""
    report = check_spec_directory(EXAMPLE, conventions_for(EXAMPLE), cited_from=EXAMPLE.parent)
    checked = " ".join(report.checked)

    # Eight: the four nodes, the decision, the parameter and the two open unknowns. Every one of
    # the four kinds of subject the method defines, which is what makes this example worth
    # checking — a citation to any of them has to resolve.
    #
    # It was five while the example DREW `ch1-P1` and declared it nowhere, against a tutorial
    # saying a parameter lives at the foot of its node's block "and nowhere else"; and six while
    # an open unknown — one of those four kinds — was refused as "declared nowhere" about a bullet
    # sitting in plain sight. An example is read as the authority on every question the prose
    # leaves open, so both taught the opposite of the page beside them.
    assert "14 subject(s)" in checked, f"the example stopped declaring its fourteen subjects: {checked}"
    assert "chapter(s) in the node format, 8 node(s)" in checked, (
        f"the example no longer reads as four nodes, so the checks the tutorial says it exercises "
        f"are not being run over it: {checked}")
    assert "process flow(s) render" in checked, f"the example's flow no longer renders: {checked}"


@pytest.mark.parametrize("value", sorted(_SUPPLIED | _MADE))
def test_the_tutorial_names_every_provenance_the_gate_accepts(value):
    assert f"`{value}`" in TUTORIAL.read_text(encoding="utf-8"), (
        f"the gate accepts provenance {value!r} and the tutorial never mentions it — a value an "
        "author cannot find is one they will not use, and the closed set is the whole point of "
        "the column")


@pytest.mark.parametrize("column", ["Information", "IO", "Description", "Required", "Provenance"])
def test_the_tutorial_names_every_column_of_an_information_table(column):
    assert column in TUTORIAL.read_text(encoding="utf-8"), (
        f"an Information row has a {column!r} column the tutorial never shows. Rows are read "
        "positionally, so a reader who omits it does not get a warning — they get a table nothing "
        "reads")


def test_the_tutorial_and_the_example_define_the_same_classes():
    """The `classDef` block is stated twice on purpose, so it is checked.

    It has to be in the tutorial: a page that names seven `classDef` lines and ships none leaves
    the diagram unwritable without opening the example. It also has to be in the example, because that is the
    file people copy. Two homes for one fact is this method's defect, and the answer where a copy is
    genuinely required is not to pretend otherwise — it is to make the copy fail when it drifts.

    The failure being prevented is not cosmetic. A class used and never defined is a fault the gate
    raises, so a tutorial listing a class the example omits sends an author straight into a red run:
    `:::subroutine` was in the shapes table and in no `classDef` anywhere, and a reader demoted a
    sub-flow to a plain node rather than risk it.
    """
    import re

    def classes(text):
        return set(re.findall(r"classDef\s+(\w+)", text))

    tutorial = classes(TUTORIAL.read_text(encoding="utf-8"))
    example = classes((EXAMPLE / "diagrams" / "chapter-01-ordering.md").read_text(encoding="utf-8"))

    assert tutorial and example, "one of them stopped carrying classDef lines at all"
    assert tutorial == example, (
        "the tutorial and the worked example define different diagram classes — an author following "
        f"one and copying the other gets a class the gate refuses:\n  only in tutorial: "
        f"{sorted(tutorial - example)}\n  only in example: {sorted(example - tutorial)}")


def test_every_shape_the_tutorial_names_has_a_class():
    """The shapes table is what an author reads; a role in it whose class nobody defines is a trap."""
    import re

    text = TUTORIAL.read_text(encoding="utf-8")
    named = set(re.findall(r"`:::(\w+)`", text))
    defined = set(re.findall(r"classDef\s+(\w+)", text))

    assert named <= defined, (
        f"the tutorial names classes it never defines: {sorted(named - defined)}. Every one of them "
        "is a fault waiting for whoever uses that shape")


def test_the_tutorial_lists_the_sections_in_the_order_the_gate_wants():
    """Order is enforced, so a tutorial that showed them in another order would teach a fault.

    Anchored on the page's own canonical listing rather than on the first mention of each name.
    The earlier version searched the whole page and broke the moment a section was *discussed* out
    of order in prose — which is legitimate and happens throughout. What has to be right is the one
    block a reader copies from.
    """
    listing = "\n".join(f"    ## {section}" for section in SECTIONS)

    assert listing in TUTORIAL.read_text(encoding="utf-8"), (
        "the tutorial does not carry the section list verbatim, in the gate's order — that block is "
        f"what a reader copies, and the order is checked:\n{listing}")
