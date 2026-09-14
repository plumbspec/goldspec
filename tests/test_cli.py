"""The command is a view over the gate's report, and `vie7` is what it owes.

> **No view may assert what its source does not** — a projection may summarize, aggregate and omit;
> it may never state a status, a completion, or a date the spec and its run do not support. The
> whole framework is worthless if the number shown upward is not the number the gate produced.

That is the story this file proves, and the defect it was written for is the literal reading of its
last clause: `main` read `report.faults`, an attribute `Report` does not define, through a `getattr`
default. The number shown upward was `0 fault(s)` for every spec ever checked. The number the gate
produced was whatever it actually found, and no caller could tell the two apart.

So the property asserted here is **correspondence**, not a worked example. A test that feeds in one
broken spec and asserts a non-zero exit is satisfied by a command hard-wired to fail, and would have
been satisfied by the broken one for the clean case too. What `vie7` asks for is that the view
carries its source upward *without alteration* — every problem, verbatim, in order, with a count
that matches and an exit code that agrees — and that is a property of every spec rather than of one.

**The data is organised by fault class**, one fixture per thing the gate can say, because a
correspondence proved only over specs that happen to be clean proves nothing. `test_every_fault_class_is_covered`
is what stops that set from silently falling behind the gate: it counts the classes in the gate's
own source and fails when one arrives here uncovered, which is the same *assert the check actually
checked* rule the gate already applies to itself one layer down.

**Two things the board says about this file are true, and neither is a defect to fix.**

`grounding.reached-outside` — the correspondence test drives the entry point *and* calls
`check_spec_directory` directly, so the grounding does not vouch for all of it, and the board
suggests splitting. Splitting is wrong here: the oracle has to be the live gate. The alternative is
a stored list of expected problems, which is the second copy this file exists to avoid, and it goes
stale in the direction that passes. The signal is accurate and accepted rather than silenced.

`22/57` mutants killed, and the shortfall is structural rather than slack. A correspondence is
invariant under mutations of the thing it compares against: change a message inside the gate and
both sides of the assertion change together, so the mutant lives. This property proves the view
faithful to its source and can never prove the source right. What pins the gate's own behaviour is
`EXPECTED` — the per-class substrings — and those assertions belong to no story yet. Read the score
as a floor on `vie7`, never as a verdict on the gate.
"""

import ast
import re
from pathlib import Path

import pytest

from goldspec.cli import main
from goldspec.conventions import CITATION_MARKER, conventions_for
from goldspec.specgate import check_spec_directory

SRC = Path(__file__).resolve().parent.parent / "src" / "goldspec"

#: The one clean chapter every fixture is derived from. There is one format, so there is one of
#: these; `CLEAN` and `CLEAN` are the same text under two names while callers are updated.
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

    classDef terminal fill:#eef0ee,stroke:#52514e,color:#0b0b0b;
    classDef process fill:#e9eef5,stroke:#2a78d6,color:#0b0b0b;
    classDef good fill:#e2f2e2,stroke:#0ca30c,color:#0b0b0b;
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

#: A conventions file naming the sibling, so a fixture that cites across a corpus resolves.
NODE_FORMAT_ON = '[conventions]\nsiblings = ["../neighbour"]\n'

#: The other half of that corpus. Read for the one name it defines and never checked, so it needs
#: to be no more than a table — which is also the smallest demonstration that a sibling may be in
#: either shape.
NEIGHBOUR = """# Chapter 3 — people

**Last updated** 2026-09-15 v1

> **As a shop I want the person behind an order recorded, so that there is somebody to tell.**

```mermaid
flowchart TD
    START([START]):::terminal
    WHO[ch3-1 record who asked]:::process
    DONE([END]):::good
    START --> WHO --> DONE

    classDef terminal fill:#eef0ee,stroke:#52514e,color:#0b0b0b;
    classDef process fill:#e9eef5,stroke:#2a78d6,color:#0b0b0b;
    classDef good fill:#e2f2e2,stroke:#0ca30c,color:#0b0b0b;
```

## Nodes

### ch3-1 · record who asked

> **As a shop I want the customer recorded, so that an order has somebody behind it.**

#### Information

| Information | IO | Description | Required | Provenance |
|---|---|---|---|---|
| ch3-1-inf1 | In | `enquiry` | yes | authored |
| ch3-1-inf2 | Out | `customer` | yes | derived |

#### User Requirements
  * ch3-1-ur1 - the customer is recorded against the order

#### System Requirements

#### Non-Functional Requirements

#### Unknowns

## Glossary

| Term | Meaning |
|---|---|
| Customer | The person an order belongs to |
"""


def nodes_case(text: str, with_neighbour: bool = True) -> dict:
    """A node-format spec tree: the chapter, the file that holds it to the format, and the corpus.

    `with_neighbour=False` drops the sibling and leaves the import naming a home that does not
    exist, which is its own fault class.
    """
    tree = {"spec/diagrams/chapter-01-example.md": text, "spec/goldspec.toml": NODE_FORMAT_ON}
    if with_neighbour:
        tree["neighbour/diagrams/chapter-03-people.md"] = NEIGHBOUR
    return tree

#: A parent whose `ch1-2` drills down, and the chapter that expands it. The cross-flow checks
#: compare the two, so a fixture for them is a pair rather than a file.
PARENT = CLEAN.replace(
    "    CHARGE[ch1-2 charge once]:::process",
    "    CHARGE[[ch1-2 charge once]]:::subroutine").replace(
    "    classDef good", "    classDef subroutine fill:#e9eef5,stroke:#2a78d6,color:#0b0b0b;\n"
                         "    classDef good")

CHILD = """# Chapter 1.2 — charging

**Last updated** 2026-09-15 v1

> **As a customer I want one charge, so that a retry costs me nothing.**

```mermaid
flowchart TD
    START([START]):::terminal
    ONE[ch1-2-1 take the reference]:::process
    TWO[ch1-2-2 charge against it]:::process
    DONE([END]):::good
    START --> ONE --> TWO --> DONE

    classDef terminal fill:#eef0ee,stroke:#52514e,color:#0b0b0b;
    classDef process fill:#e9eef5,stroke:#2a78d6,color:#0b0b0b;
    classDef good fill:#e2f2e2,stroke:#0ca30c,color:#0b0b0b;
```

## Nodes

### ch1-2-1 · take the reference

> **As the charging step I want the order's reference, so that the charge can be keyed by it.**

#### Information

| Information | IO | Description | Required | Provenance |
|---|---|---|---|---|
| ch1-2-1-inf1 | In | `order` | yes | parent |
| ch1-2-1-inf2 | Out | `reference` | yes | derived |

#### User Requirements
  * ch1-2-1-ur1 - the reference comes from the order rather than being minted here

#### System Requirements

#### Non-Functional Requirements

#### Unknowns


---

### ch1-2-2 · charge against it

> **As a customer I want the charge keyed to my order, so that a retry is the same charge.**

#### Information

| Information | IO | Description | Required | Provenance |
|---|---|---|---|---|
| ch1-2-2-inf1 | In | `reference` | yes | ch1-2-1 |
| ch1-2-2-inf2 | Out | `charge` | yes | observed |

#### User Requirements
  * ch1-2-2-ur1 - one order is charged once

#### System Requirements

#### Non-Functional Requirements

#### Unknowns

## Glossary

| Term | Meaning |
|---|---|
| Reference | The handle a charge is keyed by |
"""



#: A third chapter that reads what the child makes, so an element transiting the parent is one the
#: parent has to declare.
LEDGER = """# Chapter 2 — the ledger

**Last updated** 2026-09-15 v1

> **As a bookkeeper I want each charge against its reference, so that the books reconcile.**

```mermaid
flowchart TD
    START([START]):::terminal
    POST[ch2-1 post the charge]:::process
    DONE([END]):::good
    START --> POST --> DONE

    classDef terminal fill:#eef0ee,stroke:#52514e,color:#0b0b0b;
    classDef process fill:#e9eef5,stroke:#2a78d6,color:#0b0b0b;
    classDef good fill:#e2f2e2,stroke:#0ca30c,color:#0b0b0b;
```

## Nodes

### ch2-1 · post the charge

> **As a bookkeeper I want the charge posted under its reference, so that the books reconcile.**

#### Information

| Information | IO | Description | Required | Provenance |
|---|---|---|---|---|
| ch2-1-inf1 | In | `reference` | yes | authored |
| ch2-1-inf2 | Out | `posting` | yes | derived |

#### User Requirements
  * ch2-1-ur1 - every charge is posted under the reference it was keyed by

#### System Requirements

#### Non-Functional Requirements

#### Unknowns

## Glossary

| Term | Meaning |
|---|---|
| Posting | A line in the books |
"""


def subflow_case(parent: str = PARENT, child: str = CHILD, neighbour: str = None) -> dict:
    """A parent, the chapter it drills into, and optionally a third that reads what the child makes."""
    tree = {"spec/diagrams/chapter-01-example.md": parent,
            "spec/diagrams/chapter-01.2-charging.md": child,
            "spec/goldspec.toml": NODE_FORMAT_ON,
            "neighbour/diagrams/chapter-03-people.md": NEIGHBOUR}
    if neighbour is not None:
        tree["spec/diagrams/chapter-02-ledger.md"] = neighbour
    return tree




def with_row(text: str, row: str) -> str:
    """Append a trace row, which now sits mid-file rather than at the end."""
    return text.replace("\n\n## Input → process → output",
                        "\n" + row + "\n## Input → process → output", 1)

#: One fixture per thing the gate can say. The value is the spec tree: relative path -> content,
#: written under `tmp_path`, with the spec itself at `spec/`. Anything outside `spec/` is there to
#: be read as a citation source, which is `cited_from` in the CLI's own call.
CASES: dict[str, dict[str, str]] = {
    "clean": {
        "spec/diagrams/chapter-01-example.md": CLEAN,
    },
    "flow_without_a_start": {
        # A and B point at each other, so neither is a start; C is reached and reaches nothing,
        # so an end exists and only the start is missing.
        "spec/diagrams/chapter-01-example.md":
            CLEAN.replace("""    START([START]):::terminal
    TAKE[ch1-1 take the order]:::process
    CHARGE[ch1-2 charge once]:::process
    DONE([END]):::good
    START --> TAKE --> CHARGE --> DONE""",
                          "    A[a] --> B[b]\n    B --> A\n    B --> C[c]"),
    },
    "flow_without_an_end": {
        "spec/diagrams/chapter-01-example.md":
            CLEAN.replace("""    START([START]):::terminal
    TAKE[ch1-1 take the order]:::process
    CHARGE[ch1-2 charge once]:::process
    DONE([END]):::good
    START --> TAKE --> CHARGE --> DONE""",
                          "    A[a] --> B[b]\n    B --> C[c]\n    C --> B"),
    },
    "no_subjects": {
        # A flow directory with nothing the glob matches: the gate refuses to read this as a pass.
        "spec/diagrams/notes.md": "not a chapter, and not matched by chapter-*.md\n",
    },
    "rendering": {
        "spec/diagrams/chapter-01-example.md":
            CLEAN.replace("TAKE[ch1-1 take the order]:::process",
                          "TAKE[ch1-1 take the order]:::nosuchclass"),
    },
    "bare_delimiter": {
        "spec/diagrams/chapter-01-example.md":
            CLEAN.replace("TAKE[ch1-1 take the order]", "TAKE[ch1-1 take the order (once)]"),
    },
    "classdef_without_colour": {
        "spec/diagrams/chapter-01-example.md":
            CLEAN.replace("    TAKE[ch1-1 take the order]:::process",
                          "    TAKE[ch1-1 take the order]:::process\n"
                          "    classDef process fill:#e9eef5,stroke:#2a78d6;"),
    },

    # ---- the node format (`ch16`), which needs the flag as well as the chapter ----------------
    "node_clean": nodes_case(CLEAN),
    "node_sections_incomplete": nodes_case(
        CLEAN.replace("#### System Requirements\n", "")),
    "requirement_named_for_another_node": nodes_case(
        CLEAN.replace("* ch1-1-ur1 -", "* ch9-9-ur1 -")),
    "requirement_stated_twice": nodes_case(CLEAN.replace(
        "  * ch1-2-ur1 - a retry charges nothing a second time",
        "  * ch1-1-ur1 - a retry charges nothing a second time")),
    "colours_by_build_status": nodes_case(CLEAN.replace(
        "    classDef good", "    classDef done fill:#e2f2e2,stroke:#0ca30c,color:#0b0b0b;\n"
                             "    classDef good")),
    "subflow_parent_hides_a_transit": subflow_case(
        parent=PARENT.replace("| ch1-2-inf2 | Out | `charge` | yes | observed |\n", ""),
        neighbour=LEDGER.replace("| ch2-1-inf1 | In | `reference` | yes | authored |",
                                 "| ch2-1-inf1 | In | `charge` | yes | authored |")),
    "subject_declared_twice": {
        "spec/diagrams/chapter-01-example.md": CLEAN,
        "spec/diagrams/chapter-01.9-again.md": CLEAN.replace(
            "# Chapter 1 — a customer places an order", "# Chapter 1.9 — the same ids again"),
        "spec/goldspec.toml": NODE_FORMAT_ON,
        "neighbour/diagrams/chapter-03-people.md": NEIGHBOUR,
    },
    "cited_and_declared_nowhere": {
        "spec/diagrams/chapter-01-example.md": CLEAN,
        "spec/goldspec.toml": NODE_FORMAT_ON,
        "neighbour/diagrams/chapter-03-people.md": NEIGHBOUR,
        "tests/test_something.py": (
            "import pytest\n\n\n"
            "@pytest.mark.proves(\"ch1-9\")\ndef test_a_subject_nobody_wrote_down():\n    pass\n"),
    },
    "subflow_parent_short": subflow_case(
        child=CHILD.replace("| ch1-2-1-inf1 | In | `order` | yes | parent |",
                            "| ch1-2-1-inf1 | In | `token` | yes | parent |")),
    "subflow_parent_overclaims": subflow_case(
        parent=PARENT.replace("| ch1-2-inf2 | Out | `charge` | yes | observed |",
                              "| ch1-2-inf2 | Out | `receipt` | yes | observed |")),
    "subflow_parent_takes_unused": subflow_case(
        parent=PARENT.replace("| ch1-2-inf1 | In | `order` | yes | ch1-1 |",
                              "| ch1-2-inf1 | In | `order` | yes | ch1-1 |\n"
                              "| ch1-2-inf9 | In | `basket` | optional | ch1-1 |")),
    "restates_a_step": nodes_case(CLEAN.replace(
        "| ch1-1-inf1 | In | `basket` | yes | authored |",
        "| ch1-1-inf1 | In | take the order from the customer | yes | authored |")),
    "subflow_expanded_nowhere": nodes_case(CLEAN.replace(
        "    CHARGE[ch1-2 charge once]:::process",
        "    CHARGE[[ch1-2 charge once]]:::subroutine")),
    # ---- the process checks, each driving one class -------------------------------------------
    "chain_break": nodes_case(CLEAN.replace(
        "| ch1-2-inf1 | In | `order` | yes | ch1-1 |",
        "| ch1-2-inf1 | In | `order` | yes | ch1-1 |\n"
        "| ch1-2-inf3 | In | `coupon` | yes | ch1-1 |")),
    "attributed_figure": nodes_case(CLEAN.replace(
        "> charged for something that is actually coming.**",
        "> charged for something that is actually coming.**\n\n"
        "Measured on a customer's suite: 308 orders a second.")),
    "unpadded_series": nodes_case(CLEAN.replace(
        "| ch1-1-inf2 | Out | `order` | yes | derived |",
        "| ch1-1-inf2 | Out | `order` | yes | derived |\n"
        "| ch1-1-inf10 | Out | `receipt` | optional | derived |")),
    "no_stamp": nodes_case(CLEAN.replace("\n**Last updated** 2026-09-15 v1\n", "")),
    "reports_build_status": nodes_case(CLEAN.replace(
        "  * ch1-1-ur1 - the basket is recorded as the customer chose it",
        "  * ch1-1-ur1 - the basket is recorded as the customer chose it, and nothing "
        "implements one")),
    "carries_its_own_proof": nodes_case(CLEAN.replace(
        "## Glossary",
        "| test method | subject |\n|---|---|\n| takesTheOrder | ch1-1 |\n\n## Glossary", 1)),
    "provenance_missing": nodes_case(CLEAN.replace(
        "| ch1-1-inf1 | In | `basket` | yes | authored |",
        "| ch1-1-inf1 | In | `basket` | yes |  |")),
    "provenance_out_is_not_a_way_of_making": nodes_case(CLEAN.replace(
        "| ch1-1-inf2 | Out | `order` | yes | derived |",
        "| ch1-1-inf2 | Out | `order` | yes | ch1-1 |")),
    "provenance_names_no_step": nodes_case(CLEAN.replace(
        "| ch1-2-inf1 | In | `order` | yes | ch1-1 |",
        "| ch1-2-inf1 | In | `order` | yes | ch9-9 |")),
    "provenance_step_does_not_produce_it": nodes_case(CLEAN.replace(
        "| ch1-1-inf1 | In | `basket` | yes | authored |",
        "| ch1-1-inf1 | In | `basket` | yes | ch1-2 |")),
    "provenance_flow_does_not_reach": nodes_case(CLEAN.replace(
        "| ch1-1-inf1 | In | `basket` | yes | authored |",
        "| ch1-1-inf1 | In | `charge` | yes | ch1-2 |")),
    "prohibition_as_a_step": nodes_case(CLEAN.replace(
        "### ch1-2 · charge once", "### ch1-2 · never charge twice").replace(
        "CHARGE[ch1-2 charge once]", "CHARGE[ch1-2 never charge twice]").replace(
        "| ch1-2-inf2 | Out | `charge` | yes | observed |\n", "")),
    "node_sections_out_of_order": nodes_case(
        CLEAN.replace("## Nodes", "## Glossary\n\n## Nodes", 1)),
    "node_chapter_with_no_nodes": nodes_case(
        CLEAN.split("## Nodes")[0] + "## Nodes\n\n## Glossary\n"),
    "node_not_namespaced": nodes_case(CLEAN.replace("### ch1-2 ·", "### ch2-9 ·")),
    "node_expanded_twice": nodes_case(CLEAN.replace(
        "## Glossary",
        "### ch1-1 · take the order again\n\n#### Information\n\n"
        "| Information | IO | Description | Required | Provenance |\n|---|---|---|---|---|\n"
        "| ch1-1-inf9 | In | `order` | yes | ch1-1 |\n\n## Glossary", 1)),
    "node_moves_nothing": nodes_case(CLEAN.replace(
        "| ch1-2-inf1 | In | `order` | yes | ch1-1 |\n"
        "| ch1-2-inf2 | Out | `charge` | yes | observed |\n", "")),
    "node_kinded_id_not_namespaced": nodes_case(CLEAN.replace("`ch1-D1`", "`ch9-D1`")),
    "node_drawn_and_never_expanded": nodes_case(
        CLEAN.replace("    DONE([END]):::good",
                            "    REFUND[ch1-3 refund]:::process\n    DONE([END]):::good")
        .replace("CHARGE --> DONE", "CHARGE --> REFUND --> DONE")),
    "node_expanded_and_not_in_the_flow": nodes_case(
        CLEAN.replace("    CHARGE[ch1-2 charge once]:::process\n", "")
        .replace("START --> TAKE --> CHARGE --> DONE", "START --> TAKE --> DONE")),
}

#: Classes the command cannot reach, each with the reason it cannot.
#:
#: **Listing is not excusing.** A class lands here only with a reason, and the count below still
#: has to add up, so a new class cannot arrive unnoticed by being quietly unreachable.
#:
#: One entry. `review.unconsumed` is an **observation** rather than a check: it reports an element
#: nothing downstream takes, which is a flow's product about as often as it is waste, so it is
#: counted on every run and never made a fault. No fixture can drive it through `main` as a
#: problem, because nothing can. Everything else the gate carries runs through the command on
#: every spec, so a class this file cannot trigger is a class nothing exercises.
FLAG_GATED: set[str] = {"leaves with ... which nothing in ... takes"}

#: What each fixture is here to make the gate say. Matched as a substring of one problem, so the
#: wording may be improved without this file objecting — only the class disappearing fails it.
EXPECTED: dict[str, str] = {
    "no_subjects": "declares no subjects at all",
    "flow_without_a_start": "the flow has no start",
    "flow_without_an_end": "the flow has no end",
    "rendering": "no classDef defines it",
    "bare_delimiter": "inside an unquoted label",
    "classdef_without_colour": "sets no `color:`",
    "node_sections_out_of_order": "not ['Nodes', 'Glossary']",
    "node_chapter_with_no_nodes": "a Nodes section that declares no nodes",
    "node_not_namespaced": "expected ch1-<n>, so a citation from another chapter",
    "node_expanded_twice": "is expanded more than once",
    "node_moves_nothing": "states no information at all",
    "node_kinded_id_not_namespaced": "#ch9-D1 is not namespaced to its chapter",
    "node_drawn_and_never_expanded": "is drawn in the flow and has no node block",
    "node_expanded_and_not_in_the_flow": "has a node block and is not in the flow",
    "chain_break": "which no earlier step produces",
    "attributed_figure": "attributes a figure",
    "unpadded_series": "where the largest needs",
    "no_stamp": "no stamp under the title",
    "reports_build_status": "reports its own build status",
    "colours_by_build_status": "colours the diagram by build status",
    "node_sections_incomplete": "a reader looking for what constrains a step",
    "requirement_named_for_another_node": "a constraint is filed on the step it constrains",
    "requirement_stated_twice": "is stated more than once",
    "carries_its_own_proof": "names the test that proves it",
    "provenance_missing": "does not say where",
    "provenance_out_is_not_a_way_of_making": "which is not a way a step makes something",
    "provenance_names_no_step": "which is neither a step of this chapter",
    "provenance_step_does_not_produce_it": "which does not produce it",
    "provenance_flow_does_not_reach": "which the flow does not reach it from",
    "prohibition_as_a_step": "produces nothing and reads as a prohibition",
    "restates_a_step": "names a step this chapter already has",
    "subflow_expanded_nowhere": "is drawn as a sub-flow and no chapter expands it",
    "subflow_parent_short": "which the chapter it drills into needs and cannot make for itself",
    "subflow_parent_overclaims": "claims to leave with",
    "subflow_parent_takes_unused": "which no step of the chapter it drills into consumes",
    "subflow_parent_hides_a_transit": "does not declare",
    "subject_declared_twice": "has more than one trace row",
    "cited_and_declared_nowhere": "declared nowhere in spec/",
}


def _write(root: Path, tree: dict) -> Path:
    for relative, text in tree.items():
        path = root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
    return root / "spec"


def _build(root: Path, case: str) -> Path:
    return _write(root, CASES[case])


def _gate(spec: Path):
    """The oracle, built the way the command builds it.

    Through `conventions_for` rather than a `Conventions(...)` written here, because a fixture may
    carry a `goldspec.toml` — the node-format cases do, since that flag is what decides whether a
    node fault is a problem at all. Constructed by hand, the oracle would judge those fixtures under
    conventions the command never uses, and the correspondence test would fail on a difference in
    *configuration* while reporting it as the view altering its source.
    """
    return check_spec_directory(spec, conventions_for(spec), cited_from=spec.parent)


@pytest.mark.proves("vie7", depth="wiring")
@pytest.mark.parametrize("case", sorted(CASES))
def test_the_command_says_exactly_what_the_gate_found(case, tmp_path, capsys):
    """`vie7` — every problem carried upward verbatim, in order, counted and exited on.

    Asserted against the gate's own report rather than against a list written here, because a
    second copy of the expected problems is the authored status this method exists to remove: it
    would go stale the moment a message is reworded, and the direction it goes stale in is the
    dangerous one — a shorter expectation passes.
    """
    spec = _build(tmp_path, case)
    expected = _gate(spec).problems

    code = main([str(spec)])
    printed = capsys.readouterr().out.splitlines()

    assert printed[:-1] == expected, (
        "the command did not carry the gate's problems upward unaltered — a view stating something "
        f"its source does not is vie7's one prohibition:\n  gate said: {expected}\n"
        f"  command said: {printed[:-1]}")
    assert printed[-1] == f"{len(expected)} fault(s) in {spec}", (
        "the number shown upward is not the number the gate produced, which is the sentence vie7 "
        f"ends on:\n  {printed[-1]}\n  gate found {len(expected)}")
    assert code == (1 if expected else 0), (
        f"the exit code disagrees with what was printed: {len(expected)} problem(s), exit {code}. "
        "A gate read by a script is read through this number and nothing else")


@pytest.mark.parametrize("case", sorted(EXPECTED))
def test_each_fixture_still_produces_the_fault_it_is_here_for(case, tmp_path):
    """The correspondence test passes vacuously against a spec that stopped being broken.

    Every fixture above is hand-written, and a gate whose wording or parsing moves can quietly stop
    finding the thing one was built to trigger. Correspondence would still hold — nothing printed,
    nothing expected, zero equals zero — and the class would be untested with every test green.
    """
    problems = _gate(_build(tmp_path, case)).problems

    assert any(EXPECTED[case] in problem for problem in problems), (
        f"the {case!r} fixture no longer makes the gate say {EXPECTED[case]!r}, so the "
        f"correspondence proved for it is proved over a clean spec:\n{problems}")


def test_no_fixture_is_broken_by_accident(tmp_path):
    """The clean case must be clean, or the suite cannot tell a fault from a fixture."""
    assert _gate(_build(tmp_path, "clean")).problems == []


#: The lists a fault message is appended to. `report.problems` is the gate's own; the other three
#: are the local names `datadef`, `nodes` and `flowcheck` collect into before handing back.
FAULT_LISTS = {"problems", "found", "conflicting", "duplicated"}


def authored_fault_classes(module: Path) -> int:
    """How many distinct fault messages one module writes.

    Parsed rather than grepped, and this is the fourth shape of a guard that has been too narrow
    three times. It first counted only `.append(` and missed the `+=` family; it then counted only
    `specgate` while eight data-definition classes were being written in `datadef`; then `nodes`
    arrived with eleven classes and `flowcheck` with three, and the count carried a literal `+ 1`
    for the whole of `flowcheck` and nothing at all for `nodes` — so the node format shipped with
    every one of its checks outside this guard.

    A regex cannot survive that, because each fix was a new spelling: a different list name, a
    wrapped call, an argument on the next line.

    **Counting only `.append` was the fourth time it was too narrow**, and the checks moved out
    from under it: a check that `return`s a list comprehension of f-strings emits exactly as many
    classes as one that appends them, and eleven of them had become invisible here. So what is
    counted is the *message* — a string or an f-string that becomes an element of a list this
    module hands back as faults — however it gets there.
    """
    tree = ast.parse(module.read_text(encoding="utf-8"))

    def is_message(node) -> bool:
        # A message, not a record: a node appending `Element(...)` to a list it happens to call
        # `found` is a parse step, and counting it would demand a fixture for something that
        # reports nothing.
        return isinstance(node, ast.JoinedStr) or (
            isinstance(node, ast.Constant) and isinstance(node.value, str))

    faults = 0
    for node in ast.walk(tree):
        # Appended to a list of faults …
        if (isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute)
                and node.func.attr == "append" and node.args):
            target = node.func.value
            name = target.attr if isinstance(target, ast.Attribute) else getattr(target, "id", None)
            if name in FAULT_LISTS and is_message(node.args[0]):
                faults += 1
            continue
        # … or built inline: returned, assigned to a fault list, or added to one. All three are the
        # same act, and counting only the first spelling is how eleven classes went unexercised.
        built = None
        if isinstance(node, ast.Return):
            built = node.value
        elif isinstance(node, (ast.Assign, ast.AugAssign)):
            targets = node.targets if isinstance(node, ast.Assign) else [node.target]
            named = {t.id for t in targets if isinstance(t, ast.Name)}
            if named & FAULT_LISTS:
                built = node.value
        if isinstance(built, ast.ListComp):
            faults += 1 if is_message(built.elt) else 0
        elif isinstance(built, ast.List):
            faults += sum(1 for part in built.elts if is_message(part))
    return faults


def test_every_fault_class_is_covered():
    """A class the gate can emit and this file cannot trigger is an untested branch.

    Counted out of the gate's own source across every module of it, so a class arriving in a module
    this file has never heard of fails here rather than shipping unexercised — which is exactly
    what happened to the eleven node-format classes and two of flowcheck's three.
    """
    emitted = sum(authored_fault_classes(module) for module in sorted(SRC.glob("*.py")))
    # Distinct *classes*, not fixtures: several fixtures may drive one class, and counting cases
    # would make adding a second route to an already-covered fault look like a coverage gain.
    covered = set(EXPECTED.values())

    assert len(covered) + len(FLAG_GATED) == emitted, (
        f"the gate emits {emitted} fault class(es); this file has data for {len(covered)} and "
        f"records {len(FLAG_GATED)} as unreachable from the command. An uncovered class is a "
        "branch nothing here would notice breaking — add a fixture, or say why it cannot fire")


# ---- the same faults, through the entry point ------------------------------------------------
#
# `test_nodes.py` proves the library: it calls `read()` and `faults()` and asserts what they
# return. That is a real test and it is not evidence the story holds where it is used — the board
# said so, in as many words: *every citation passed, and none of them reached the wired system*.
# A gate's subjects are about the gate, and the gate is reached through `main`.
#
# So the citations live here, at wiring depth, on tests that hand argv to the command and read
# stdout and the exit code back. The library tests keep the same coverage and cite nothing.


def run(case, tmp_path, capsys):
    """Drive the command over a fixture and return what a caller would see."""
    spec = _build(tmp_path, case)
    code = main([str(spec)])
    return code, capsys.readouterr().out









# ---- the node format, through the same entry point -------------------------------------------
#
# `spe` describes the format `nodes.py` implements, and `test_nodes.py` proves that module by
# calling it. The chapter's subjects are about what an
# author is held to, and an author is held to it by running the command, so the citations are here.
#
# Three of the ten nodes are cited by nothing, and deliberately. `spe4` is the closing argument,
# which carries no id and is checked by no one — that is `spe4-nfr1`, stated rather than papered over.
# `spe1` is the page-length rule, whose threshold is `spe1-nfr1` and unmeasured, so the gate holds
# nobody to it. `ent5` is the conversion, which is a guide rather than a check; `test_docs.py`
# holds the guide and its worked pair together. An absent subject is the honest reading of all three.


@pytest.mark.proves("spe1", depth="wiring")
def test_the_command_requires_a_flow_that_starts_and_ends(tmp_path, capsys):
    """`spe1` — draw it first, because a box has to connect to something.

    The two fixtures are a cycle with nothing entering it and a cycle with nothing leaving it,
    which is what a step half-mentioned in prose looks like once it has to be a box.
    """
    for case, expected in (("flow_without_a_start", "the flow has no start"),
                           ("flow_without_an_end", "the flow has no end")):
        code, out = run(case, tmp_path / case, capsys)
        assert code != 0 and expected in out, f"{case}: {out}"



@pytest.mark.proves("spe2", depth="wiring")
def test_the_command_holds_the_drawing_and_the_expansion_together(tmp_path, capsys):
    """`spe2` — both failures, because they are opposite and only one of them looks wrong.

    A step drawn and never expanded leaves a diagram that looks complete, which is the half that
    goes unnoticed; a block with no box is a step nothing reaches.
    """
    for case, expected in (
            ("node_drawn_and_never_expanded", "is drawn in the flow and has no node block"),
            ("node_expanded_and_not_in_the_flow", "has a node block and is not in the flow")):
        code, out = run(case, tmp_path / case, capsys)
        assert code != 0 and expected in out, f"{case}: {out}"



@pytest.mark.proves("spe4", depth="wiring")
def test_the_command_namespaces_a_parameter_and_a_decision_to_their_chapter(tmp_path, capsys):
    """`spe4` — the id exists so a room can point at the same constraint, which needs it to
    resolve from outside the chapter that wrote it."""
    code, out = run("node_kinded_id_not_namespaced", tmp_path, capsys)
    assert code != 0 and "#ch9-D1 is not namespaced to its chapter" in out, out


@pytest.mark.proves("spe5", depth="wiring")
def test_the_command_holds_the_sections_in_order(tmp_path, capsys):
    """`spe5` — the set and the order both, and a Nodes section that states no nodes."""
    for case, expected in (
            ("node_sections_out_of_order", "not ['Nodes', 'Glossary']"),
            ("node_chapter_with_no_nodes", "a Nodes section that declares no nodes")):
        code, out = run(case, tmp_path / case, capsys)
        assert code != 0 and expected in out, f"{case}: {out}"



@pytest.mark.proves("ent6", depth="wiring")
def test_a_finding_in_a_flow_chapter_fails_the_command(tmp_path, capsys):
    """`ent6` — a chapter written as a flow is held to what a flow owes, through `main`.

    Through the command rather than the library, because what a corpus actually meets is the exit
    code. There is no flag between the finding and the fault: a chapter that has adopted the format
    is checked against it, and one that has not never reaches these checks at all.
    """
    broken = CLEAN.replace("| ch1-2-inf1 | In | `order` | yes | ch1-1 |",
                                 "| ch1-2-inf1 | In | `order` | yes | ch1-1 |\n"
                                 "| ch1-2-inf3 | In | `coupon` | yes | ch1-1 |")

    code = main([str(_write(tmp_path / "on", nodes_case(broken)))])
    out = capsys.readouterr().out

    assert code != 0 and "coupon" in out, \
        f"a finding in a converted chapter is not a fault:\n{out}"