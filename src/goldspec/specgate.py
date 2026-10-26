"""The gate that keeps a spec written in these conventions honest. Shipped, and opted into.

Every check here presumes an artifact and a habit: that a subject is declared by its row in a trace
table, placed in a process flow, and that open questions are tracked in two places. That is a
method, and a *tool* requiring it would be choosing somebody's method for them — which is why Plumb
cannot read a spec, cannot verify one, and cannot check against one, and why none of this was ever
allowed to live there.

A spec that nothing checks rots, and the rot is silent. That is the argument for gates. How they
reach anybody is the harder half. A gate copied into somebody's project forks the moment it lands:
a fix reaches nobody who adopted earlier, and the tool cannot tell *behind* from *deliberately
edited* without stamping every file it wrote and reporting drift, which is machinery whose only
reason to exist is the copying. A copy is also in **a language**, which a project that has none of
it cannot run.

So: one artifact rather than modules landing in a repository, so a fix reaches everyone on the next
install and there is nothing to fork. goldspec is a separate product with its own version, and
nobody who installs Plumb is given it, asked about it, or affected by it. Reading a spec is not a
tool reaching into a project; it is a method a project chose, checking the conventions that project
adopted.

What it checks: every subject declared once and once only, placed in its process flow, every open
unknown tracked in both of its homes, every flow able to render, and no citation naming a subject
the declared set does not define.

Every check is a pure source scan: no build, no network, no rendering. That is what makes it cheap
enough to always run, which is the only reason a gate is ever actually run.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path

# Defined in `conventions.py` and re-exported here, where every caller already reaches for it. It
# moved because the settings module is named for it and was holding the same defaults over again as
# bare constants: `"ch"` was typed in two files. That is the second home this method exists to
# remove, at the smallest possible scale and inside its own tool.
from goldspec.conventions import Conventions

#: Where a citation can be written, in the languages the tool speaks. A citation is a marker and an
#: id; the shapes differ and the question does not. Listed rather than inferred: guessing at a
#: citation is how a scan reports a subject as uncited because it did not recognise the syntax.
CITATION_PATTERNS = (
    # @pytest.mark.proves("ID") / .informs("ID")
    r'mark\.(?:proves|informs)\(\s*["\']([^"\']+)["\']',
    # @Proves(value = "ID") / @Informs("ID") — Java, with or without the member name
    r'@(?:Proves|Informs)\(\s*(?:value\s*=\s*)?"([^"]+)"',
)

#: Where citations are looked for. A source tree, not a build output.
SOURCE_SUFFIXES = (".py", ".java", ".kt", ".groovy", ".scala")

SKIP_DIRS = {".git", "target", "build", "node_modules", "__pycache__", ".venv", "venv", "dist"}




@dataclass
class Report:
    """What the gates found. `checked` matters as much as `problems`: a run that checked nothing
    and found nothing is not a pass, and saying so is the difference between the two."""

    checked: list[str] = field(default_factory=list)
    problems: list[str] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return not self.problems


def cited_subjects(root: Path) -> dict[str, list[str]]:
    """Every subject id cited anywhere under `root`, and where. Language-independent by pattern."""
    found: dict[str, list[str]] = {}
    for path in sorted(root.rglob("*")):
        if path.is_dir() or path.suffix not in SOURCE_SUFFIXES:
            continue
        if any(part in SKIP_DIRS for part in path.parts):
            continue
        try:
            text = path.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        for pattern in CITATION_PATTERNS:
            for cited in re.findall(pattern, text):
                found.setdefault(cited, []).append(str(path.relative_to(root)))
    return found


# ---- the spec-directory tier ------------------------------------------------------------------

def declared_in_spec(spec: Path, conv: Conventions) -> list[str]:
    """Every subject the spec declares, in flow order — **its row in a trace table**.

    The row *is* the declaration. It always held the id and the one line saying what the subject
    claims, and a chapter module held the same id a second time as a function name: measured at
    160 ids from each on this project's own spec, 17 on its decision spec and 16 on goldspec's,
    identical in both directions every time. What a gate could then check was that two copies of
    one list still agreed — which is the id-drift a handed-over feed produces, at a smaller scale
    and inside a single repository.

    So the copy that goes is the one carrying nothing else. A trace row holds what the subject
    *says*; a `def chN_M():` holds a name a regex agreed to read, in a language the spec did not
    have to be written in.

    In the node format the declaration moved again, and for the same reason it moved the first time.
    A node *is* the subject — it carries the story, and the trace row that used to hold the claim is
    the node's own expansion rather than a second list beside it. So a chapter with a `## Nodes`
    section declares its subjects there, and one without declares them in its trace table.
    """
    from goldspec import nodes as node_format

    found = []
    for md in _flow_files(spec, conv):
        chapter = node_format.read(md)
        if chapter is not None:
            found += [node.id for node in chapter.nodes]
            # The KINDED subjects too — `chN-D1`, `chN-P1` and the rest that `nodes.py` already
            # parses out of a node block and `faults()` already namespace-checks. Without them a
            # citation to a decision or a parameter is unsatisfiable: `informs` is one of the
            # markers scanned for, so those citations are held against a list that structurally
            # cannot contain them, and no way of authoring the chapter makes one pass. Measured on
            # a gate that cannot fail for a real reason — which is
            # gate that cannot fail for a real reason because it never stops failing for this one.
            found += [kinded for node in chapter.nodes for kinded in node.kinded]
            # And the ones stated for the flow as a whole, above `## Nodes`, which the format
            # provides for and this list did not carry — so a citation to one was unsatisfiable.
            found += list(chapter.kinded)
            # And the open unknowns. `getting-started` and `docs/README` both name an open unknown
            # as one of the four kinds of subject; a test citing one was told it was "declared
            # nowhere", about a bullet sitting in plain sight in the chapter. A subject the method
            # defines and the gate refuses to see is unsatisfiable however the chapter is written.
            found += [req.id for node in chapter.nodes
                      for req in node.requirements if req.kind == "u"]
    return found


def _flow_files(spec: Path, conv: Conventions) -> list[Path]:
    return sorted((spec / conv.flow_dir).glob(conv.flow_glob))


def _chapter_prefix(md: Path, conv: Conventions) -> str:
    """The namespace every id in one flow file carries.

    Two naming conventions, and the file says which it is in. ``chapter-01.2-gate.md`` numbers its
    chapters, so the prefix is the namespace and that number: ``ch1-2``. A file named for its flow —
    ``dev07-run-plumb.md``, ``spe-specify-a-process.md`` — carries the sigil itself, so the prefix is
    the leading segment, and a sub-flow's file keeps the parent's number with it.

    Falling back to ``conv.namespace`` where neither matches is what used to happen for every
    sigil-named file, and where the namespace is an alternation of sigils that is not a prefix any
    id starts with — so every node in the corpus reported as not namespaced to its own chapter.
    """
    stem = conv.flow_glob.replace("*", "").removesuffix(".md").rstrip("-")
    if stem:
        found = re.match(rf"{re.escape(stem)}-(\d+)(?:\.(\d+))?", md.name)
        if found:
            major, minor = found.groups()
            return f"{conv.namespace}{int(major)}" + (f"-{int(minor)}" if minor else "")
    # The sigil the project declared, taken off the front of the filename with whatever number
    # follows it: `dev07-6-append-...` -> `dev07-6`, `ado-bring-...` -> `ado`. Read against the
    # declared namespace rather than off the first word, because a flow may be named for its reader
    # rather than its sigil — `developer-day.md` carries `dev00`..`dev11`, and taking the first
    # word gave `developer`, under which every id in the file is not namespaced to its own chapter.
    named = re.match(rf"(?:{conv.namespace})(?:\d+(?:-\d+)*)?", md.name)
    if named:
        return named.group(0)
    # A main flow named for no sigil has no steps of its own to namespace: every step is another
    # flow, named by that flow's prefix (`spe1-sr5`).
    return "" if conv.main_flow and md.name == conv.main_flow else conv.namespace


def check_spec_directory(spec: Path, conv: Conventions, cited_from: Path | None = None) -> Report:
    """Everything that needs the prose half: declaration, placement, citation, unknowns, flows.

    ``cited_from`` is the source tree whose citations are held against this spec — the repository
    root, usually. Left out, that check does not run and the report says so: a spec is checkable
    on its own, and a project keeping its spec somewhere else entirely still gets the rest.
    """
    from goldspec import nodes as node_format
    from goldspec.flowcheck import faults, terminals

    report = Report()
    # WHAT THIS RUN JUDGED BY, first, before any verdict about the spec.
    #
    # Every fault below is phrased as a statement about somebody's corpus, and the one cause none
    # of them can phrase is having been handed the wrong strings. The command has named its basis
    # on every run for exactly that reason; the library did not, so a caller who built a
    # `Conventions` by hand had no way to see which one was wrong. One did: `flow_glob` kept its
    # default while the namespace was corrected, the glob matched no file, and the run reported a
    # corpus of 34 nodes as declaring nothing at all.
    report.checked.append(
        f"conventions: ids namespaced {conv.namespace!r}, flows in {conv.flow_dir}/{conv.flow_glob}")

    subjects = declared_in_spec(spec, conv)
    report.checked.append(f"{len(subjects)} subject(s) declared in {spec.name}/")

    # A read that yielded nothing is a failure, never a pass. A gate cannot be used to
    # find out whether it read anything if the answer looks identical to holding together: a spec
    # this scan cannot parse reports "0 subject(s)" and "consistent with itself" in the same
    # breath, and a whole spec silently becoming invisible is the largest regression this gate can
    # be asked about.
    if not subjects:
        # How many files the glob MATCHED, against how many are sitting there. A count of zero
        # beside a count of seven says *your glob is wrong* in a way no amount of prose does, and
        # it is the difference between reading this as a verdict on the corpus and reading it as a
        # verdict on the strings the gate was handed.
        matched = len(_flow_files(spec, conv))
        present = len(list((spec / conv.flow_dir).glob("*.md"))) if (spec / conv.flow_dir).is_dir() \
            else 0
        report.problems.append(
            f"{spec.name}/ declares no subjects at all — this gate reads trace-table rows in "
            f"{conv.flow_dir}/{conv.flow_glob}, which matched {matched} of the {present} markdown "
            f"file(s) there, which is never a state anybody intends. Either the spec is not there, "
            f"or its flows are named differently from {conv.flow_glob!r}")

    # One row per subject. With the declaration and the description in one place a second row is
    # no longer a disagreement to reconcile — it is two claims wearing one id, and whichever a
    # reader finds first wins silently.
    for subject in sorted({s for s in subjects if subjects.count(s) > 1}):
        report.problems.append(
            f"{subject} has more than one trace row — a subject says one thing, and an id "
            f"carrying two claims is answered for by whichever is read first")

    # What a test cites and what the spec declares, held against each other. This is the check the
    # old cross-check was standing in for: it compared two copies of one list, where this compares
    # the spec against something authored independently of it. Scoped to this spec's namespace,
    # because a repository may carry several (`ch2-15`) and a citation into another one is not
    # this spec's to answer for.
    if cited_from is None:
        report.checked.append("citations not checked — no source tree given")
    else:
        ours = re.compile(rf"{conv.namespace}\d")
        known = set(subjects)
        cited = cited_subjects(cited_from)
        report.checked.append(f"{len(cited)} cited id(s) read from {cited_from}")
        for subject, where in sorted(cited.items()):
            if ours.match(subject) and subject not in known:
                report.problems.append(
                    f"{subject} is cited by {where[0]} and declared nowhere in {spec.name}/ — a "
                    f"citation to a subject nobody wrote down reads as authoritative as any other")


    # `alt4` — a flow is closed and reachable from its start, which presumes it has one. Derived
    # from the edges rather than from a shape somebody remembered to draw: a start is a node nothing
    # points at, an end is a node pointing at nothing. A flow with neither is a diagram of a cycle,
    # and a reader cannot tell where it begins or what it arrives at.
    #
    # Open unknowns are excluded from both. They hang off a flow deliberately and are terminal by
    # construction, so counting one as an ending would let a flow satisfy this by carrying an
    # unanswered question — the opposite of what the check is for.
    for md in _flow_files(spec, conv):
        for block in node_format.mermaid_blocks(md.read_text()):
            starts, ends = terminals(block)
            if not starts:
                report.problems.append(
                    f"{md.name}: the flow has no start — every node is pointed at by another, so "
                    "nothing says where it begins (alt4)")
            if not ends:
                report.problems.append(
                    f"{md.name}: the flow has no end — every node points at another, so nothing "
                    "says what it arrives at (alt4)")

    rendering = faults(_flow_files(spec, conv))
    report.problems += rendering
    report.checked.append(f"{len(_flow_files(spec, conv))} process flow(s) render")
    _nodes(spec, conv, report)
    _review(spec, conv, report)
    _reached(spec, conv, report)
    return report


def _reached(spec: Path, conv: Conventions, report: Report) -> None:
    """Every flow reachable from the main flow, where the corpus names one (`spe5-sr8`).

    Reached means drawn as a sub-flow of a reached flow, or linked from one. A flow standing beside
    the main flow and reached by neither is a chapter no reader starting at the top will find.
    """
    from goldspec import nodes as node_format
    from goldspec.review import expands

    if not conv.main_flow:
        return
    flows = {p.name: p for p in _flow_files(spec, conv)}
    if conv.main_flow not in flows:
        report.problems.append(
            f"the main flow {conv.main_flow} names no flow in {spec.name}/{conv.flow_dir}/ — "
            f"name a file there matching {conv.flow_glob!r}, or nothing can be reached from it")
        return
    chapters = {name: node_format.read(path) for name, path in flows.items()}
    reached, todo = set(), [conv.main_flow]
    while todo:
        name = todo.pop()
        if name in reached:
            continue
        reached.add(name)
        text = flows[name].read_text(encoding="utf-8")
        todo += [n for n in re.findall(r"\]\(([^)#\s/]+\.md)(?:#[^)]*)?\)", text) if n in flows]
        chapter = chapters[name]
        for drawn in (chapter.subflows if chapter else ()):
            todo += [n for n, c in chapters.items() if c and n != name and expands(drawn, c)]
    for name in sorted(set(flows) - reached):
        report.problems.append(
            f"{name} is neither drawn from the main flow nor referenced from a flow that is — draw "
            f"it as a step of {conv.main_flow} or of a flow under it, or link it from one")


def _review(spec: Path, conv: Conventions, report: Report) -> None:
    """The process checks, per flow file.

    Two lists and no flag between them. `review` holds what has an invariant and is a fault;
    `observations` holds what a reader has to judge and is counted. A flag over both meant turning
    one report off turned every real gate off with it.
    """
    from goldspec import review as process_checks

    flows = _flow_files(spec, conv)
    # This spec's chapters, and the chapters of every spec it names as a sibling. A sibling is read
    # for what it defines and never checked here — it is gated by its own run, where it is the
    # subject rather than the context.
    #
    # `conv.siblings` was parsed, validated, resolved and then read by nothing. So `siblings` in a
    # `goldspec.toml` and `--sibling` on the command line both did exactly nothing, while the line
    # this function prints said an element was taken by nothing "in this chapter **or anywhere
    # linked**" — asserting a corpus-wide search on a run that had linked nothing. A check that
    # says out loud that it looked is the worst one to have looking nowhere.
    linked = list(flows)
    for other in conv.siblings:
        linked += sorted((Path(other) / conv.flow_dir).glob(conv.flow_glob))

    for path in flows:
        report.problems += process_checks.review(path, linked, _chapter_prefix(path, conv))
        seen = process_checks.observations(path, linked)
        if seen:
            report.checked.append(
                f"{path.name}: {len(seen)} observation(s) — an element nothing downstream takes is "
                f"a flow's product about as often as it is waste, so this is read and never gated")
            # And what they were. A count is not what the run saw, and a reader told only that
            # there are two of something cannot decide anything about either — which is the whole
            # of what an observation asks of them.
            report.checked += [f"  {line}" for line in seen]


def _flows_drawn(chapter, chapters: dict) -> set:
    """The sub-flow steps of ``chapter`` that another chapter expands."""
    from goldspec.review import expands

    return {d for d in chapter.subflows
            if any(c is not chapter and expands(d, c) for c in chapters.values())}


def _nodes(spec: Path, conv: Conventions, report: Report) -> None:
    """The chapters written as flows, over the whole spec at once.

    **A chapter is held to the shape it is written in, and nothing else.** One without a `## Nodes`
    section is read the old way and *counted*; it never reaches these checks, so a corpus that
    predates the format cannot be failed by them. That is what makes the checks unconditional —
    there was once a flag deciding whether the count was a fault, and once the checks stopped
    demanding one shape of everybody it could only ever have suppressed real findings in chapters
    that had adopted the format.

    Corpus-wide for the same reason `ch15` is: a node moving an element a neighbouring chapter
    defines is correct, and one moving an element nothing anywhere defines is a defect, and from
    inside a single file those are the same sentence.
    """
    from goldspec import nodes as node_format

    flows = _flow_files(spec, conv)
    converted = {}
    for path in flows:
        chapter = node_format.read(path)
        if chapter is not None:
            converted[path] = chapter

    report.checked.append(
        f"{len(converted)} of {len(flows)} chapter(s) in the node format, "
        f"{sum(len(c.nodes) for c in converted.values())} node(s)")

    if not converted:
        return

    for path, chapter in converted.items():
        prefix = _chapter_prefix(path, conv)
        # Ids the flow draws, excluding the kinded ones — an unknown, a decision and a parameter are
        # attached to a node rather than being nodes, so requiring a block for each would demand an
        # expansion of a thing that is not a step.
        # Off the parsed chapter, never off the markdown again: the diagram had two readers and
        # they disagreed about which ids it draws, so a check could read an empty set and pass
        # without comparing anything.
        # A main flow's steps that are whole flows carry those flows' prefixes, not its own.
        flows = _flows_drawn(chapter, converted) if path.name == conv.main_flow else set()
        drawn = {i for i in chapter.var2id.values() if i.startswith(prefix)} | flows
        found = node_format.faults(chapter, prefix, drawn, flows)
        report.problems += found



