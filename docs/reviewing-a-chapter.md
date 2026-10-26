# Reviewing a chapter

**Last updated** 2026-10-26 v4

**For anybody reading a chapter and deciding whether it is right — including the person who wrote it.**

The gates check what has an invariant. This is the rest: the judgements a reader has to make, the
questions that separate one kind of thing from another, and the failures that look like style and are
not. Where a check exists, it is named; where none can, that is said.

## The one question that settles most of it

**Does a person do it?**

A process flow is a sequence of acts. A node's text is the shortest description of what somebody
does. If a box states something about the system rather than something a person performs, it is not a
node — however true it is, and however much it looks like one.

*keep the core language-blind* is not a step. Nobody performs it. It has no position in a sequence,
which is why no amount of rewording gives it one. It is a **requirement**, and it belongs on the node
it constrains.

This is the single most common defect in a corpus written before the question was asked. It produces
boxes that cannot be ordered, cannot be chained, and cannot be tested.

## Where a claim belongs

Five questions, asked in order, and the first *yes* is the answer. They sort a claim into where it
is written — which is a different question from
[the four kinds of subject](getting-started.md#the-four-kinds-of-subject), which sorts a thing that
already has an id by what would settle it. A claim reaching the second row here is a story, and a
story is one of those four.

| ask | if yes |
|---|---|
| Does a person do it? | a **node** |
| Is it ever *done*? | a **story** — cited with `proves`, and it carries a depth |
| Is it a standing commitment evidence accumulates against? | a **decision** — cited with `informs`, no depth, never reads PROVEN |
| Is it a constraint the work must satisfy? | a **requirement** — UR, SR or NFR on the node it constrains |
| Is it something the tool deliberately does not do? | a **boundary** — an NFR, not an unknown |

*Depth*, *PROVEN* and *the board* are [Plumb](https://plumbspec.org/)'s words: Plumb runs the
tests, reads the marks they carry, and derives how deeply each story is proven onto a board.
goldspec checks only that the ids a test cites resolve to subjects in the spec — see
[cite the spec from a test](getting-started.md#10-cite-the-spec-from-a-test).

**Where the citation lives is not in the chapter.** `proves` and `informs` are carried by the
annotation on the test, and the depth is derived by a run and reported on the board. A chapter that
also names the tests that prove it is carrying a second copy that goes stale — the same defect as
reporting its own build status, and it passes every other gate.

The gate catches three shapes of it — a click link to a test file, a trace table keyed
by test name, and a `Spec source:` line. **A sentence that names a test in prose is not caught**, so
this one is mostly yours.

Plumb's and goldspec's own chapters do describe citation and depth, because for those two products
they are **features being specified**. That is a statement about what is built, not a claim that the
chapter is proven, and the two must not be confused.

Two traps here:

**Owning no elements does not make something a decision.** A story with an empty `Out` is still a
story. The test is *is it ever done*, not *does it produce data*.

**A gap you have decided not to close is a boundary, not an unknown.** An unknown says nobody has
decided. Writing *nothing checks that the backlog reads the status back* as an unknown implies the
tool ought to; writing *integration with a team's story management tool is not part of this* says the
decision is made. Unknowns that are really boundaries accumulate as false debt.

## Altitude

Every node in a chapter describes an act at the same level of granularity. A chapter that mixes
altitudes cannot be read in order, because the reader keeps changing how much they are being told.

Pick the altitude first, from the person: *what a developer does between picking up work and closing
it* is an altitude. *What the tool does between a command and a board* is a different one, one level
down. Write the whole chapter at whichever you picked, and let the steps that are too big drill down
into their own chapters.

**Altitude cannot be fully checked.** There is no invariant for *is this at the right level* — the
data cannot say what level the node was supposed to be at. What can be checked is a **shadow**: a row
or a requirement that names something the chapter already has as a node is probably a layer low, and
the gate reports that. A row described too finely that happens to collide with
nothing leaves no shadow, and only a reader will see it.

Look for: a requirement describing a mechanism the person never touches; a description naming a
command or a file where its siblings name business information; one row naming a whole collection
where the next names a single instance.

## Prose is a detector

**If the story is complete, and the requirements and unknowns are complete, there is no prose left to
write.**

Everything with an identifier can be tested. Prose cannot. So a paragraph inside a node is not a
style problem — it is a **requirement that has not been written yet**, and the fix is to find it and
give it an id, not to shorten the paragraph.

Delete a node's last remaining sentence. What it was hiding is usually a requirement or an open
question that never got an id.

## A spec states what is

Not what happened, not why, not what was tried. Specifically, none of these belong:

- **History.** *"The distinction was learned twice, expensively"*, *"both were tried in a week"*, a
  closed unknown with the date it closed. If a decision needs recording, record the decision.
- **Argument.** A paragraph defending a choice against an objection nobody raised. The story's *so
  that* is where the reason goes.
- **Anecdote.** *"The evidence is a…"* — a measurement needs no story around it.
- **Chapter self-description.** *"Twenty-one nodes, which is past the working threshold"*, *"this
  chapter has two sides"*. A spec does not report on its own size or structure.
- **Build status.** *"specified and unbuilt"*, *"nothing implements one"*. Whether something is built
  is derived from a run and reported on the board. A spec that says it is carrying a second copy that
  goes stale. The gate catches a short list of *build*-status phrases and a `classDef`
  named for whether a thing is built. **A status somebody typed — `Status: accepted`, *(done)* — is
  refused by nothing**, so that half is a reader's.

**Length is the tell.** More than a few simple statements and it has become an essay.

**Measurements stay; attribution goes.** A number needs no owner. *"measured at 346µs a round-trip"*
is a fact; *"measured on another team's suite"* discloses whose.

The gate catches a narrow band of this — a figure in the same sentence as *measured on
a…*, *the evidence is a…*, *the reference project*, or a possessive naming a pilot, customer, client
or adopter. It is deliberately narrow, because *a customer* is the business domain of half the specs
anybody will write and a matcher that fired on it taught readers to stop reading the output. **The
example above is outside that band**, and so is most phrasing. Read for it.

## Stories

The **so that** is the person's benefit, not the system's achievement.

> so that there is something for the tests to be true of ← the mechanism
> so that the end-user gets their functionality ← the benefit

The role is a role — *an IT professional*, *a developer* — not somebody defined by their relationship
to this document. *As somebody deciding whether to trust this tool* is a reader of the spec, not a
user of the product.

## Identifiers

Identifiers exist so that people in a room can point at a thing by name. Everything gets one, because
the time a design session spends *finding* what is being discussed is enormous.

- **They must sort with a plain sort**, so left-pad each number to the width its own largest member
  needs. A series numbered no higher than 9 uses one digit; adding a tenth takes the whole series to
  two and rewrites every one of them. The gate checks it.
- **Renumbering is forever, and that is accepted.** The burden falls on whoever maintains the corpus
  rather than on everyone reading it. It is affordable only because the rewrite is one audited pass —
  rename one subject and every citation to it moves at once.
- **An id is issued once and never reissued.** Rewording a subject keeps its id; changing what it
  claims does not — that is a new subject, and the old proofs must not follow it.
- **An id written as an example is spelled without a prefix**, so a rewrite of real identifiers cannot
  reach it. A chapter documenting its own numbering otherwise fails its own numbering
  check, and breaks the script renumbering it.

## The stamp

Every chapter carries `**Last updated** YYYY-MM-DD vN` immediately under the title, optionally
followed by `derived` or `authored`.

The version is not decoration. A chapter revised between a morning session and an afternoon one is two
documents on the same date, and a room needs to know which is on the table. **Every change is a
version, including a typo** — a misspelling in a requirement stops a session while people work out
whether it is a mistake or a distinction. The gate checks the stamp's shape; where it sits
is not checked.

## What a node owes, structurally

Five headings inside a node block, in one order: `Information`, then the three kinds of
requirement, then `Unknowns`. The order is held rather than suggested, for the reason the glossary
goes last — a reader looking for what constrains a step should not have to hunt for it.

**A requirement is named for the step it is stated under**, and an id is issued once. A constraint
filed on one step and named for another resolves to whichever a reader finds first, which is the
same defect as two claims wearing one id. All three are checked.

**The three kinds are apart because three readers argue with them.** What the person needs, what
the system must do, and what holds whatever the design. Running them together costs every later
reader the search.

## Information, and what it is for

A node's Information table is what the person needs (In) and what they leave with (Out). Two things
are derived from it, and both find real defects:

**The chain.** Every In must be an earlier Out, handed in by the parent, or arrive from outside the
flow — `authored`, `observed` or `generated`. A gap means either
a step is missing an output or **a whole step is missing**. The chain finds an unclaimed step from the
data alone, without the chapter having to admit it in prose, and finds a missing step nobody has
noticed at all. The gate checks it.

**What accumulates.** Information a node leaves with that no later step consumes is work being done
for nobody, and that is where process inefficiency is found. A step that keeps something to itself says so
as a requirement. The run lists each one as an *observation*, after searching every chapter it
reads for a step that takes it — and counts it rather than failing on it, because a flow's own
product, such as a confirmation sent to a customer, looks identical to waste from the data alone.

## What the gates cannot see

A run reports two kinds of finding, and nothing switches either off. **Faults fail it**: the
chain, provenance, the stamp, padding, prohibitions, build status, a named test, an attributed
figure, a row that restates a step, and the sub-flow checks. **Observations are counted and never
fail it** — information nothing downstream takes is the whole of that list, because it has no
invariant to hold.

Read the output knowing:

- **A check passing on a format it cannot parse is worse than no check.** `0 fault(s)` looks the
  same whether the gate read your chapter or nothing at all, so read the counts above it — subjects,
  flows that render, chapters in the node format, nodes — and confirm they are the size of what you
  wrote.
- **A sub-flow's entry point is not a chain fault.** A row whose provenance is `parent` answers
  *where does this come from* with something outside the flow, exactly as `authored` does, so the
  chain passes over it rather than reporting it unproduced. What holds the two sides together is
  the sub-flow check, which reads the parent's node against the chapter it drills into. A chain
  fault on any row is a real finding; none of them is expected and dismissed.
- **Observations cannot see a later run.** A cursor written today is read tomorrow by the same
  chapter, and no reading of the flow will find that.

## Failures worth knowing about in advance

- **Matching the surrounding style instead of the current one.** Writing a new node in the shape of the
  chapter it lands in, rather than the shape now in force. If you touch it, it comes to the current
  format.
- **Matching a claim by its system-side consequence.** Two subjects whose bodies end in the same
  guarantee are not duplicates if a person does different things in them. Compare what a person
  does, not what the system ends up promising.
- **Reporting a pass from a checker that could not read the file.** See above.
- **Renaming a file without checking inbound links.** A rename is a citation change.
- **Inventing a value where one already exists.** A legend colour the corpus has already settled is
  not yours to choose again.
- **Running a search and calling it an audit.** A search finds instances of what you thought of.

## A removal must not announce itself

A spec is published surface, and so is everything around it. When a chapter stops saying something
because it should never have said it, the change is described by what the chapter now claims — not
by what left. Branch names, commit subjects, commit bodies and code comments all travel with the
repository and all carry it straight back. Say what changed — *corrected the spec to reflect what
the product offers* — and nothing more.

This is about redaction. A commit converting an existing document is not a removal in that sense:
it says what was converted and what was retired, because that is the change
([getting started §13](getting-started.md#13-bringing-in-a-document-you-already-have)).

The same applies to a guide like this one: **every example here is synthesised, or drawn from this
method's own corpus.** A guide that teaches people not to leak, illustrated with the thing being
protected, is the leak.
