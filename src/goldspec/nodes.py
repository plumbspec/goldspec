"""The node format — information and data live with the node that moves them.

**Why this exists.** A chapter used to carry one `## Input → process → output` section and one
`## Data definitions` table for the whole flow. That is the wrong altitude, and the symptom is
measurable: with nowhere per-node to put what a step consumes, what it holds and what constrains it,
all of it backs up into the claim. A trace row can reach **486 words** against a chapter average of
161, with twelve separate things wearing one id — a
claim, a decision, three pieces of history, a reading, a cross-reference, two constraints, and two
steps that had never been drawn because there was no flow for them to be steps in.

So a node owns its story, and beneath it the information it moves. The chapter keeps one element
list, because an element is defined once for the corpus (`ent2`) and a per-node table would be a
second home for every element more than one node touches. A node **references**; it never defines.

**What that buys, beyond tidiness.** Each node's In/Held/Out is a citable subject, so *does this step
have the information it needs* stops being a thing a reviewer checks and becomes a thing a run
derives. And an element's producers and consumers are then already stated, which makes the data-flow
diagram derivable rather than drawn — nobody maintains it, and an element produced by no node or
consumed by none is a dangling half-edge the gate can name.

**Reporting before gating.** Every corpus that exists predates this format. A gate demanding it would
fail all of them on the release that introduced it, so a chapter without a `## Nodes` section is read
the old way and counted, and never reaches the checks these chapters are held to. The
default flips when the corpora are converted. `spe3` is why this paragraph exists: a check that is
stated and not enforced has to say which it is.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path


#: The sections a node-format chapter carries, in the order they must appear.
#:
#: `## Elements` and `## Nodes` replace the older `## Story → test trace`, `## Input → process →
#: output` and `## Data definitions`; the last two are unchanged. Order is checked for the same
#: reason `spe3` checks it: a glossary is looked up rather than read through, and the only reliable
#: way to be findable is to be in the same place every time.
SECTIONS = ("Nodes", "Glossary")

#: The `####` headings inside a node block, in the order they must appear. Information first
#: because a reader asks *what does this step take* before *what constrains it*; the three kinds of
#: requirement apart because each is argued with by a different reader; unknowns last because a
#: question is read after the claim it hangs off.
NODE_SECTIONS = ("Information", "User Requirements", "System Requirements",
                 "Non-Functional Requirements", "Unknowns")

#: The id suffix each requirement kind carries. A row is `inf`, and it is parsed with the table.
KINDS = {"User Requirements": "ur", "System Requirements": "sr",
         "Non-Functional Requirements": "nfr", "Unknowns": "u"}

#: A trailing section a chapter may carry and a gate ignores. It says of itself that it is not part
#: of the chapter, which is what makes ignoring it honest rather than lenient.
WORKING_NOTES = "Working notes"

#: A row of the five-column information table:
#: `| dev1-inf2 | In | \`order\` | yes | dev0 |`. The shape that replaced `| **In** | ... |`,
#: and the reason a row carries its own id is that a constraint on one piece of information is a
#: thing a room has to be able to point at.
_INFO_ROW = re.compile(
    r"^\|\s*(([\w.-]+?)-inf\d+)\s*\|\s*(In|Out|Process)\s*\|\s*([^|]*?)\s*\|"
    r"\s*([^|]*?)\s*\|\s*([^|]*?)\s*\|",
    re.M | re.I)

#: A node opens a `###` block and carries its id first: `### ch1-2 · check availability`.
#: The id may be backticked or not; the separator may be `·`, `—` or `-`.
_NODE = re.compile(r"^###\s+`?([A-Za-z]+\d[\w.\-]*\d|[A-Za-z]+\d)`?\s*[·—-]?\s*(.*)$", re.M)

#: An id that is a decision or a parameter rather than a story, **where the node declares it**:
#: `**Decision \`ch1-D1\` — the window closes at 02:00, so nothing may assume same-day.**`
#:
#: The run-in is what makes it a declaration. Matched anywhere in the block, this read every
#: *mention* as one, so a closing paragraph citing another chapter's unknown — `ch3-U1`, `ent4-u1`,
#: the ordinary way one node points at a decision another chapter owns — was reported as an id not
#: namespaced to its chapter. The prose was right and the gate was wrong, and it fired the first
#: time a converted chapter cited across chapters at all.
#:
#: `[^*]*` is what pins it: the id has to sit inside the *first* bold run of the line, before any
#: other emphasis, which is the shape both a parameter and a decision are written in and the shape a
#: sentence about somebody else's unknown never has.
_KINDED = re.compile(r"^\*\*[^*]*`([A-Za-z]+\d+(?:-\d+)*-([PUD])\d+)`", re.M)

#: The node's story — the blockquote under its heading, one or more lines of `> `.
_STORY = re.compile(r"^> (.+(?:\n> .+)*)", re.M)

#: A `####` heading inside a node block.
_NODE_SECTION = re.compile(r"^#### (.+?)\s*$", re.M)

#: One requirement or unknown: `  * spe1-ur3 - the flow is drawn before any step is described`.
_REQUIREMENT = re.compile(r"^\s*\*\s+((([\w.-]+?)-(ur|sr|nfr|u))\d+)\s*-\s*(.+)$", re.M)

_H2 = re.compile(r"^## ", re.M)
_H3 = re.compile(r"^### ", re.M)


def names_in(description: str) -> tuple:
    """What one Information row names.

    Backticked element names where the row has them; otherwise the description itself. A row may
    legitimately name a thing the corpus does not define — *the team's own backlog* — and that row
    still moves something, still has a provenance, and still has to chain.
    """
    found = re.findall(r"`([^`]+)`", description)
    if found:
        return tuple(found)
    text = description.strip()
    return (text,) if text and text != "—" else ()


@dataclass(frozen=True)
class Requirement:
    """One requirement or unknown, read once with the node that carries it."""

    node_id: str
    id: str
    #: ``ur`` · ``sr`` · ``nfr`` · ``u``
    kind: str
    text: str


@dataclass(frozen=True)
class Row:
    """One row of a node's Information table, read once and shared.

    **This type exists so nothing reads the table twice.** The parser and the checks each used to
    scan the markdown for themselves, against a regex each module kept its own copy of, and they
    disagreed: one fell back to the description where a row named no element and the other did not,
    so a row saying *the team's list of what is in flight* was a consumed thing nothing could ever
    supply. A shared rule was not enough, because two readings of one row can still diverge in what
    they do with it. A shared *object* cannot.
    """

    node_id: str
    row_id: str
    #: ``In`` or ``Out``, normalised.
    io: str
    description: str
    #: What the row names, by the one rule above.
    names: tuple
    required: str
    provenance: str

    @property
    def is_in(self) -> bool:
        return self.io == "In"


@dataclass(frozen=True)
class Node:
    """One step. A user story, and the information it moves.

    What it moves is its ``rows`` and nothing else — ``consumes`` and ``produces`` are derived from
    them, so there is no second place for a caller to disagree with.
    """

    id: str
    title: str
    #: The node's Information table, parsed once.
    rows: tuple = ()
    #: The constraints and open questions stated under this node.
    requirements: tuple = ()
    #: The `####` headings this node carries, in the order it carries them.
    sections: tuple = ()
    #: Ids of the decisions and parameters stated under this node.
    kinded: tuple = ()
    #: The blockquote under the heading — *as a role I want something so that a goal*. What the old
    #: trace row's claim became, and the reason a backlog is still readable off a converted chapter:
    #: the title says what the step is called and only this says what somebody wants.
    story: str = ""

    @property
    def consumes(self) -> tuple:
        return tuple(n for row in self.rows if row.is_in for n in row.names)

    @property
    def produces(self) -> tuple:
        return tuple(n for row in self.rows if not row.is_in for n in row.names)

    @property
    def touches(self) -> set:
        return set(self.consumes) | set(self.produces)


@dataclass(frozen=True)
class Chapter:
    """One chapter, read once. ``None`` from :func:`read` where a chapter is not in this format.

    **This is the hand-off, and it is the only one.** The tool this method is delivered beside
    learned the same lesson from the other end: an adapter watches a run once and emits a manifest,
    the core derives every status from that manifest, and nothing downstream is allowed to go back
    and observe for itself — because two observers of one run are two answers waiting to differ.

    A chapter is the same shape of problem. The markdown is read here, once, into nodes, rows and
    the flow's edges; every check is a pure function of what this carries. A check that re-scanned
    the source would be a second observer, and the first thing two of them did was disagree about
    what a row names.

    ``text`` is here for the checks that genuinely read prose — a stamp, an attribution, a claim
    about build status. They read it *from here* rather than opening the file again, so there is
    still one read.
    """

    path: Path
    nodes: tuple = ()
    #: The chapter's own source, so a prose check needs no second read.
    text: str = ""
    #: The flow: ``var -> {var}`` edges, and the ``var -> node id`` the diagram declares.
    edges: dict = field(default_factory=dict)
    var2id: dict = field(default_factory=dict)
    #: Ids the diagram draws as a drill-down, so nothing has to re-read the shapes.
    subflows: tuple = ()

    @property
    def name(self) -> str:
        return self.path.name

    @property
    def id2var(self) -> dict:
        return {v: k for k, v in self.var2id.items()}



def _mermaid(text: str) -> str:
    return "\n".join(re.findall(r"```mermaid(.*?)```", text, re.S))


def read_flow(text: str) -> tuple[dict, dict, tuple]:
    """``(edges, var -> node id, ids drawn as sub-flows)`` from the chapter's mermaid block."""
    mer = _mermaid(text)
    # The id may be bold or bare. Requiring `<b>` read every diagram that did not use it as naming
    # no nodes at all — and a check whose input is silently empty passes without comparing anything,
    # which is the failure this whole module is arranged to prevent.
    var2id = {}
    for m in re.finditer(r"^\s{4}(\w+)\s*[\[\({>]+\s*(?:<b>)?\s*([A-Za-z]+\d[\w.-]*)", mer, re.M):
        var2id.setdefault(m.group(1), m.group(2))
    edges: dict[str, set] = {}
    for line in mer.splitlines():
        line = re.sub(r"\|[^|]*\|", " ", line)          # edge labels are not node names
        if "-->" not in line:
            continue
        hops = [h.strip() for h in line.strip().split("-->")]
        for a, b in zip(hops, hops[1:]):
            if re.fullmatch(r"\w+", a) and re.fullmatch(r"\w+", b):
                edges.setdefault(a, set()).add(b)
    subflows = tuple(sorted(
        {m.group(1) for m in
         re.finditer(r"^\s{4}\w+\[\[\s*(?:<b>)?\s*([A-Za-z]+\d[\w.-]*)", mer, re.M)}))
    return edges, var2id, subflows


def _section(text: str, title: str) -> str | None:
    """The body of one `##` section, or ``None``."""
    opened = re.search(rf"^## {re.escape(title)}\s*$", text, re.M)
    if not opened:
        return None
    rest = text[opened.end():]
    nxt = _H2.search(rest)
    return rest[:nxt.start()] if nxt else rest




def read(path: Path) -> Chapter | None:
    """Parse a chapter written in the node format, or ``None`` if it is not in it.

    Detection is the presence of a `## Nodes` section and nothing cleverer. A chapter half-converted
    is not a state to guess at: it either states its nodes or it does not.
    """
    text = Path(path).read_text(encoding="utf-8")
    nodes_body = _section(text, "Nodes")
    if nodes_body is None:
        return None

    nodes = []
    starts = [(m.start(), m.group(1), m.group(2).strip()) for m in _NODE.finditer(nodes_body)]
    for i, (at, node_id, title) in enumerate(starts):
        end = starts[i + 1][0] if i + 1 < len(starts) else len(nodes_body)
        block = nodes_body[at:end]
        # The table, read once. Everything downstream reads these rows rather than the markdown.
        rows = tuple(
            Row(owner, row_id, "In" if io.lower() == "in" else "Out", desc.strip(),
                names_in(desc), required.strip(), provenance.strip())
            for row_id, owner, io, desc, required, provenance in _INFO_ROW.findall(block))
        told = _STORY.search(block)
        story = " ".join(line.lstrip("> ") for line in told.group(0).splitlines()) if told else ""
        requirements = tuple(
            Requirement(owner, rid, kind, body.strip())
            for rid, _stem, owner, kind, body in _REQUIREMENT.findall(block))
        sections = tuple(_NODE_SECTION.findall(block))
        nodes.append(Node(node_id, title, rows,
                          requirements, sections,
                          tuple(sorted({m[0] for m in _KINDED.findall(block)})),
                          story.replace("**", "").strip()))

    edges, var2id, subflows = read_flow(text)
    return Chapter(Path(path), tuple(nodes), text, edges, var2id, subflows)


def faults(chapter: Chapter, prefix: str, in_flow: set) -> list:
    """What is wrong with one node-format chapter.

    ``in_flow`` is the set of ids the chapter's process flow draws, so a node the flow does not
    carry and a node drawn but never expanded are both nameable.

    What a step moves is **not** checked against a list here. It is stated in the row that moves it,
    with a provenance, and what answers *does this arrive from anywhere* is the chain, the
    provenance and the cross-flow checks in `review`.
    """
    found = []
    name = chapter.path.name

    headings = re.findall(r"^## (.+?)\s*$", chapter.path.read_text(encoding="utf-8"), re.M)
    # A trailing section that says of itself it is not part of the chapter is not held to the set.
    carried = tuple(h for h in headings if not h.startswith(WORKING_NOTES))
    owed = SECTIONS
    if carried != owed:
        found.append(f"{name}: sections are {list(carried)}, not {list(owed)} — a reader looking "
                     "for the glossary should never have to hunt for it")

    if not chapter.nodes:
        found.append(f"{name}: a Nodes section that declares no nodes — a chapter states its steps, "
                     "or nothing can be checked about them")

    seen, requirements_seen = set(), set()
    for node in chapter.nodes:
        if not node.id.startswith(prefix):
            found.append(f"{name}#{node.id} is not namespaced to its chapter — expected "
                         f"{prefix}-<n>, so a citation from another chapter is never ambiguous")
        if node.id in seen:
            found.append(f"{name}#{node.id} is expanded more than once — a node says one thing, and "
                         "an id carrying two is answered for by whichever is read first")
        seen.add(node.id)

        if not node.rows:
            found.append(f"{name}#{node.id} states no information at all — a step that consumes "
                         "nothing and produces nothing is scenery, not a step")


        for kinded in node.kinded:
            if not kinded.startswith(prefix):
                found.append(f"{name}#{kinded} is not namespaced to its chapter")

        # The four headings, present and in order. A constraint is argued with by a different
        # reader depending on its kind, so a node that runs them together, drops one or reorders
        # them costs every later reader the same search.
        if node.sections and tuple(node.sections) != NODE_SECTIONS:
            found.append(f"{name}#{node.id} states {list(node.sections)}, not "
                         f"{list(NODE_SECTIONS)} — a reader looking for what constrains a step "
                         f"should never have to hunt for it")

        for req in node.requirements:
            # A requirement belongs to the step it constrains, and says so in its id.
            if req.node_id != node.id:
                found.append(f"{name}#{req.id} is stated under {node.id} and named for "
                             f"{req.node_id} — a constraint is filed on the step it constrains")
            if req.id in requirements_seen:
                found.append(f"{name}#{req.id} is stated more than once — an id carrying two "
                             f"claims is answered for by whichever is read first")
            requirements_seen.add(req.id)

    # A node drawn and never expanded is the half that goes unnoticed: the diagram looks complete.
    for drawn in sorted(in_flow - seen):
        found.append(f"{name}#{drawn} is drawn in the flow and has no node block — the diagram is "
                     "the authority and the expansion is what a reader follows it into")
    for expanded in sorted(seen - in_flow):
        found.append(f"{name}#{expanded} has a node block and is not in the flow — a step nothing "
                     "reaches cannot be performed")


    return found
