"""Faults that stop a process flow rendering, found by reading it.

A flow that does not render is worse than one that is wrong: it fails **silently and completely**,
and every gate we have still passes because they parse the markdown around the diagram rather than
the diagram itself. Either fault below takes a whole diagram with it, and neither is
caught by anything that parses the markdown around the fence.

Pure source scan, so it costs nothing and therefore always runs.

Reached through ``goldspec.specgate``, so the ``goldspec`` command runs it and an adopter gets it
along with everything else the methodology checks. That is the opposite of what this said while the
gate lived inside Plumb, where the point was that a *tool* has no business deciding whether a
project draws diagrams. goldspec is not the tool: drawing flows is one of the conventions somebody
adopts by installing it, so checking that they render is squarely its business.
"""

import re
from pathlib import Path

#: Brackets that open a node label. Deliberately not `>` or `(`: the `id>"text"]` shape is always
#: written quoted, and `>` also appears in every `<b>`, `<br/>` and `-->` on the line — matching it
#: produced a false positive on almost every diagram in the repository, which is worse than the
#: fault it was looking for.
_OPENERS = {"[": "]", "{": "}"}

#: The parameter shape, `P1>"a label"]`, matched at the head of a node definition.
#:
#: `>` cannot go in `_OPENERS`: it is in every `<b>`, `<br/>` and `-->` on the line, and matching
#: it produced a false positive on almost every diagram here. So the shape is found where it is
#: unambiguous — a node name at the start of a line, then `>` — which is the only place it can
#: legally appear. Without this the one shape the tutorial singles out as "the one shape where
#: quoting is not optional" was the one shape never scanned.
_PARAMETER = re.compile(r"^\s*[A-Za-z_]\w*>(?!=)(.*?)\]\s*(?::::\w+)?\s*$")

#: Characters an *unquoted* label cannot contain. Mermaid reads each as the start of another shape,
#: so the parse dies and takes the **whole diagram** with it — the same total, silent failure as a
#: bare quote, which is why they belong in the same check rather than a new one.
#:
#: `(` was the one that got through. A hexagon reading `{{... (dec1-U4)}}` passed this gate and
#: rendered nothing, which is precisely the fault this module exists to catch, so the rule is now
#: the general one rather than the single character that happened to be found first. Established
#: against mermaid's own parser across every shape — `[]`, `{}`, `{{}}`, `>]` — and quoting fixes
#: all of them.
_UNQUOTABLE = '"([{'
_CLASSDEF = re.compile(r"^\s*classDef\s+(\S+)\s+(.*)$")
_CLASS_USE = re.compile(r":::(\w+)")

#: Classes for a node that is attached to the flow rather than part of it — a value
#: to discover, a question nobody has answered. Terminal by construction, so neither
#: is an ending the start-and-end check should accept.
_HANGS_OFF = {"unknown", "parameter"}


def faults(paths) -> list[str]:
    """Every rendering fault in these markdown files, as lines a reader can act on."""
    found: list[str] = []
    for path in sorted(Path(p) for p in paths):
        for start, block in _mermaid_blocks(path):
            found += _block_faults(path, start, block)
    return found


def _mermaid_blocks(path: Path):
    """Each fenced ```mermaid block as (first-line-number, lines)."""
    lines = path.read_text().split("\n")
    blocks, current, start = [], None, 0
    for number, line in enumerate(lines, start=1):
        if line.strip().startswith("```mermaid"):
            current, start = [], number
        elif current is not None and line.strip() == "```":
            blocks.append((start, current))
            current = None
        elif current is not None:
            current.append(line)
    return blocks


def _bare_delimiter(line: str) -> str:
    """The character breaking an unquoted label, or `""`.

    Mermaid reads `"`, `(`, `[` and `{` as delimiters, so any of them inside a label that was not
    opened with a quote is a parse error — and it takes the **entire diagram** down rather than the
    one node. Quoting the label is the fix in every case.
    """
    index = 0
    while index < len(line):
        closer = _OPENERS.get(line[index])
        if closer is None:
            index += 1
            continue
        # `[[gate]]` and `{{hexagon}}` double both ends, so a scan that assumed one character
        # read the label as starting at the *second* bracket and called every gate in every
        # diagram a fault — a rate that would have got the whole check deleted.
        run = 2 if line[index + 1:index + 2] == line[index] else 1
        end = line.find(closer * run, index + run)
        if end == -1:
            index += 1
            continue
        label = line[index + run:end]
        # Compound shapes — `([stadium])`, `[(cylinder)]`, `[/slanted/]` — leave one delimiter at
        # each edge of what is otherwise an ordinary label.
        if len(label) > 1 and label[0] in "([{/\\" and label[-1] in ")]}/\\":
            label = label[1:-1]
        if not label.startswith('"'):
            found = [c for c in _UNQUOTABLE if c in label]
            if found:
                return found[0]
        index = end + run
    return ""


def _block_faults(path: Path, start: int, block: list[str]) -> list[str]:
    found, defined, used = [], set(), set()
    for offset, line in enumerate(block, start=1):
        where = f"{path.name}:{start + offset}"

        bare = _bare_delimiter(line)
        if not bare:
            shaped = _PARAMETER.match(line)
            if shaped and not shaped.group(1).startswith('"'):
                found_in = [c for c in _UNQUOTABLE if c in shaped.group(1)]
                bare = found_in[0] if found_in else ""
        if bare:
            found.append(f"{where}: a bare `{bare}` inside an unquoted label — quote the label or "
                         f"the whole diagram fails to render: {line.strip()[:70]}")

        declared = _CLASSDEF.match(line)
        if declared:
            defined.add(declared.group(1))
            if "color:" not in declared.group(2):
                found.append(f"{where}: classDef {declared.group(1)} sets no `color:` — node text "
                             f"falls back to the reader's theme and vanishes on one of them")
        used.update(_CLASS_USE.findall(line))

    for name in sorted(used - defined):
        found.append(f"{path.name}: `:::{name}` is used but no classDef defines it — the node "
                     f"renders unstyled and the mistake is invisible")
    return found


#: A node definition: `NAME[label]`, `NAME([label])`, `NAME{label}`, `NAME>label]`, `NAME[[label]]`.
_NODE = re.compile(r"^\s+([A-Za-z_][A-Za-z0-9_]*)\s*(\[\[|\(\[|\[|\{|>)(.*?)(\]\]|\]\)|\]|\})(:::\w+)?\s*$", re.M)
#: An edge, solid or dotted, labelled or not.
#: A node may carry its shape inline on either side of an edge — `A[a] --> B[b]` is as valid as
#: naming both above and writing `A --> B`. Skipping the shape is what lets both read the same.
_SHAPE = r"(?:\[\[.*?\]\]|\(\[.*?\]\)|\[.*?\]|\{.*?\}|>.*?\])?"
#: One hop of a chain: an arrow, an optional label, and the node on the far side.
#: Written as a scan rather than a match of the whole line, because `A --> B --> C` is one line
#: carrying two edges and reading only the first is how `C` came to look like a node nothing points
#: at. Every chapter the tutorial teaches is drawn that way, so the start-and-end check was
#: answering about a graph the chapter does not have.
_HOP = re.compile(
    rf"[-.=]+[^>\n]*>\s*(?:\|[^|]*\|\s*)?([A-Za-z_][A-Za-z0-9_]*){_SHAPE}")
#: The node a chain starts from, at the head of the line.
_HEAD = re.compile(rf"^\s+([A-Za-z_][A-Za-z0-9_]*){_SHAPE}\s*(?=[-.=]+[^>\n]*>)", re.M)


def _edges(source: str) -> list:
    """Every ``(from, to)`` the diagram draws, including each hop of a chain."""
    found = []
    for line in source.splitlines():
        head = _HEAD.match(line)
        if not head:
            continue
        previous = head.group(1)
        for hop in _HOP.finditer(line, head.end()):
            found.append((previous, hop.group(1)))
            previous = hop.group(1)
    return found


def terminals(source: str) -> tuple[list[str], list[str]]:
    """The nodes a flow begins at and ends at, derived from the edges rather than declared.

    A start is a node with a way out and nothing pointing at it; an end is a node something
    reaches and nothing leaves. **Both halves are load-bearing.** Asking only *is it pointed at*
    counts every node that is drawn and never connected — a legend, which this dialect asks every
    chapter to ship, is seven of them — so the check had a start and an end on any chapter
    carrying one, whatever its flow actually did.

    Unknowns and parameters are excluded from both. They hang off the flow deliberately and are
    terminal by construction, so counting one as an ending would let a flow satisfy this check by
    having an unanswered question in it, which is the opposite of what the check is for.
    """
    nodes = {m.group(1): (m.group(5) or "")[3:] for m in _NODE.finditer(source)}
    # The shape is what makes a parameter one (`>"…"]`), so it hangs off the flow whatever class it
    # was given: without `:::parameter` it was counted as an ending, and a flow that never ended
    # passed for having a value to tune.
    shaped = {m.group(1) for m in _NODE.finditer(source) if m.group(2) == ">"}
    edges = _edges(source)
    for a, b in edges:
        nodes.setdefault(a, "")
        nodes.setdefault(b, "")
    sources = {a for a, _ in edges}
    targets = {b for _, b in edges}

    starts = [n for n, cls in nodes.items()
              if n in sources and n not in targets and cls not in _HANGS_OFF and n not in shaped]
    ends = [n for n, cls in nodes.items()
            if n in targets and n not in sources and cls not in _HANGS_OFF and n not in shaped]
    return starts, ends
