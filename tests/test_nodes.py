"""The node format, and the checks that hold a chapter to it.

**Asserted as a difference, not as a green run.** Every test here builds a chapter that is correct
and then breaks exactly one thing, because a check that fires on everything passes a suite as
readily as one that fires on the right thing. The clean fixture is asserted clean first, so a
regression that makes the gate refuse everything fails here rather than looking like success.

A chapter is held to the shape it is written in: one that predates the format is counted and 89
corpus that predates the format is in the older shape. A chapter without a `## Nodes` section must
be read the old way and counted, never failed — so that is tested too, in both directions.
"""

from pathlib import Path

import pytest

from goldspec import check_spec_directory
from goldspec.conventions import Conventions
from goldspec.nodes import Node, faults, read

CLEAN = """# Chapter 1 — a customer places an order

**Last updated** 2026-09-15 v1

> **As a customer I want to place an order and be told it was accepted, so that I know I will be
> charged for something that is actually coming.**

```mermaid
flowchart TD
    START([START]):::terminal
    TAKE[ch1-1 take the order]:::process
    CHARGE[ch1-2 charge once]:::process
    DONE([END]):::good
    START --> TAKE --> CHARGE --> DONE
```

## Nodes

### ch1-1 · take the order

> **As a customer I want my basket recorded as I chose it, so that nothing is reconstructed later.**

#### Information

| Information | IO | Description | Required | Provenance |
|---|---|---|---|---|
| ch1-1-inf1 | In | `basket` | yes | authored |
| ch1-1-inf2 | Out | `order` | yes | derived |

#### User Requirements
  * ch1-1-ur1 - the basket is recorded as the customer chose it

#### System Requirements

#### Non-Functional Requirements

#### Unknowns


---

### ch1-2 · charge once

> **As a customer I want to be charged exactly once, so that a retry does not cost me twice.**

#### Information

| Information | IO | Description | Required | Provenance |
|---|---|---|---|---|
| ch1-2-inf1 | In | `order` | yes | ch1-1 |
| ch1-2-inf2 | Out | `charge` | yes | observed |

#### User Requirements
  * ch1-2-ur1 - a retry charges nothing a second time

#### System Requirements

#### Non-Functional Requirements

#### Unknowns

**Decision `ch1-D1` — the processor's reconciliation window closes at 02:00.**

## Glossary

| Term | Meaning |
|---|---|
| Basket | What a customer chose, before it is an order |
"""


def _chapter(tmp_path: Path, text: str = CLEAN) -> Path:
    path = tmp_path / "chapter-01-ordering.md"
    path.write_text(text, encoding="utf-8")
    return path


def _check(tmp_path: Path, text: str = CLEAN, drawn=("ch1-1", "ch1-2")) -> list:
    return faults(read(_chapter(tmp_path, text)), "ch1", set(drawn))


# ── the format is read at all ───────────────────────────────────────────────────────────────────


def test_a_chapter_in_the_format_is_read(tmp_path):
    chapter = read(_chapter(tmp_path))

    assert [n.id for n in chapter.nodes] == ["ch1-1", "ch1-2"]
    assert chapter.nodes[0].consumes == ("basket",)
    assert chapter.nodes[0].produces == ("order",)
    assert chapter.nodes[1].kinded == ("ch1-D1",)
    # The story, not the title. A backlog read off a converted chapter is the title plus nothing
    # unless this is parsed — `take the order` is what the step is called, and only the blockquote
    # says who wants it and why, which is the whole of what the old trace row's claim carried.
    assert chapter.nodes[0].story.startswith("As a customer I want my basket recorded")
    assert "**" not in chapter.nodes[0].story, "the emphasis is markdown, not part of the claim"


def test_a_chapter_not_in_the_format_reads_as_none(tmp_path):
    """The detection, and it is the whole of the migration story: no `## Nodes`, no node format."""
    assert read(_chapter(tmp_path, CLEAN.replace("## Nodes", "## Story → test trace"))) is None


def test_the_clean_fixture_is_clean(tmp_path):
    """Asserted first, so a gate that refuses everything fails here rather than passing every
    test below it vacuously."""
    assert _check(tmp_path) == []


# ── each check, proved by breaking exactly one thing ────────────────────────────────────────────




def test_a_node_not_namespaced_to_its_chapter_is_named(tmp_path):
    broken = CLEAN.replace("### ch1-2 ·", "### ch2-9 ·")
    assert any("ch2-9" in f and "not namespaced" in f for f in _check(tmp_path, broken,
                                                                     drawn=("ch1-1",)))


def test_a_node_drawn_and_never_expanded_is_named(tmp_path):
    """The half that goes unnoticed, because the diagram looks complete."""
    assert any("ch1-3" in f and "no node block" in f
               for f in _check(tmp_path, drawn=("ch1-1", "ch1-2", "ch1-3")))


def test_a_node_expanded_and_not_in_the_flow_is_named(tmp_path):
    assert any("ch1-2" in f and "not in the flow" in f
               for f in _check(tmp_path, drawn=("ch1-1",)))


def test_a_node_that_moves_nothing_is_named(tmp_path):
    broken = CLEAN.replace(
        "| ch1-2-inf1 | In | `order` | yes | ch1-1 |\n"
        "| ch1-2-inf2 | Out | `charge` | yes | observed |\n", "")
    assert any("ch1-2" in f and "scenery" in f for f in _check(tmp_path, broken))




def test_a_node_expanded_twice_is_named(tmp_path):
    # Inserted *inside* the Nodes section. Appended after the glossary it is not a node at all, and
    # the parser is right to ignore it — a `###` under another `##` belongs to that section.
    broken = CLEAN.replace(
        "## Glossary",
        "### ch1-1 · take the order again\n\n#### Information\n\n"
        "| Information | IO | Description | Required | Provenance |\n|---|---|---|---|---|\n"
        "| ch1-1-inf9 | In | `order` | yes | ch1-1 |\n\n## Glossary", 1)
    assert any("ch1-1" in f and "more than once" in f for f in _check(tmp_path, broken))


def test_a_kinded_id_not_namespaced_to_its_chapter_is_named(tmp_path):
    broken = CLEAN.replace("`ch1-D1`", "`ch9-D1`")
    assert any("ch9-D1" in f and "not namespaced" in f for f in _check(tmp_path, broken))


def test_citing_another_chapters_unknown_is_not_declaring_one(tmp_path):
    """A node points at a decision another chapter owns, which is the ordinary way chapters relate.

    Read as a declaration, every such citation was reported as an id not namespaced to its chapter —
    so the gate refused correct prose, and did it the first time a converted chapter cited across
    chapters at all. The run-in is what separates the two: a parameter and a decision are *stated* in a
    bold lead-in at the start of a line, and a sentence mentioning somebody else's unknown is not.
    """
    citing = CLEAN.replace(
        "**Decision `ch1-D1` — the processor's reconciliation window closes at 02:00.**",
        "**Decision `ch1-D1` — the processor's reconciliation window closes at 02:00.**\n\n"
        "Whether a retry may cross that window is `ch9-U4`, and the depth it needs is `ch3-P2`.")
    chapter = read(_chapter(tmp_path, citing))

    assert chapter.nodes[1].kinded == ("ch1-D1",), (
        f"a cited id was read as a declared one: {chapter.nodes[1].kinded}")
    assert _check(tmp_path, citing) == [], "citing another chapter's unknown was refused"


# ── the phase: reported before it is gated ──────────────────────────────────────────────────────


def _spec(tmp_path: Path, text: str) -> Path:
    spec = tmp_path / "spec" / "diagrams"
    spec.mkdir(parents=True)
    (spec / "chapter-01-ordering.md").write_text(text, encoding="utf-8")
    return tmp_path / "spec"


def test_an_unconverted_chapter_is_counted_and_never_failed(tmp_path):
    """A corpus that predates the format. Turning it on must not fail a chapter for being in
    the shape it was written in — that is what the count is for."""
    old = CLEAN.replace("## Nodes", "## Story → test trace").replace("## Elements", "## Prologue")
    spec = _spec(tmp_path, old)

    report = check_spec_directory(spec, Conventions(), cited_from=spec.parent)

    assert not any("node" in p.lower() and "format" in p.lower() for p in report.problems)
    assert any("0 of 1 chapter(s) in the node format" in c for c in report.checked)


# ---- the start-and-end check reads the flow the tutorial teaches --------------------------------

LEGEND = """
    subgraph LEGEND["legend — shape carries the role"]
        direction LR
        LT([START / END]):::terminal
        LA[action]:::process
    end
"""


def test_a_chain_on_one_line_is_every_hop_of_it():
    """`A --> B --> C` and one edge per line are the same graph, so they answer the same.

    Reading only the first pair made `C` a node nothing points at and `B` a node nothing leaves,
    which is a start and an end invented out of the notation. Every chapter the tutorial draws is
    written this way, so the check was answering about a graph no chapter has.
    """
    from goldspec.flowcheck import terminals

    nodes = "    A[a]\n    B[b]\n    C[c]\n"
    assert terminals(nodes + "    A --> B --> C") == terminals(
        nodes + "    A --> B\n    B --> C") == (["A"], ["C"])


def test_a_node_drawn_and_never_connected_is_neither_a_start_nor_an_end():
    """The legend this dialect asks every chapter to ship is nodes with no edges at all.

    Counting a node as a start merely because nothing points at it made the legend seven starts
    and seven ends, so a chapter carrying one satisfied the check whatever its flow did — a gate
    that cannot fail. A start has a way out; an end is arrived at.
    """
    from goldspec.flowcheck import terminals

    cycle = "    A[a]\n    B[b]\n    A --> B\n    B --> A"
    assert terminals(cycle) == ([], [])
    assert terminals(cycle + LEGEND) == ([], []), "the legend must not supply the terminals"


def test_the_worked_example_begins_and_ends_where_it_is_drawn_to():
    """The shipped chapter, read as a graph: one start, and both of its endings."""
    from goldspec.flowcheck import terminals
    from goldspec.nodes import mermaid_blocks

    text = Path("docs/example/spec/diagrams/chapter-01-ordering.md").read_text(encoding="utf-8")
    starts, ends = terminals("\n".join(mermaid_blocks(text)))
    assert starts == ["START"]
    assert sorted(ends) == ["DONE", "SHORT"]


# ---- a constraint stated for the whole flow is still a subject ----------------------------------

FLOW_LEVEL = CLEAN.replace(
    "## Nodes",
    "**Decision `ch1-D2` — the round closes on a fixed date.** External and restricting.\n"
    "\n## Nodes", 1)


def test_a_decision_stated_for_the_whole_flow_is_declared(tmp_path):
    """The format provides for one above `## Nodes`, and nothing read it.

    Kinded ids were parsed only inside node blocks, so a constraint written exactly where the
    tutorial says to write it was declared nowhere — uncitable, and held to no namespace. It is
    the placement the tutorial recommends for a constraint that is genuinely not one step's, so
    the advice and the gate disagreed about whether the result was a subject at all.
    """
    chapter = read(_chapter(tmp_path, FLOW_LEVEL))
    assert chapter.kinded == ("ch1-D2",), (
        f"a flow-level decision is not read off the chapter: {chapter.kinded}")

    from goldspec.specgate import declared_in_spec

    spec = _spec(tmp_path / "corpus", FLOW_LEVEL)
    declared = declared_in_spec(spec, Conventions())
    assert "ch1-D2" in declared, (
        f"the flow-level decision is not among what the spec declares, so a citation to it is "
        f"unsatisfiable however the chapter is written: {declared}")


def test_a_flow_level_decision_is_namespaced_to_its_chapter(tmp_path):
    """`zz9-D9` between the diagram and `## Nodes` passed, on a spec with no other fault."""
    stray = FLOW_LEVEL.replace("`ch1-D2`", "`zz9-D9`")
    found = faults(read(_chapter(tmp_path, stray)), "ch1", {"ch1-1", "ch1-2"})
    assert any("zz9-D9" in f and "namespaced" in f for f in found), found


def test_one_number_series_covers_both_placements(tmp_path):
    """"Flow-level and node-level decisions share one number series per chapter" — held, now."""
    twice = FLOW_LEVEL.replace(
        "#### Unknowns",
        "#### Unknowns\n\n**Decision `ch1-D2` — the same id, at a node.** Restating.", 1)
    found = faults(read(_chapter(tmp_path, twice)), "ch1", {"ch1-1", "ch1-2"})
    assert any("ch1-D2" in f and "more than once" in f for f in found), found


def test_a_requirement_bullet_nothing_can_read_is_named(tmp_path):
    """The separator is load-bearing and its absence was silent.

    `* ch1-2-ur1: the text` and `* ch1-2-ur1 — the text` parse as nothing, so the requirement is
    not read at all: the ownership check and the duplicate check go quiet on a line that looks
    exactly right, and nothing counts requirements, so there was no number to compare either.
    That is the shape of failure this whole module is arranged to prevent, inside the parser.
    """
    # An em dash and an en dash now read the same as a hyphen, as they do in a `###` heading.
    for at, separator in enumerate((":", "", ";")):
        broken = CLEAN.replace("ch1-1-ur1 - ", f"ch1-1-ur1{separator} ", 1)
        where = tmp_path / f"case{at}"
        where.mkdir()
        found = faults(read(_chapter(where, broken)), "ch1", {"ch1-1", "ch1-2"})
        assert any("ch1-1-ur1" in f and "nothing reads" in f for f in found), (
            f"a requirement written with {separator!r} between the id and the text was read as "
            f"nothing and reported as nothing: {found}")


def test_the_dashes_a_heading_accepts_a_requirement_accepts(tmp_path):
    """`:586` blesses `-`, `\u2013` and `\u2014` for a node heading, and a reader carries the habit."""
    for at, separator in enumerate(("-", "\u2013", "\u2014")):
        where = tmp_path / f"dash{at}"
        where.mkdir()
        chapter = read(_chapter(where, CLEAN.replace("ch1-1-ur1 - ", f"ch1-1-ur1 {separator} ", 1)))
        assert not any(node.malformed for node in chapter.nodes), (
            f"a requirement separated by {separator!r} was read as unreadable")


def test_a_row_named_for_another_step_is_named(tmp_path):
    """The rule a requirement is already held to, and a row was not — with nothing saying which."""
    misfiled = CLEAN.replace("| ch1-2-inf1 |", "| ch1-1-inf9 |", 1)
    found = faults(read(_chapter(tmp_path, misfiled)), "ch1", {"ch1-1", "ch1-2"})
    assert any("ch1-1-inf9" in f and "filed on the step that moves it" in f for f in found), found


def test_the_clean_fixture_has_no_unreadable_requirement(tmp_path):
    """The check is a difference, so the correct shape must stay silent."""
    chapter = read(_chapter(tmp_path, CLEAN))
    assert not any(node.malformed for node in chapter.nodes), (
        "the requirement shape the documentation teaches is being reported as unreadable")


def test_a_table_row_nothing_can_read_is_named(tmp_path):
    """A row the five-column parser could not read used to vanish before every check.

    An unidentified required input, from a step that does not exist, passed a clean run — the row
    matched nothing, so the element it moves and the provenance it claims were never in the data
    any check saw. `Input` and `Output`, which is the older shape's own spelling, disappeared the
    same way rather than being refused.
    """
    for at, broken in enumerate((
            CLEAN.replace("| ch1-1-inf1 | In |", "|  | In |", 1),
            CLEAN.replace("| ch1-1-inf1 | In |", "| ch1-1-inf1 | Input |", 1))):
        where = tmp_path / f"row{at}"
        where.mkdir()
        found = faults(read(_chapter(where, broken)), "ch1", {"ch1-1", "ch1-2"})
        assert any("nothing can read" in f for f in found), (
            f"a row nothing could parse was dropped in silence rather than named: {found}")


def test_a_diagram_is_indented_however_its_author_indents_it(tmp_path):
    """`^\\s{4}` meant exactly four whitespace characters, and mermaid does not care.

    At two, six or eight spaces the var-to-id map came back empty — so `chain`, `provenance`'s
    reachability half and `unconsumed` all went silent together, while every node in the chapter
    was reported as not being in the flow. Four faults naming the wrong cause, and three real
    gates off, over an indent nothing documented because nothing knew it mattered.
    """
    from goldspec.nodes import read_flow

    for spaces in (2, 4, 6, 8):
        body = "\n".join(" " * spaces + line for line in (
            "A[<b>ch1-1</b> take the order]:::process",
            "B[<b>ch1-2</b> charge once]:::process",
            "A --> B"))
        _, var2id, _ = read_flow(f"```mermaid\nflowchart TD\n{body}\n```")
        assert var2id == {"A": "ch1-1", "B": "ch1-2"}, (
            f"a diagram indented by {spaces} reads as naming no nodes: {var2id}")


def test_a_heading_quoted_in_a_code_block_is_not_a_section(tmp_path):
    """The section scan re-read the file raw, so a chapter could not quote a `##` heading.

    It is the concrete cost of a second observer: this page promises exactly one reader, and the
    one that went back to the source had its own opinion of what a `##` line is.
    """
    quoting = CLEAN + "\n\n## Working notes\n\n```\n## Input → process → output\n```\n"
    found = faults(read(_chapter(tmp_path, quoting)), "ch1", {"ch1-1", "ch1-2"})
    assert not any("sections are" in f for f in found), (
        f"a `##` heading inside a fenced code block was read as a section: {found}")


def test_working_notes_are_exempt_only_where_they_belong(tmp_path):
    """The exemption is for a TRAILING section that says what it is, and placement was unchecked.

    Two passages say it goes last and nothing held it there, so a chapter could open with its
    working notes and pass. The heading keeps its own wording after the name — the corpus writes
    `## Working notes — not part of the chapter` — which is the whole reason ignoring it is honest
    rather than lenient, so the name is a prefix and the position is the rule.
    """
    ok, bad = tmp_path / "ok", tmp_path / "bad"
    ok.mkdir(); bad.mkdir()
    trailing = CLEAN + "\n\n## Working notes — not part of the chapter\n\nstill thinking.\n"
    assert not [f for f in faults(read(_chapter(ok, trailing)), "ch1",
                                  {"ch1-1", "ch1-2"}) if "sections are" in f], (
        "a trailing working-notes section is not exempt, and the corpus writes one")

    leading = CLEAN.replace("## Nodes", "## Working notes — first?\n\nnope.\n\n## Nodes", 1)
    assert [f for f in faults(read(_chapter(bad, leading)), "ch1",
                              {"ch1-1", "ch1-2"}) if "sections are" in f], (
        "working notes above the chapter's own sections passed the section check")


def test_a_chapter_named_by_its_sigil_can_declare_a_decision(tmp_path):
    """A corpus that names its flows by sigil has a prefix with no number in it.

    `chapter-01-ordering.md` gives `ch1`, so `ch1-D1` reads. A flow named `snd-send-what-a-run-
    produced.md` gives `snd`, its nodes are `snd1`..`snd4`, and the only spelling consistent with
    those is `snd-D1` — which matched nothing. It was declared nowhere and held to no namespace,
    and the run reported no fault, because the gate could not see it in order to refuse it.
    """
    from goldspec.specgate import declared_in_spec

    sigil = CLEAN.replace("ch1-", "snd").replace("### snd1 ", "### snd1 ").replace(
        "## Nodes",
        "**Decision `snd-D1` — the window closes at 02:00.** External and restricting.\n\n## Nodes",
        1)
    chapter = read(_chapter(tmp_path, sigil))
    assert chapter.kinded == ("snd-D1",), (
        f"a decision in a chapter whose prefix carries no number is invisible: {chapter.kinded}")


def test_the_corpus_this_ships_with_still_declares_its_own_kinded_ids(tmp_path):
    """The numbered spelling is the common one, and widening the pattern must not lose it."""
    from goldspec.nodes import _KINDED

    assert [m[0] for m in _KINDED.findall("**Decision `ch1-D1` — the window closes.**")] == ["ch1-D1"]
    assert [m[0] for m in _KINDED.findall("**Parameter `dev07-6-P1` — a window.**")] == ["dev07-6-P1"]
    # A sentence citing somebody else's subject is still not a declaration.
    assert _KINDED.findall("The argument turns on **the** other chapter's `ch3-U1`, which is open.") == []


# ---- the dotted-name rule runs one way per question (`spe5-sr07`) --------------------------------

PARENT = """# Chapter 1 — a customer places an order

**Last updated** 2026-09-15 v1

> **As a customer I want to place an order, so that I get the thing.**

```mermaid
flowchart TD
    START([START]):::terminal
    TAKE[ch1-1 take the order]:::process
    SUB[[ch1-2 assess it]]:::subroutine
    DONE([END]):::good
    START --> TAKE --> SUB --> DONE
    classDef terminal fill:#eee,stroke:#555,color:#000;
    classDef process fill:#eef,stroke:#27d,color:#000;
    classDef subroutine fill:#eef,stroke:#27d,color:#000;
    classDef good fill:#efe,stroke:#0a0,color:#000;
```

## Nodes

### ch1-1 · take the order

> **As a customer I want my order recorded, so that nothing is reconstructed later.**

#### Information

| Information | IO | Description | Required | Provenance |
|---|---|---|---|---|
| ch1-1-inf1 | In | `basket` | yes | authored |
| ch1-1-inf2 | Out | `order` | yes | derived |

#### User Requirements
  * ch1-1-ur1 - the order records what was chosen
#### System Requirements
#### Non-Functional Requirements
#### Unknowns

---

### ch1-2 · assess it

> **As a customer I want the order assessed, so that I am told before my card is touched.**

#### Information

| Information | IO | Description | Required | Provenance |
|---|---|---|---|---|
| ch1-2-inf1 | In | `order` | yes | ch1-1 |
| ch1-2-inf2 | Out | `verdict` | yes | derived |

#### User Requirements
  * ch1-2-ur1 - the assessment is made from the order
#### System Requirements
#### Non-Functional Requirements
#### Unknowns

## Glossary

| Term | Meaning |
|---|---|
| Order | A basket the shop accepted |
"""

CHILD = PARENT.replace("# Chapter 1 — a customer places an order",
                       "# Chapter 1.2 — assessing an order") \
              .replace("ch1-1", "ch1-2-1").replace("ch1-2 ·", "ch1-2-2 ·") \
              .replace("ch1-2-inf", "ch1-2-2-inf").replace("ch1-2-ur", "ch1-2-2-ur") \
              .replace("SUB[[ch1-2 assess it]]:::subroutine", "SUB[ch1-2-2 grade it]:::process") \
              .replace("`verdict`", "`order.grade`")


def _corpus(root, parent_text, neighbour_consumes):
    """A parent with a sub-flow, its child, and a neighbouring chapter that consumes something."""
    flows = root / "diagrams"
    flows.mkdir(parents=True)
    (flows / "chapter-01-ordering.md").write_text(parent_text, encoding="utf-8")
    (flows / "chapter-01.2-assessing.md").write_text(CHILD, encoding="utf-8")
    (flows / "chapter-09-elsewhere.md").write_text(
        PARENT.replace("# Chapter 1 —", "# Chapter 9 —").replace("ch1-", "ch9-")
              .replace("SUB[[ch9-2 assess it]]:::subroutine", "SUB[ch9-2 assess it]:::process")
              .replace("| ch9-1-inf1 | In | `basket` | yes | authored |",
                       f"| ch9-1-inf1 | In | `{neighbour_consumes}` | yes | authored |"),
        encoding="utf-8")
    return root


def test_taking_the_whole_elsewhere_is_not_a_demand_for_a_part(tmp_path):
    """`spe5-sr07`. A neighbour consuming `order` does not make `order.grade` need declaring.

    This read the rule backwards, so any chapter anywhere taking `order` made every `order.*` a
    child produced look wanted — and a parent was told to declare something because an unrelated
    flow took the whole. The fault surfaced in a file whose author had not touched it.
    """
    from goldspec.review import cross_flow

    root = _corpus(tmp_path / "whole", PARENT, "order")
    found = cross_flow(root / "diagrams" / "chapter-01-ordering.md",
                       sorted((root / "diagrams").glob("*.md")))
    assert not [f for f in found if "does not declare" in f], found


def test_taking_a_part_elsewhere_is_a_demand_the_parent_must_carry(tmp_path):
    """The other half, and the reason the check exists: a real escape still fires.

    Asserted beside the case above, because a fix that silences the false positive by silencing
    the check is indistinguishable from a fix until somebody loses a transit.
    """
    from goldspec.review import cross_flow

    root = _corpus(tmp_path / "part", PARENT, "order.grade")
    found = cross_flow(root / "diagrams" / "chapter-01-ordering.md",
                       sorted((root / "diagrams").glob("*.md")))
    assert [f for f in found if "does not declare" in f and "order.grade" in f], found
