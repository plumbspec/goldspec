# Changelog

What each release gives you, and what to change to take it.

## 0.5.0 — a file is named for its ids' prefix

**A file is named for its ids' prefix.** `chapter-1-….md` holds `ch1`, `chapter-1.09-….md` holds
`ch1-09`, and `chapter-01-….md` holds `ch01`.

**Every id in a series has the same number of digits**, as many as its largest needs. Every
reference to it carries the same digits: the id where it is declared, a test's citation, a link,
and a file name. A series is one kind of id under one parent:

| series | up to nine | ten or more |
|---|---|---|
| chapters | `ch1` … `ch9`, in `chapter-1-….md` | `ch01` … `ch10`, in `chapter-01-….md` |
| a flow's steps | `ch1-1` … `ch1-9` | `ch1-01` … `ch1-10` |
| a drill-down's file | `chapter-1.3-….md` | `chapter-1.03-….md` |
| a drill-down's steps | `ch1-3-1` … `ch1-3-9` | `ch1-3-01` … `ch1-3-10` |
| one step's user requirements | `ch1-3-ur1` … `ur9` | `ch1-3-ur01` … `ur10` |
| one step's system requirements | `ch1-3-sr1` … `sr9` | `ch1-3-sr01` … `sr10` |
| one step's non-functional requirements | `ch1-3-nfr1` … `nfr9` | `ch1-3-nfr01` … `nfr10` |
| one step's unknowns | `ch1-3-u1` … `u9` | `ch1-3-u01` … `u10` |
| one step's Information rows | `ch1-3-inf1` … `inf9` | `ch1-3-inf01` … `inf10` |
| a chapter's decisions | `ch1-D1` … `D9` | `ch1-D01` … `D10` |
| a chapter's parameters | `ch1-P1` … `P9` | `ch1-P01` … `P10` |

Reaching ten renumbers the whole series and every reference to it. A tenth step turns
`@pytest.mark.proves("ch1-3")` into `proves("ch1-03")`, turns `[charging](chapter-1.3-charging.md)`
into `[charging](chapter-1.03-charging.md)`, and turns the requirement `ch1-3-ur1` into
`ch1-03-ur1`.

**To take it:** rename a file whose name carries a zero its ids don't. `chapter-01-ordering.md`
holding `ch1` becomes `chapter-1-ordering.md`, and `main_flow` and any links naming it change with
it. The gate names every file that needs it.

## 0.4.0 — one main flow, said on the front page and by the gate

**A corpus of top-level flows side by side is warned of.** Where no `main_flow` is named, the gate
cannot hold a corpus to one tree, so a set of unrelated flows passed silently. The run now warns
when more than one flow is entered from nothing, names them, and suggests the one that reaches the
most as the main flow. It is a warning on stderr; the exit code is unchanged. Naming `main_flow`
still turns an unreached flow into a fault.

**The rule is on the README's front page.** A chapter is a process flow, and a step that is itself a
process drills into its own chapter, named for that step. The worked example names its main flow,
and Getting started opens with its main flow and drill-down.

**goldspec lives at [gold.plumbspec.org](https://gold.plumbspec.org/).**

Nothing to change to take it. goldspec's own spec numbers `spe5`'s system requirements `sr01`…`sr10`;
that matters only to something citing goldspec's own ids.

## 0.3.1 — how to verify it, and where to report

**New.** `SECURITY.md` says how to check a release against its checksums and signature, and names
the signing key. `CONTRIBUTING.md` says how to run the suite and the gate. Vulnerability reports
and proposals for a large change go to [support.plumbspec.org](https://support.plumbspec.org).
The package links to plumbspec.org and its source.

## 0.3.0 — one tree, and a gate a newcomer can follow

**One main flow, and one tree under it.** Name the flow a corpus starts from with `main_flow` in
`goldspec.toml`. Every other flow is a drill-down of the step it is entered from, named for that
step, so the file names alone show where each chapter sits. Once the main flow is named, a flow
neither drawn from it nor linked from a flow that is fails the gate.

**What a sub-flow makes and takes below itself never left it.** A step was told to declare an
element its sub-flow's own drill-down consumed, because the chapter below the sub-flow counted as
another chapter. Found by the first corpus three levels deep.

**A chapter is held to every number its name carries.** `chapter-01.2.2-….md` expands `ch1-2-2`;
the gate read only the first two numbers, so a third-level chapter could file its steps under any
step of its grandparent and pass.

**Citing a requirement names the step to cite instead.** A test citing `ch1-1-ur1` was told the id
was declared nowhere, though it plainly was; it is now told the requirement belongs to `ch1-1`, and
that a test cites the step.

**A misnumbered chapter is reported as misnumbered.** Its steps were also reported as not in the
flow, though they were drawn and connected; the namespace fault now says the file name may be the
side that is wrong. The conventions line names the main flow when one is set.

**A requirement in a `-` or numbered bullet is named, not skipped.** Documents being converted
write requirements as `- R1 …` or `1. R1 …`; those were silently ignored, so no check held them.
They are now reported as written in a shape nothing reads.

**A link to a chapter nobody wrote is reported.** A hand-off linked before its chapter exists, or to
a misspelling of one, read as reaching it.

**A parameter is never a flow's end.** Drawn without its `:::parameter` class it was counted as one,
so a flow that never ended passed the check for having a value to tune.

**A sibling spec is read under its own conventions.** It was read with this spec's file pattern, so
a sibling that named its chapters differently was read as holding nothing, and every word borrowed
from it looked defined nowhere.

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
