# Writing a process flow

**Last updated** 2026-09-14 v8

[`reviewing-a-chapter.md`](reviewing-a-chapter.md) is the test a chapter has to pass. This is the
other half: how to write one so that it passes.

Everything here is a habit that costs rework when it is missing. Where a check exists, it is named;
where none can, that is said.

---

## 1 · Write from the person, never from the solution

The single error underneath most of the others. *Keep the core language-blind* cannot be placed as a
step, because it is a statement about the system and a flow is a sequence of acts. Rewording does
not help; it was never a node.

**Describe what the product does from a user's perspective.** A chapter is what somebody does
between one intention and the next, and nothing in it is true of the system alone.

The tell that a writer has slipped is hunting for *where does this go as a node*. When that hunt
starts, the answer is almost always that it is not a node — it is a requirement on one, or a
boundary.

## 2 · The five questions, in order

Asked of every claim before it is written anywhere:

| ask | if yes |
|---|---|
| Does a person do it? | a **node** |
| Is it ever *done*? | a **story** |
| Is it a standing commitment evidence accumulates against? | a **decision** |
| Is it a constraint the work must satisfy? | a **requirement** |
| Is it something the product deliberately does not do? | a **boundary**, written as an NFR |

The fifth is the one most often failed. Writing *nothing checks that the backlog reads the status
back* as an unknown quietly assumes the product ought to. **An unknown says nobody has decided; a
boundary says somebody has.** Unknowns that are really boundaries accumulate as false debt.

## 3 · The sixth question, asked whenever a step fails the person test

Two looks, not one: **each step a person has to take, then what the product enables.** Running only
the first produces a wrong remedy that passes every gate.

A step like *take the opening reading* fails *does a person do it* — the tool takes it, and nobody
present consumes it. The tempting conclusion is that it demotes to a system requirement. The right
answer is often a **question node**: the step is where an optional feature enters the flow, and the
person's act is real but earlier — they declared the feature in their configuration. The five-kinds
table has no row for *a step of an optional feature*, so classifying harder never finds it; the
answer lives in the diagram vocabulary rather than the claim vocabulary.

So, whenever a step fails the person test: **which product capability does this serve, and did a
person opt into it somewhere — a declaration, a configuration, an install?** If yes, the step lands
behind a question node whose answer is that earlier choice, required within the branch, with the
branch carrying the optionality. Only where there is no capability or no opt-in does it demote to a
requirement.

The rule sorts a corpus cleanly: mechanism nobody chose is a system requirement; a feature opted
into is a branch. The two sides of one feature mirror — the same question node where it is entered
and where it is left — so a reader of either sub-flow sees the other's shape.

## 4 · The story's *so that* is a person's benefit

The most expensive habit on this list, because it is corrected one story at a time:

> so that there is something for the tests to be true of → **so that the end user gets their functionality**
> so that the cost of a bad close lands on the person who can see it → **so that it is easy to resume from where I left off**
> so that *done* comes out of a run rather than out of my own judgement → **so that *done* informs my own judgement**

The first two are the same mistake: justifying the design instead of saying what somebody gets. The
third is worse than a style defect — it changes the claim. A method that proves the *shape* of a
proof and never its meaning must not describe a run that replaces a person's judgement, because that
is something it explicitly refuses to be. **Writing the benefit from the mechanism makes the product
overclaim.**

And the role is a role. *A developer*, *an IT professional*, *somebody accounting for a day*. Not
*somebody who will want to know what the day moved* — that is a person defined by their relationship
to the document rather than to the work.

## 5 · Say what a thing is, not what it is not — in a positive, active voice

**Entrances and exits.** A flow *exits to* the next thing; it never *leaves to* it. An entrance is
an exit seen from the other side, and the pair is symmetric; *leave* has no entrance to pair with.

> nothing in this flow writes a status → **this flow derives status**
> configuring is a repair → **configuring is an enhancement**

Both are one word, and both are product claims. A prohibition also reads as a constraint filed as a
step, which is the shape `review.prohibitions` exists to catch. Prefer the positive; it is shorter
and it is checkable.

The same rule reaches sentence shape:

> so that the word carries something nobody could have simply typed → **so that I can rely on it**
> so that the questions one run cannot answer have somewhere to be answered from → **so that the history shows status over time**
> so that what I do next comes from what was proven rather than from a log → **so that what I do next comes from what was proven**

A double negative shows the writer was arguing with an objection; the positive form states the
offer. The same pass retires *judgement* in favour of **claims** — the developer's work is not on
trial, their claims are being checked — and drops role qualifiers that accuse the reader (*whose
work is being judged*, *being told a story is done*).

## 6 · Prose in a node is a requirement not yet written

Everything with an identifier can be tested; prose cannot. So a paragraph in a node is not a length
problem — it is a missing requirement, and the fix is to find it and give it an id.

This is verifiable and it verifies. Deleting a node's one remaining sentence leaves it visibly thin,
and what the sentence was hiding is a real requirement or a real open question.

The same rule reaches inside a requirement. A bullet carrying *because …* or *…, where the cost of
being wrong lands on …* is a requirement plus an argument, and the argument belongs in the *so that*
or nowhere.

## 7 · One altitude, chosen from the person before anything is written

Pick the person first, then the span: *what a developer does between picking up work and closing
it*. Write every node at that level. Steps too big for it drill down into their own chapters; claims
too small for it are requirements on the node above them.

A layer can slip inside a single Information table — a row naming a command where its siblings name
business information. The check for this is weak by nature: `review.restates_a_step` finds a row
that collides with a node the chapter already has, and a row described too finely that collides with
nothing leaves no shadow at all. **Altitude is the thing a reader has to carry.**

Look for: a requirement describing a mechanism nobody touches; one row naming a whole collection
where the next names a single field of one instance.

## 8 · The diagram is authored; the ids follow it

Order the flow the way a person reads it — left to right, top to bottom. A diagram that jumps
backwards and forwards through its own numbering is unreadable, and no amount of correct content
fixes it.

Then the ids are renumbered to match. Renumbering a corpus costs every citation in it, and it is
affordable only because the rewrite is a single audited pass — which is what makes the subject that
owns renumbering load-bearing rather than incidental.

Identifiers exist so people in a room can point at a thing by name, and the time a design session
spends *finding* what is being discussed is enormous. So: everything gets one; they sort with a
plain sort; each number is left-padded to the width its own largest member needs and no wider; an id
is issued once and never reissued; and an id written as an example is spelled without its prefix, so
a corpus-wide rewrite cannot reach it.

**The scheme's pedigree is a statutory code**, where a commissioner is directed to assign every new
section its number; to codify, arrange, rearrange and generally update the code so as to maintain an
orderly and logical arrangement; and to publish an official report of all changes made in each
recodification. Those are the three id rules: numbers assigned centrally, rearrangement legitimate
in the name of orderly reading, and every renumbering one audited, reported pass. A citation
composes at most four levels, packing the last two into one number.

Two deliberate divergences:

  * **Nodes follow the statute; rows do not.** A node segment is a bare number — position already
    says *node*, exactly as position says *section* in a statute, and somebody doing the work never
    has to ask what a letter means. Row segments carry their kind (`inf`, `ur`, `sr`, `nfr`, `u`),
    because a row's kind is not positional and the tooling finds a series by it.
  * **A statute leaves numbering gaps** where a corpus renumbers densely — a legislature cannot
    rewrite the opinions that cite it, and a corpus can rewrite every citing file in the same
    audited pass. Dense numbers keep the sort natural and the keys short.

## 9 · Never overload a word

Collisions are cheap to introduce and expensive to find:

* **board** — a derived board is not a team's sprint backlog, and a flow about a developer's day
  touches both.
* **decision** — a fork in a process is not a closed-loop commitment evidence accumulates against.
  The diagram shape is a **question**.
* **elements** — a word already carrying a meaning should not be reused for what a step moves. They
  are **Information**: a document, a database lookup, a book, institutional knowledge.

Before introducing a term, check the glossary. If it is not there and it carries special meaning in
this chapter, it goes in the glossary in the same edit.

## 10 · The domain sequence is not derivable, so ask

Some orderings cannot be produced from the material at any level of care, because they are how a
particular team works rather than facts about the product:

* clarify what the story means, **then** pull — a pull happens as close to coding as possible
* annotate and write the tests **before** doing the work
* the failing loop returns to **the tests**, not to the work
* commit sits **inside** the loop, not after it
* the story id travels in the commit, the pull request **and** the merge
* it is a test *suite*, not a test

Ask for these. Do not infer them, and do not assume another team's answers are yours.

## 11 · Every row says where it came from

The Information table has five columns, and the fifth is **Provenance**. It exists because **a node
has to be readable on its own.** Anything that sends a reader to a diagram, an imports block or a
glossary to answer *where does this arrive from* will not be consulted under time pressure. The
answer sits in the row that raises the question, and nowhere else. An imports block that repeats the
table is a second copy that goes stale.

| the row is | it answers with |
|---|---|
| `In`, from a step of this flow | that step's id |
| `In`, at a sub-flow's entry | `parent` — the chapter this one drills into hands it in |
| `In`, from outside any step | `authored`, `observed` or `generated` |
| `Out` | `derived`, `authored`, `observed` or `generated` — how this node made it |

The vocabulary is not invented for the column; it is the one a corpus already uses to say where a
fact came from. Only `parent` is new, because sub-flows are.

Declaring it is not duplication of the diagram. The diagram says a step is reachable; the row says
which step actually produced the thing, and the two disagreeing is a defect `review.provenance`
reports — a node that both takes and writes one element, whose produced row was labelled with the
step the consumed row came from.

The column also separates two questions that run together. **`Required` asks whether the person must
have it; Provenance asks where it comes from.** A team's own backlog is required and has no
producer. A board has a producer and is not required, because on a first run no run has written one.

## 12 · The chain, and what accumulates

Every `In` is an earlier `Out`, handed in by a parent, or arrived from outside. A gap is either a
step missing an output or a whole step missing — and the chain finds it from the data alone, in
chapters whose prose had admitted the problem and in chapters where nobody had noticed at all.

And what the older shape's `Held` column was for: **information that accumulates with no later
consumer is work being done for nobody**, and that is where process inefficiency is found. There is
no `Held` column now; a step that keeps something to itself states it as a requirement, so the
element does not read as defined and used by nobody.

## 13 · If you touch it, it comes to the current format

Matching the surrounding style instead of the one in force is how a corpus stays half-migrated
forever. Transitional prose is defensible while transitioning and nowhere else.

Every chapter carries `**Last updated** YYYY-MM-DD vN` under its title. The version is not
decoration: a chapter revised between a morning session and an afternoon one is two documents on the
same date, and a room needs to know which is on the table. **Every change is a version, including a
typo** — a misspelling in a requirement stops a session while people work out whether it is a
mistake or a distinction.

## 14 · Redaction, and why a search is not an audit

A search finds instances of what you thought of. The material that must not go public is mostly
inferred rather than spelled: *the one consumer who can test it* states an install base without
naming a number; *a second adapter lands only when a second project adopts* does the same; a named
class from somebody's test scope discloses a third party's code.

The standing rules: declarative not historical · measurements stay, attribution goes · length is the
tell · never name a third party's code, architecture or posture · no count of adopters · no
commercial register · anything with a whiff of it is raised, not decided.

And a redaction must not announce itself. Branch names, commit subjects, commit bodies and code
comments are published surface, and *removed customer references* carries the fact straight back.
Say what changed and nothing more. The same applies to this document: **every example here is
synthesised or drawn from this method's own corpus, never from the material being protected.**

## 15 · The rebuild test

The completeness check for a converted chapter: **look at the code that cites each subject as it
moves, and ask whether that code and its tests could be rebuilt from the chapter alone.** A citing
test pins a rule; a rule the chapter no longer states is fidelity lost to the conversion, however
clean the gates run.

It finds real omissions in numbers — rules the citing tests pin and the first pass of a conversion
drops: that a refusal names the missing component rather than the class of failure, that a remedy is
a whole ordered list and never an append, that order outranks membership, that a stale installed
artifact is its own diagnosis, that a project with no build tool is asked nothing, and that a
refusal names the flag which proceeds anyway.

**And read the mechanism source, not only the tests — the configuration surface especially.** Tests
pin claims; only the source lists the tie-ins. Every configuration key is an input the flow must
show, and a chapter whose System Requirements read light has usually skipped this half: a whole
configured policy and a core-owned vocabulary can sit plainly in the source while every citing test
passes the scan. *System Requirements are getting light* is what that failure looks like from the
outside.

## 16 · What a checker can take off a reader, and what it cannot

Worth knowing before a review, because it says where the reading effort should go.

**A checker settles**, and a chapter passing them is not correct but stops spending a reader's
attention: an argument inside a requirement; a benefit clause naming the mechanism; a role that is
not a role; sibling rows at two granularities; a `Required` column with one value; a title that
disagrees with the parent's node text; a step drawn and never expanded, or expanded and never drawn.

**Only a reader catches**: a requirement that contradicts the diagram's order; a step announcing a
choice made two steps earlier; a reading differenced against something not yet produced; an element
one chapter writes and another never does. And altitude, which is why a word-by-word read has not
been retired.

**Only the owner settles**: where a step sits in their own sequence; whether a claim is worth
making; whether publishing an apparatus publishes a working method.

The route off word-by-word review is not *write more carefully*. It is to repair the checks that
read nothing, move the first bucket into the checker, and keep the reader for the second.

**A check passing on a format it cannot parse is worse than no check.** If a check says `ok`,
confirm it read something. The structural answer is one reader: the chapter is parsed once into an
object every check is a pure function of, so no check can form its own opinion of what a row says.
