# Changelog

What each release gives you, and what to change to take it.

## Unreleased

**One main flow, and one tree under it.** Name the flow a corpus starts from with `main_flow` in
`goldspec.toml`. Every other flow is a drill-down of the step it is entered from, named for that
step, so the file names alone show where each chapter sits. Once the main flow is named, a flow
neither drawn from it nor linked from a flow that is fails the gate.

**What a sub-flow makes and takes below itself never left it.** A step was told to declare an
element its sub-flow's own drill-down consumed, because the chapter below the sub-flow counted as
another chapter. Found by the first corpus three levels deep.

## 0.2.0 — chapters that are stories, and one Python

**A chapter is a set of stories, not a table.** Every step of a flow is somebody's story — a role,
what they want, and what it gets them — and each step carries its own requirements: what the person
needs, what the system must do, and what holds whatever the design. They sit with the step they
constrain, so you can read a step on its own.

**References nest.** A subject drilled into carries its parent's id, so `dev07-1-3` tells you where
it sits and you keep no second index in step with it.

**Information traces between diagrams.** Each step states what it takes in and what it leaves
behind, and every row says where it came from. An element produced in one flow and consumed in
another reads as that, so you can follow a corpus end to end.

**One Python.** goldspec runs on 3.9, down from 3.11. On RHEL 9 and Ubuntu 22.04 the `python3` you
already have is enough.

### Convert at your own pace

Chapters in the older shape still pass. Convert a chapter at a time and the gate fails neither half
for being the half it is — no flag to set, none to remember to unset.

### The run now tells you what it read

`0 fault(s)` used to be the whole answer whether the gate had parsed six subjects or found no
chapters at all. Every run now says how many subjects it declared, how many flows it read and how
many chapters it parsed — so a spec the gate cannot see reads as that rather than as a pass. It
also prints the observations it finds: information a step leaves with that nothing downstream
takes, which is counted and never fails a run.

Those lines go to stderr, so `goldspec spec > report.txt` still captures exactly the faults and
their count.

### Checks that were looking at nothing

**`siblings` did nothing.** Naming another spec directory — in `goldspec.toml` or with
`--sibling` — was parsed, validated and then read by no check, while the run said an element was
taken by nothing "in this chapter **or anywhere linked**". A corpus that spans repositories is now
actually read across them.

**Padding was dead for a renamed flow.** The check took its id prefix from the file name, so a
project whose flows are `story-*.md` had it looking for ids beginning `story` — it found no series
and passed. It uses your conventions now, like every other check.

**A diagram indented by anything but exactly four spaces read as naming no nodes.** That silently
turned off the chain, the provenance reachability check and the unconsumed report together, while
reporting every node in the chapter as absent from its own flow.

**What the parser could not read, it dropped.** A table row with no id, or an `IO` outside the set,
vanished before every check — so an unidentified required input from a step that does not exist
passed clean. A requirement bullet written `ch1-2-ur1: …` instead of `ch1-2-ur1 - …` did the same,
and took the ownership and duplicate checks with it. Both are named now. `-`, `–` and `—` all read
the same in a bullet, as they already did in a heading.

**An open unknown can be cited.** It is one of the four kinds of subject and was the one kind the
declared set could not contain, so a test citing one was told it was declared nowhere.

### Two checks that could not fail

**A flow's start and end.** `A --> B --> C` on one line is two edges and only the first was read,
so the check was answering about a graph your chapter does not have. A node drawn and never
connected also counted as both a start and an end — and the legend this method asks every chapter
to ship is seven of those, so any chapter carrying one passed whatever its flow did.

**A constraint stated for the whole flow.** A decision or parameter written between the diagram and
`## Nodes`, which is where the format puts one that is genuinely not any single step's, was not
read at all: it could not be cited, and it was held to no namespace. It is a subject now, sharing
one number series with the ones at a node.

### A chapter named by its sigil can declare a decision

`ch1-D1` read and `snd-D1` did not: the pattern required a number after the sigil, which is true of
`chapter-01-ordering.md` and false of a corpus that names its flows `hol-…` or `snd-…` and numbers
its nodes `hol1`, `snd1`. A decision spelled the only way consistent with those nodes was declared
nowhere, held to no namespace, and reported as no fault — the gate could not see it to refuse it.

### A run says what it judged by, whichever door you came in

Every fault this gate emits is a statement about your corpus, and the one cause none of them can
phrase is having been handed the wrong strings. The command has named its basis on every run for
that reason; the library had no equivalent, so a project calling `check_spec_directory` with a
`Conventions` it built itself had nothing to check it against.

The report now opens with the conventions it read by, and a glob that matched nothing says so
against what is actually there:

    conventions: ids namespaced 'ch', flows in diagrams/chapter-*.md
    spec/ declares no subjects at all — … matched 0 of the 7 markdown file(s) there …

Reported by a project whose corpus of 34 nodes came back as declaring nothing: the namespace had
been corrected and `flow_glob` left at its default, so the glob matched no file and the verdict
read as being about their spec.

### One dotted-name rule, read the same way by both checks

A name and its parts relate one way per question: a producer of the whole supplies a taker of a
part, and a taker of a part reads a producer of the whole. Neither reverses.

`cross_flow` had it backwards in one direction — any chapter consuming `order` made every `order.*`
a sub-flow produced look wanted, so a parent was told to declare a transit because an unrelated
flow elsewhere took the whole. The fault landed in a chapter whose author had not touched it.

The rule was implemented twice and written down nowhere, which is how the two copies came to
disagree. It is `spe5-sr7` now.

### Smaller things

- `goldspec --version` answers with the version you installed, where it could answer with an older
  one.
- The documentation was rewritten against the tool. Four writers built a chapter from it and the
  gate passed all four first time; what they found on the way is fixed — the node block as it is
  actually shaped, which provenance is legal on an `In` and which on an `Out`, what a drill-down's
  ids look like, the stamp every chapter is checked for, and one table of everything the gate
  refuses.
