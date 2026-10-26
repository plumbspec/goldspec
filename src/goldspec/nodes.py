"""The node format — information and data live with the node that moves them.

**Why this exists.** A chapter used to carry one `## Input → process → output` section and one
`## Data definitions` table for the whole flow. That is the wrong altitude, and the symptom is
measurable: with nowhere per-node to put what a step consumes, what it holds and what constrains it,
all of it backs up into the claim. A trace row can reach **486 words** against a chapter average of
161, with twelve separate things wearing one id — a
claim, a decision, three pieces of history, a reading, a cross-reference, two constraints, and two
steps that had never been drawn because there was no flow for them to be steps in.

So a node owns its story, and beneath it the information it moves: one five-column table whose
every row carries an id, an `In` or an `Out`, and the provenance saying where it came from. There is
no chapter-level list of information and no `Held` column — a row is stated once, by the step that
moves it.

**What that buys, beyond tidiness.** Each row is a citable subject, so *does this step have the
information it needs* stops being a thing a reviewer checks and becomes a thing a run derives. And
each piece of information's producers and consumers are then already stated, which makes the
data-flow diagram derivable rather than drawn — nobody maintains it, and something produced by no
node or consumed by none is a dangling half-edge the checks can name.

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


#: The sections a node-format chapter carries, in the order they must appear. Two, and no more:
#: `## Nodes` replaces the older `## Story → test trace`, `## Input → process → output` and
#: `## Data definitions` together, because all three said something about a step from outside it.
#: Order is checked for the same reason `spe3` checks it: a glossary is looked up rather than read
#: through, and the only reliable way to be findable is to be in the same place every time.
#: `WORKING_NOTES` below is the one trailing heading exempt from the set.
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

#: Any row of a five-column table, so a row `_INFO_ROW` could not read is still *seen*.
#:
#: A row with no id, or with an `IO` outside the set, matched nothing and was dropped before every
#: downstream check — so an unidentified required input from a step that does not exist passed a
#: clean run, and `Input`/`Output` (the older shape's own spelling) vanished rather than being
#: refused. The same silent-drop as a misformed requirement bullet, one table over.
_TABLE_ROW = re.compile(r"^\|(?:[^|\n]*\|){4,}\s*$", re.M)

#: The header of an Information table, and the `|---|` rule under it. Neither is a row.
_NOT_A_ROW = re.compile(r"^\|\s*(information\s*\||\s*:?-+:?\s*\|)", re.I)

#: A node opens a `###` block and carries its id first: `### ch1-2 · check availability`.
#: The id may be backticked or not; the separator may be `·`, `—` or `-`.
_NODE = re.compile(r"^###\s+`?([A-Za-z]+\d[\w.\-]*\d|[A-Za-z]+\d)`?\s*[·—-]?\s*(.*)$", re.M)

#: An id that is a decision or a parameter rather than a story, **where the node declares it**:
#: `**Decision \`ch1-D1\` — the window closes at 02:00, so nothing may assume same-day.**`
#:
#: The run-in is what makes it a declaration. Matched anywhere in the block, this read every
#: *mention* as one, so a closing paragraph citing another chapter's unknown — `ch3-U1`, `spe1-1-4-u1`,
#: the ordinary way one node points at a decision another chapter owns — was reported as an id not
#: namespaced to its chapter. The prose was right and the gate was wrong, and it fired the first
#: time a converted chapter cited across chapters at all.
#:
#: `[^*]*` is what pins it: the id has to sit inside the *first* bold run of the line, before any
#: other emphasis, which is the shape both a parameter and a decision are written in and the shape a
#: sentence about somebody else's unknown never has.
#: The chapter number is OPTIONAL. `[A-Za-z]+\d+` assumed every chapter is numbered — true of
#: `chapter-01-ordering.md` giving `ch1`, and false of a corpus that names its flows by sigil, where
#: the prefix is `hol` or `snd` and the nodes are `hol1`, `snd1`. A decision written `snd-D1`, which
#: is the only spelling consistent with those nodes, matched nothing: it was declared nowhere, held
#: to no namespace, and the run reported no fault — the gate could not see it to refuse it.
_KINDED = re.compile(r"^\*\*[^*]*`([A-Za-z]+\d*(?:-\d+)*-([PUD])\d+)`", re.M)

#: The node's story — the blockquote under its heading, one or more lines of `> `.
_STORY = re.compile(r"^> (.+(?:\n> .+)*)", re.M)

#: A `####` heading inside a node block.
_NODE_SECTION = re.compile(r"^#### (.+?)\s*$", re.M)

#: One requirement or unknown: `  * spe1-ur3 - the flow is drawn before any step is described`.
#: `-`, `\u2013` and `\u2014` all read the same, as they do in a `###` heading — the page says so
#: there and a reader carries the habit across. A colon or nothing still parses as nothing, and
#: `_REQUIREMENT_SHAPED` names it.
_REQUIREMENT = re.compile(
    r"^\s*\*\s+((([\w.-]+?)-(ur|sr|nfr|u))\d+)\s*[-\u2013\u2014]\s*(.+)$", re.M)

#: A bullet that OPENS with a requirement-shaped id, however it goes on.
#:
#: `_REQUIREMENT` wants ` - ` between the id and the text. Written with a colon or an em dash the
#: bullet matches nothing, and a requirement nothing parsed is a requirement no check holds: the
#: ownership check and the duplicate check simply go quiet, on a line that looks exactly right.
#: Nothing counts requirements either, so there was no number a reader could have compared — which
#: is the one remedy this method offers for a check that read nothing.
#: Any list marker — `*`, `-`, `+` or a number — because a document being converted writes its
#: requirements as `- R1 …` or `1. R1 …` far more often than as `*`, and a bullet the reader skips is
#: a requirement nothing holds (`spe5-sr4`).
_REQUIREMENT_SHAPED = re.compile(r"^\s*(?:[*+-]|\d+[.)])\s+([\w.-]+?-(?:ur|sr|nfr|u)\d+)",
                                 re.M | re.I)

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
    #: Bullets that open with a requirement-shaped id and that nothing could read.
    malformed: tuple = ()
    #: Rows of a five-column table that the row parser could not read.
    unreadable: tuple = ()
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
    #: Decisions and parameters stated for the whole flow, above `## Nodes`. A constraint that
    #: genuinely is not one step's — a regulatory clock binding the whole process — has nowhere
    #: else to go, and hanging it on whichever node happens to start is bending the model to fit
    #: the tool. It is read here so that it is still a subject: it was parsed only inside node
    #: blocks, so one written where the format says to write it was declared nowhere, cited
    #: nowhere, and namespaced to nothing — `zz9-D9` between the diagram and `## Nodes` passed.
    kinded: tuple = ()

    @property
    def name(self) -> str:
        return self.path.name

    @property
    def id2var(self) -> dict:
        return {v: k for k, v in self.var2id.items()}



#: The fenced block a chapter draws its flow in. `read_flow` reads its edges and `specgate` checks
#: its terminals, so the pattern has one home rather than one per reader.
#:
#: `flowcheck._mermaid_blocks` is the same fence seen differently — by path, carrying the line
#: numbers a fault message needs — and stays separate for that.
_MERMAID = re.compile(r"```mermaid(.*?)```", re.S)


def mermaid_blocks(text: str) -> list[str]:
    """Every mermaid block in a chapter, in the order it draws them."""
    return _MERMAID.findall(text)


def _mermaid(text: str) -> str:
    return "\n".join(mermaid_blocks(text))


def read_flow(text: str) -> tuple[dict, dict, tuple]:
    """``(edges, var -> node id, ids drawn as sub-flows)`` from the chapter's mermaid block."""
    mer = _mermaid(text)
    # The id may be bold or bare. Requiring `<b>` read every diagram that did not use it as naming
    # no nodes at all — and a check whose input is silently empty passes without comparing anything,
    # which is the failure this whole module is arranged to prevent.
    # INDENTED BY ANY AMOUNT. This read `^\s{4}` — exactly four whitespace characters — so a
    # diagram indented by two, six or eight spaces, all of which mermaid renders identically,
    # produced an EMPTY map. `chain`, `provenance`'s reachability half and `unconsumed` all key
    # off it, so they went silent together, while the drawn-and-expanded check reported every node
    # in the chapter as "not in the flow" — four faults naming the wrong cause, and three real
    # gates off. Nothing documented the four, because nothing knew it was load-bearing.
    var2id = {}
    for m in re.finditer(r"^[ \t]+(\w+)\s*[\[\({>]+\s*(?:<b>)?\s*([A-Za-z]+\d[\w.-]*)", mer, re.M):
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
         re.finditer(r"^[ \t]+\w+\[\[\s*(?:<b>)?\s*([A-Za-z]+\d[\w.-]*)", mer, re.M)}))
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
        # Rows the five-column parser could not read, so nothing is dropped in silence.
        read_rows = {row.row_id for row in rows}
        unreadable = tuple(
            line.strip() for line in _TABLE_ROW.findall(block)
            if not _NOT_A_ROW.match(line)
            and not any(rid in line for rid in read_rows))
        told = _STORY.search(block)
        story = " ".join(line.lstrip("> ") for line in told.group(0).splitlines()) if told else ""
        requirements = tuple(
            Requirement(owner, rid, kind, body.strip())
            for rid, _stem, owner, kind, body in _REQUIREMENT.findall(block))
        read_ids = {req.id for req in requirements}
        malformed = tuple(sorted(
            {rid for rid in _REQUIREMENT_SHAPED.findall(block)} - read_ids))
        sections = tuple(_NODE_SECTION.findall(block))
        nodes.append(Node(node_id, title, rows,
                          requirements=requirements, sections=sections,
                          kinded=tuple(sorted({m[0] for m in _KINDED.findall(block)})),
                          malformed=malformed, unreadable=unreadable,
                          story=story.replace("**", "").strip()))

    edges, var2id, subflows = read_flow(text)
    # Everything above `## Nodes` — the title, the stamp, the story, the diagram, and any
    # constraint stated for the flow as a whole.
    preamble = text[:text.index(nodes_body)] if nodes_body else text
    flow_level = tuple(sorted({m[0] for m in _KINDED.findall(preamble)}))
    return Chapter(Path(path), tuple(nodes), text, edges, var2id, subflows, flow_level)


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

    # Off the chapter this was handed, and with fenced blocks removed first. It re-read the file
    # — a second observer, against a page promising exactly one — and scanned raw, so a chapter
    # quoting a `##` heading inside a code block was told its section set was wrong. The two
    # defects are the same one: a check that goes back to the source forms its own opinion of what
    # a line is.
    headings = re.findall(r"^## (.+?)\s*$", re.sub(r"```.*?```", "", chapter.text, flags=re.S), re.M)
    # A section that says of itself it is not part of the chapter is not held to the set — and it
    # has to be TRAILING. The exemption was granted wherever the heading sat, so the two passages
    # saying it "goes last" were enforced by nothing, and a chapter could open with its working
    # notes and still pass. The heading keeps its own wording after the name (`## Working notes —
    # not part of the chapter`), which is the corpus convention and the whole reason ignoring it
    # is honest rather than lenient.
    carried = tuple(headings)
    while carried and carried[-1].startswith(WORKING_NOTES):
        carried = carried[:-1]
    owed = SECTIONS
    if carried != owed:
        found.append(f"{name}: sections are {list(carried)}, not {list(owed)} — a reader looking "
                     "for the glossary should never have to hunt for it")

    if not chapter.nodes:
        found.append(f"{name}: a Nodes section that declares no nodes — a chapter states its steps, "
                     "or nothing can be checked about them")

    kinded_seen = set()
    for kinded in chapter.kinded:
        if not kinded.startswith(prefix):
            found.append(f"{name}#{kinded} is stated for the whole flow and is not namespaced to "
                         f"its chapter — expected {prefix}-<kind><n>")
        kinded_seen.add(kinded)

    seen, requirements_seen = set(), set()
    for node in chapter.nodes:
        if not node.id.startswith(prefix):
            found.append(f"{name}#{node.id} is not namespaced to its chapter — expected "
                         f"{prefix}-<n>, or the file name carries the wrong number for the step it "
                         f"expands; a citation from another chapter must never be ambiguous")
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
            # Flow-level and node-level decisions share one number series per chapter, which is
            # only true if something holds them to it.
            if kinded in kinded_seen:
                found.append(f"{name}#{kinded} is stated more than once — a subject says one "
                             f"thing, and an id carrying two is answered for by whichever is "
                             f"read first")
            kinded_seen.add(kinded)

        # The four headings, present and in order. A constraint is argued with by a different
        # reader depending on its kind, so a node that runs them together, drops one or reorders
        # them costs every later reader the same search.
        if node.sections and tuple(node.sections) != NODE_SECTIONS:
            found.append(f"{name}#{node.id} states {list(node.sections)}, not "
                         f"{list(NODE_SECTIONS)} — a reader looking for what constrains a step "
                         f"should never have to hunt for it")

        for line in node.unreadable:
            found.append(f"{name}#{node.id} has a table row nothing can read — a row is "
                         f"`| <id>-infN | In or Out | <description> | <required> | <provenance> |`, "
                         f"and one written otherwise is dropped before every check sees it: {line}")

        for row in node.rows:
            # The same rule a requirement is already held to. A row named `ch1-1-inf9` under node
            # `ch1-3` resolves to whichever a reader finds first, and only one of the two id
            # families was checked — with nothing saying which.
            if row.node_id != node.id:
                found.append(f"{name}#{row.row_id} is stated under {node.id} and named for "
                             f"{row.node_id} — a row is filed on the step that moves it")

        for rid in node.malformed:
            found.append(f"{name}#{rid} is written in a shape nothing reads — a requirement bullet "
                         f"is `* {rid} - <what it requires>`, with a hyphen between the id and the "
                         f"text. Written otherwise it parses as nothing, and no check holds it")

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
    for drawn in sorted({i for i in in_flow if i.startswith(prefix)} - seen):
        found.append(f"{name}#{drawn} is drawn in the flow and has no node block — the diagram is "
                     "the authority and the expansion is what a reader follows it into")
    # Against every id the diagram draws, namespaced or not: a step drawn under the wrong number is
    # misnumbered, which the namespace fault already says, and is not missing from the flow.
    for expanded in sorted(seen - in_flow):
        found.append(f"{name}#{expanded} has a node block and is not in the flow — a step nothing "
                     "reaches cannot be performed")


    return found
