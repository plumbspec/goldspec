"""Checks that read a chapter as a process rather than as a document.

Each returns a list of fault strings in `nodes.faults` form: ``name#id — what is wrong``.
"""

from __future__ import annotations

import re
from pathlib import Path

#: A prohibition reads as a rule rather than an act. Paired with an empty Out it is the shape of a
#: constraint filed as a step.
_PROHIBITION = re.compile(r"\b(never|nothing else|and no|only ever|must not)\b", re.I)

#: A spec that reports its own implementation status carries a second copy of what the board derives.
_BUILD_STATUS = re.compile(
    r"\b(unbuilt|specified and unbuilt|nothing implements|does not exist yet|is not built|"
    r"no \w+ exists|not yet built|still to build)\b", re.I)

#: A diagram that colours its nodes by whether they are built is reporting build status
#: structurally rather than in a phrase, and no vocabulary list will catch it.
_BUILD_CLASS = re.compile(r"^\s*classDef\s+(done|todo|built|unbuilt|gap|pending)\b", re.M | re.I)

#: Phrases that name whose run produced a figure.
_OWNER = re.compile(
    r"\bmeasured on (a|an|the|our|one)\b|\bthe evidence is (a|an|the|one)\b|"
    # POSSESSIVE, AND OF SOMETHING A MEASUREMENT COMES OFF. `a customer` is the business domain
    # of half the specs anybody will write — an ordering flow says it in its title and again in
    # `a customer's intent` — while `a customer's suite` says whose run produced a number. Matching
    # the noun, or the bare possessive, fired on the domain and taught a reader to stop reading it.
    r"\b(a|an|one|another|the) (pilot|customer|client|adopter)'s (?:[\w,.~%-]+\s+){0,3}"
    r"(suite|board|estate|repo|repository|run|project|codebase|corpus|tests?|install|build)\b"
    r"|\bthe reference project\b", re.I)

#: A figure: a measurement, not any digit. Two or more digits, or a decimal or thousands group, or
#: a number carrying a unit — because a single bare digit is a chapter number, a version, an
#: ordinal, and matching it made every numbered heading a candidate.
_FIGURE = re.compile(
    r"\b\d[\d,.]*\s*(%|x|\u00d7|ns|\u00b5s|ms|kB|MB|bytes|tests?|classes)\b"
    r"|\b\d[\d,.]*[\d,.]\b")





def _ancestors(edges: dict, target: str) -> set:
    """Every var that reaches `target` by any path."""
    seen: set = set()
    stack = [target]
    while stack:
        cur = stack.pop()
        for src, dsts in edges.items():
            if cur in dsts and src not in seen:
                seen.add(src)
                stack.append(src)
    return seen


def supplied(chapter, kinds: set = None) -> set:
    """Names a chapter's rows say arrive from outside the flow, so no earlier step produces them.

    Read off the parsed rows, never off the markdown. `authored`, `observed`, `generated` and
    `parent` each answer *where does this come from* with something the flow did not make.
    """
    kinds = kinds or _SUPPLIED
    return {n for node in chapter.nodes for row in node.rows
            if row.is_in and row.provenance.lower() in kinds for n in row.names}


#: Provenance values that answer "where does this come from" with something outside the flow, so
#: no earlier step has to produce it. `parent` is the sub-flow entry: the chapter that drills into
#: this one hands it in. The rest are the corpus's own vocabulary.
_SUPPLIED = {"authored", "observed", "generated", "parent"}

#: What an Out row may say about how the node made it.
_MADE = {"derived", "authored", "observed", "generated"}


def movement(node) -> tuple:
    """``(consumes, produces)`` for one node, off the rows the parser already read."""
    return node.consumes, node.produces


def not_required(node) -> set:
    """Names a node takes in but can proceed without.

    An input marked anything other than `yes` has no producer to find. A first run reads no board
    because no run has written one, and the chain must not report that absence as a missing step.
    """
    return {n for row in node.rows
            if row.is_in and row.required.lower() != "yes" for n in row.names}


def chain(chapter) -> list[str]:
    """Every node's In is an earlier node's Out, or arrives from outside the flow."""
    id2var, by_id = chapter.id2var, {n.id: n for n in chapter.nodes}
    outside = supplied(chapter)
    found = []
    for node in chapter.nodes:
        var = id2var.get(node.id)
        if var is None:
            continue
        available = set(outside)
        for anc in _ancestors(chapter.edges, var):
            upstream = by_id.get(chapter.var2id.get(anc, ""))
            if upstream is not None:
                available |= set(upstream.produces)
        spare = not_required(node)
        missing = sorted(e for e in node.consumes
                         if e not in available and e.split(".")[0] not in available
                         and e not in spare)
        if missing:
            found.append(
                f"{chapter.name}#{node.id} needs {', '.join(missing)}, which no earlier step "
                f"produces — either a step is missing an output, or a step is missing")
    return found


def _descendants(edges: dict, source: str) -> set:
    """Every var reachable from `source`."""
    seen, stack = set(), [source]
    while stack:
        for nxt in edges.get(stack.pop(), ()):
            if nxt not in seen:
                seen.add(nxt)
                stack.append(nxt)
    return seen


def _read_elsewhere(siblings, skip) -> set:
    """Every name the rest of the corpus consumes. One read per neighbouring chapter."""
    from goldspec import nodes as node_format

    seen = set()
    for other in siblings:
        if Path(other).name == skip:
            continue
        ch = node_format.read(Path(other))
        if ch:
            seen |= {n for node in ch.nodes for n in node.consumes}
    return seen


def unconsumed(chapter, siblings=()) -> list[str]:
    """Information produced here that nothing takes — in this chapter or anywhere linked.

    Reported as candidates rather than faults. A chapter's own product legitimately leaves, and the
    corpus is searched for a reader before anything is called idle; what is left is information
    accumulating with nobody downstream, which is work being done for nobody.
    """
    id2var, by_id = chapter.id2var, {n.id: n for n in chapter.nodes}
    elsewhere = _read_elsewhere(siblings, chapter.name) if siblings else set()
    found = []
    for node in chapter.nodes:
        var = id2var.get(node.id)
        if var is None:
            continue
        downstream = set(elsewhere)
        for d in _descendants(chapter.edges, var):
            reader = by_id.get(chapter.var2id.get(d, ""))
            if reader is not None:
                downstream |= set(reader.consumes)
        idle = sorted(e for e in node.produces
                      if e not in downstream and not any(d.startswith(e + ".") for d in downstream))
        if idle:
            where = "this chapter or anywhere linked" if siblings else "this chapter"
            found.append(f"{chapter.name}#{node.id} leaves with {', '.join(idle)}, which nothing in "
                         f"{where} takes — work being done for nobody")
    return found


def prohibitions(chapter) -> list[str]:
    """A node that produces nothing and reads as a rule is a constraint filed as a step."""
    return [f"{chapter.name}#{node.id} produces nothing and reads as a prohibition — a rule the "
            f"process obeys rather than an act somebody performs"
            for node in chapter.nodes
            if not node.produces and _PROHIBITION.search(node.title)]


def build_status(chapter) -> list[str]:
    """A spec states what is to be built. Whether it is built is the board's answer."""
    text, name = chapter.text, chapter.name
    found = [f"{name}: line {text[:m.start()].count(chr(10)) + 1} reports its own build status "
             f"({m.group(0)!r}) — the board derives that"
             for m in _BUILD_STATUS.finditer(text)]
    found += [f"{name}: line {text[:m.start()].count(chr(10)) + 1} colours the diagram by build "
              f"status (`classDef {m.group(1)}`) — the board derives that"
              for m in _BUILD_CLASS.finditer(text)]
    return found


#: A chapter naming the tests that prove it: a click-link from a node to a test file, a trace
#: table keyed by test method, or a line pointing at the spec source.
_PROOF_TRACE = re.compile(
    r"^\s*click\s+\w+\s+[\"'][^\"']*[\"']"
    r"|^\|.*\b(?:test method|displayname|test name)\b.*\|"
    r"|^\s*\**Spec source:",
    re.M | re.I)


def carries_proof(chapter) -> list[str]:
    """A citation lives on the annotation, not in the chapter.

    Which test proves a subject, and to what depth, is derived by a run and reported on the board.
    A chapter that also names its tests is carrying a second copy that goes stale — the same defect
    as reporting its own build status, and it passes every other gate.

    Plumb and goldspec's own chapters describe citation and depth as *features* of the tool. That is
    a statement about what is built, not a claim that this chapter is proven, and does not trip here.
    """
    text, name = chapter.text, chapter.name
    return [f"{name}: line {text[:m.start()].count(chr(10)) + 1} names the test that proves it "
            f"({m.group(0).strip()[:48]!r}) — the annotation carries the citation, the board derives "
            f"the rest" for m in _PROOF_TRACE.finditer(text)]


def attribution(chapter) -> list[str]:
    """Flag a sentence carrying both a figure and the name of whose run produced it."""
    text, name = chapter.text, chapter.name
    found = []
    for sentence in re.split(r"(?<=[.!?])\s+", text):
        owner = _OWNER.search(sentence)
        if owner and _FIGURE.search(sentence):
            line = text[:text.index(sentence)].count(chr(10)) + 1
            found.append(f"{name}: line {line} attributes a figure ({owner.group(0)!r}) — "
                         f"the measurement stands without an owner")
    return found


#: Words carrying no subject, dropped before comparing a row against a node title.
_NOISE = frozenset("a an the of to in on for and or its it this that each every optionally".split())

#: A row of an IPO table: id, one of Input/Process/Output, a description, required.


def _content(phrase: str) -> tuple[str, set]:
    """Return (leading word, content words) with ids and noise removed."""
    words = [w for w in re.findall(r"[a-z]+", phrase.lower()) if w not in _NOISE]
    return (words[0] if words else ""), set(words)


def restates_a_step(chapter) -> list[str]:
    """Flag a row that names a step this chapter already has as a node.

    Knows only that a row and a node title share a leading verb, or that the row's words are a
    subset of the node's. It does not know whether the row is at the right level.
    """
    name, found = chapter.name, []
    for owner in chapter.nodes:
        for row in owner.rows:
            # Only a row that DESCRIBES something. A row naming an element — the ordinary case —
            # carries one or two words that any node title mentioning the same thing contains, so
            # matching those would fire on every correct chapter and teach a reader to stop looking.
            if "`" in row.description:
                continue
            verb, words = _content(row.description)
            if not verb:
                continue
            for node in chapter.nodes:
                n_verb, n_words = _content(node.title)
                # The subset rule needs TWO content words to mean anything. With one, the row
                # *the customer* is a subset of the node *tell the customer* — so §4's own
                # instruction to "write plain words where [the corpus defines no element]"
                # produced a fault on any row whose noun appears in a node title. A check whose
                # false positives are generated by the documentation teaches a reader to stop
                # reading its output.
                if verb == n_verb or (len(words) > 1 and words <= n_words):
                    found.append(
                        f"{name}#{row.row_id} names a step this chapter already has "
                        f"({node.id} \u00b7 {node.title}) \u2014 the row may be a layer below the "
                        f"node it sits in")
                    break
    return found


#: The stamp a chapter carries under its title (`spe6`).
_STAMP = re.compile(r"^\*\*Last updated\*\*\s+\d{4}-\d{2}-\d{2}\s+v\d+"
                    r"(?:\s+\u00b7\s+(?:derived|authored))?", re.M)


def stamped(chapter) -> list[str]:
    """A chapter says when it last changed, as `YYYY-MM-DD vN`.

    The version distinguishes two sessions on one day. Where the date came from — derived or
    authored — may follow it and is optional.
    """
    text, name = chapter.text, chapter.name
    if _STAMP.search(text):
        return []
    return [f"{name}: no stamp under the title — a reader holding a printout cannot tell whether it "
            f"is current (`spe6`)"]


def padded(chapter, prefix: str) -> list[str]:
    """Every id series is left-padded to the width its own largest member needs.

    Ten subjects are `ch0`..`ch9`; the eleventh renumbers the series to `ch00`..`ch10`. Sorting then
    works with a plain sort and the key stays as short as it can be.

    Reads only where an id is **declared** — a node heading, a requirement bullet, a table row. An id
    named in prose is a reference, and a chapter that discusses its own numbering would otherwise
    fail its own check.
    """
    text, name = chapter.text, chapter.name
    import collections
    series = collections.defaultdict(list)
    #: every declared id, wherever declared: a heading, a bullet, a table row
    #: a series restarts under each parent — dev07-1's rows and dev07-2's rows are two series —
    #: so the key is (everything before the segment, the segment's sigil)
    for pat in (rf"^### ({prefix}[\w-]*\d)\s", rf"^\s*\*\s+({prefix}[\w-]*\d)\b",
                rf"^\|\s*({prefix}[\w-]*\d)\s*\|"):
        for m in re.finditer(pat, text, re.M):
            segs = m.group(1).split("-")
            for i, seg in enumerate(segs):
                scope = "-".join(segs[:i])
                sm = re.fullmatch(r"([A-Za-z]+)(\d+)", seg)
                if sm:
                    series[(scope, sm.group(1))].append(sm.group(2))
                elif seg.isdigit():
                    series[(scope, "__node__")].append(seg)
    found = []
    for kind, seen in sorted(series.items()):
        if len(set(seen)) == 1:
            continue    # one distinct number says nothing about its series' width — the series
                        # may live corpus-wide, as a sub-flow's chapter number does
        widths = {len(v) for v in seen}
        want = len(str(max(int(v) for v in seen)))
        if widths != {want}:
            scope, sigil = kind
            where = f" under {scope}" if scope else ""
            label = (f"node numbers{where}" if sigil == "__node__"
                     else f"`{sigil}` numbers{where}")
            found.append(f"{name}: {label} are padded {sorted(widths)} where the largest needs "
                         f"{want} — a plain sort will not order them")
    return found


#: A step drawn as a sub-flow: `NAME[[<b>id</b> · …]]`, carrying an id of its own.

def provenance(chapter) -> list[str]:
    """Every row of an Information table says where the information came from.

    The column exists so a node can be read on its own. A developer holding one node should not
    have to hold the diagram, an imports block and a glossary in their head to find out where an
    input arrives from — so the answer sits in the row that raises the question.

    An `In` answers with the step that produced it, or with `parent` when the chapter that drills
    into this one hands it in, or with `authored`, `observed` or `generated` when it arrives from
    outside any step. An `Out` answers with how this node made it.
    """
    id2var = chapter.id2var
    by_id = {n.id: n for n in chapter.nodes}
    name = chapter.name
    found = []
    for node in chapter.nodes:
        for row in node.rows:
            prov, label = row.provenance, ", ".join(row.names)
            nid = node.id
            if not prov:
                found.append(f"{name}#{nid} does not say where {label} comes from")
                continue
            if not row.is_in:
                if prov.lower() not in _MADE:
                    found.append(f"{name}#{nid} says {label} is `{prov}`, which is not a way a "
                                 f"step makes something — one of {', '.join(sorted(_MADE))}")
                continue
            if prov.lower() in _SUPPLIED:
                continue
            if prov not in by_id:
                found.append(f"{name}#{nid} takes {label} from `{prov}`, which is neither a step "
                             f"of this chapter nor one of {', '.join(sorted(_SUPPLIED))}")
                continue
            produced = set(by_id[prov].produces)
            if not any(e in produced or e.split(".")[0] in produced for e in row.names):
                found.append(f"{name}#{nid} takes {label} from {prov}, which does not produce it")
                continue
            var, pvar = id2var.get(nid), id2var.get(prov)
            if (row.required.lower() == "yes" and var and pvar
                    and pvar not in _ancestors(chapter.edges, var)):
                found.append(f"{name}#{nid} takes {label} from {prov}, which the flow does not "
                             f"reach it from — required here, so it cannot be a later run's")
    return found


def cross_flow(path: Path, siblings: list) -> list[str]:
    """Check a sub-flow node against the chapter it drills into.

    The child's nodes are the ones whose ids nest under the parent's — `dev03-1` under `dev03`.
    Four directions are checked: the parent must supply what the child cannot make for itself; the
    parent may not claim to emit what the child never produces; the parent may not take what no
    step of the child consumes; and an element the child produces that another chapter consumes
    must be declared at the parent it transits. An element nothing else reads is the sub-flow's
    own terminal report and the parent does not restate it — a refusal stays inside its sub-flow,
    because drawing it at the parent grows loops a person cannot read.
    """
    from goldspec import nodes as node_format

    parent = node_format.read(Path(path))
    if parent is None:
        return []
    name, found = parent.name, []
    by_id = {n.id: n for n in parent.nodes}
    outside = supplied(parent)

    for drawn in parent.subflows:
        node = by_id.get(drawn)
        if node is None:
            continue
        child = None
        for other in siblings:
            if Path(other) == Path(path):
                continue
            ch = node_format.read(Path(other))
            if ch and any(re.fullmatch(rf"{re.escape(drawn)}-[a-z]?\d+", n.id) for n in ch.nodes):
                child, child_path = ch, other
                break
        if child is None:
            found.append(f"{name}#{drawn} is drawn as a sub-flow and no chapter expands it")
            continue
        gives = {n for c in child.nodes for n in c.produces}
        takes = {n for c in child.nodes for n in c.consumes}
        spare = set().union(*(not_required(n) for n in child.nodes)) if child.nodes else set()
        own = supplied(child, _SUPPLIED - {"parent"})   # the child supplies these itself
        needs = {e for e in takes - gives
                 if e not in outside and e.split(".")[0] not in outside
                 and e not in spare and e not in own}
        p_in, p_out = node.consumes, node.produces
        short = sorted(e for e in needs
                       if e not in p_in and e.split(".")[0] not in set(p_in))
        if short:
            found.append(f"{name}#{drawn} does not take {', '.join(short)}, which the chapter it "
                         f"drills into needs and cannot make for itself")
        over = sorted(e for e in p_out
                      if e not in gives and e.split(".")[0] not in gives)
        if over:
            found.append(f"{name}#{drawn} claims to leave with {', '.join(over)}, which no step of "
                         f"the chapter it drills into produces")
        unused = sorted(e for e in p_in
                        if e not in takes and e.split(".")[0] not in takes
                        and not any(t.startswith(e + ".") for t in takes))
        if unused:
            found.append(f"{name}#{drawn} takes {', '.join(unused)}, which no step of the chapter "
                         f"it drills into consumes")
        elsewhere = _read_elsewhere(siblings, Path(child_path).name)
        # `spe5-sr7` — a taker of a PART reads a producer of the whole, and taking the whole is
        # not a demand for any particular part. This read the rule backwards: `story` consumed by
        # any chapter made every `story.*` a child produced look wanted, so a parent was told to
        # declare `story.mutation.survived` because an unrelated flow elsewhere took a story.
        #
        # `unconsumed` asks the same question — does anybody read what this produces — and had
        # always asked it the right way round. Two copies of one rule, and only one of them stated.
        escapes = sorted(e for e in gives
                         if e not in takes
                         and e not in p_out and e.split(".")[0] not in p_out
                         and (e in elsewhere or any(d.startswith(e + ".") for d in elsewhere)))
        if escapes:
            found.append(f"{name}#{drawn} does not declare {', '.join(escapes)}, which the chapter "
                         f"it drills into produces and another chapter consumes")
    return found


def review(path: Path, siblings=(), prefix: str | None = None) -> list[str]:
    """Every check above, against one chapter. Empty means nothing found.

    `chain` cannot see a sub-flow's entry point: a chapter whose nodes nest under a parent id takes
    its first inputs from that parent, and `chain` reports them as unproduced. Read those against
    `cross_flow`, which is the check that knows about the boundary.
    """
    """Every check above, against one chapter. Empty means nothing found.

    **One read.** `nodes.read` observes the markdown once and hands back the chapter; every check
    below is a pure function of that. Nothing here opens the file again.
    """
    from goldspec import nodes as node_format

    chapter = node_format.read(Path(path))
    if chapter is None:
        return []
    # The caller's, because only the caller knows the project's conventions. Derived here from the
    # FILENAME, `padded` was handed `story` for a project whose flows are `story-*.md` — an id
    # prefix nothing in the corpus starts with — so it found no series, compared nothing, and
    # passed. The padding gate was silently dead for every project that renamed its flows, which
    # is exactly the population the conventions chapter is written for.
    if prefix is None:
        prefix = re.match(r'[a-z]+', Path(path).stem.replace('chapter-', 'ch')) \
                 .group(0) if Path(path).stem else 'ch'
    return (build_status(chapter) + carries_proof(chapter)
            + attribution(chapter) + stamped(chapter) + padded(chapter, prefix)
            + chain(chapter) + provenance(chapter) + prohibitions(chapter)
            + restates_a_step(chapter)
            + (cross_flow(path, siblings) if siblings else []))


def observations(path, siblings=()) -> list[str]:
    """What is worth a reader's eye and is not a fault. Reported always, never gated.

    `unconsumed` is the whole of this, and it belongs here rather than beside the checks because it
    has no invariant to hold. Every flow ends by producing something for a person — a board, a
    view, an archive — and an element nothing downstream consumes is that product about as often as
    it is waste. The check cannot tell the two apart from the data, and neither can any rule anybody
    has written down, so it says what it sees and a reader decides.

    Split out rather than left behind a flag. A flag suppressing it also suppressed every check
    beside it, which is how a corpus comes to run with its real gates off for the sake of one
    report.
    """
    from goldspec import nodes as node_format

    chapter = node_format.read(Path(path))
    return unconsumed(chapter, siblings) if chapter is not None else []
