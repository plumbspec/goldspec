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
