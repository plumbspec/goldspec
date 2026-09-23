# Getting started

**Write your first chapter, understand every part of it, and get the gate green.**

This walks one complete chapter part by part. The chapter ships at
[`docs/example/`](example/), and goldspec's own test suite runs the gate over it on every run, so
what you read here is what the gate accepts.

You need `goldspec` installed and a directory. Nothing else — no project, no test suite, no language.

    mkdir -p spec/diagrams

A spec is markdown a person reads. There is no vocabulary to import and no module a runner has to
collect.

---

## 1. A chapter is a process flow

Not a subsystem, not a component, not a team's area. **A chapter is one process, from start to
done**, and it contains **many user stories** — one for every step in it.

That is the single most important sentence on this page, and getting it wrong produces a chapter
called *the payments service*, which accepts any sentence about payments and grows until nobody
reads it. A process has a start, an end, and steps in between; most sentences are not one of its
steps, so most sentences are refused on sight.

The chapter opens with the process's own story:

> **As a customer I want to place an order and be told it was accepted, so that I know I will be
> charged for something that is actually coming.**

### Every step is a user story too

A node in the flow is **something a person does for a reason** — so it takes the same shape:

> **As a customer I want to be told a line is short before my card is touched, so that I am not
> refunding money I should never have paid.**

| Part | What it is for | What goes wrong without it |
|---|---|---|
| **As a** \<role\> | who this step is for | a step with no role is a task, and tasks have no acceptance |
| **I want** \<something\> | what they are trying to do, in their words | written in the system's words it becomes a design note and stops being arguable |
| **so that** \<goal\> | why the step is worth performing | nothing can say the step is *finished* — only that code for it exists |

**The role can be a machine, and usually should not be.** *As a firewall I want to drop the packet*
is legal. It is also a sign you have stopped asking who is being helped — this is technology built
for people, not for its own sake, and a flow whose every actor is a component has quietly become an
architecture diagram. Ask who is worse off if the step never happens. If the answer is a component,
look one level out for the person behind it.

### The three things that are not the story

All three read as diligence, and all three are the usual first-chapter failure:

1. **The solution.** *As a customer I want my basket held in Redis with a 30-minute TTL.* That is an
   implementation choice. The story is what the customer wants; how you do it is the design, and the
   design belongs where it can be argued with and replaced without touching the story.
2. **The incident.** *On 12 March a duplicate charge occurred because the retry handler…* is
   history. Put it in the commit message, which is version-anchored and stays true after the state
   it describes has moved on. A story that narrates an incident has to be rewritten every time the
   incident recedes, and nobody rewrites it, so it reads as current forever.
3. **The status.** *…(done, verified in staging)* is an authored verdict. A chapter never carries
   status. What is proven is derived from a run, and a `Status:` line is true because somebody typed
   it — which is the failure this whole method exists to remove.

The test is mechanical: **if deleting the sentence would change what the system must do, it belongs
in the chapter. If it would only change what somebody knows about the past, it belongs in a commit
message.**

---

## 2. The hierarchy, and why you cannot get the altitude wrong

**A flow can turn out to be a step inside a larger flow, and that costs you nothing.** It is the
normal case. Interview a business and they will tell you where they think their process starts;
half-way through you discover it begins two departments earlier. The flow you drew does not get
thrown away — it acquires a parent, and becomes one node in it.

So a step that is itself a process gets its own file, and the file name carries the drill-down:

| File | ids inside it |
|---|---|
| `chapter-01-ordering.md` | `ch1-1`, `ch1-2`, … |
| `chapter-01.3-charging.md` | `ch1-3-1`, `ch1-3-2`, … |

`chapter-01.3-charging.md` would be the drill-down of node `ch1-3`. Every id inside it is prefixed
`ch1-3`, and in the parent that node is drawn as a **sub-flow** — `[[…]]` `:::subroutine` — so a
reader knows to follow it.

*(Illustrative. The [worked example](example/) has no drill-down: it fits on a page, which is the
whole test. A node drawn as a plain action is a node that did not need one.)*

**A sub-chapter carries all the same sections.** It is a flow like any other; nothing about it is
abbreviated.

### When to split, and when to fold

One rule, and it is a legibility rule: **a flow should print legibly on one sheet of paper.**

- **Too dense to read?** A step is hiding a process. Give it its own file.
- **Too sparse to be worth its own page?** Fold it into its parent.

It applies to the **expansion** as well as the drawing, and that half catches more. A node whose
story and reasoning run past a page is a node hiding a flow — its steps had nowhere to be, so they
became sentences. If one of your nodes is turning into an essay, you have found a sub-process, not a
badly-written story.

### How big is too big, in numbers

**This is a working heuristic, not a rule the gate holds you to:**

| Nodes | What it usually means |
|---|---|
| 1–3 | too thin to be its own flow — fold it into its parent |
| **4–9** | the ordinary case |
| 10–14 | look hard for one step that is really a process |
| 15+ | there is a sub-flow in there, and probably two |

Applied to the **drawing**. The expansion of a ten-node chapter runs to several pages and that is
normal — what the rule asks of the expansion is that no *single node* needs more than about a page,
not that the chapter fits on one.

Treat all of it as a prompt to look rather than a threshold to obey. A ten-step process that genuinely
has ten steps is a ten-node chapter, and splitting it to hit a number would be the tool choosing the
shape of somebody's business.

### Where the hierarchy stops

**Downward**, it stops when the business stops saying *"oh, I forgot to tell you about…"*

**Upward**, it stops somewhere different in kind: when the steps stop being things a person does and
become **quantities to tune** toward a goal. A flow made mostly of parameters rather than stories is
at the ceiling. That is a thing you notice rather than decide.

---

## 3. Draw the flow first

Write the diagram before any prose. It is the cheapest part to change and it finds the most, because
a flow will not let you leave a step out — a box has to connect to something.

```mermaid
flowchart TD
    START([START · somebody with a basket and a card]):::terminal
    TAKE[ch1-1 · take the order]:::process
    STOCK{ch1-2 · is every line actually available?}:::question
    SHORT[/REFUSED · said before the card is charged/]:::bad
    CHARGE[ch1-3 · charge once]:::process
    TELL[ch1-4 · tell the customer]:::process
    DONE([END · an order the shop can act on]):::good

    START --> TAKE --> STOCK
    STOCK -->|no| SHORT
    STOCK -->|yes| CHARGE --> TELL --> DONE
```

**What the gate checks:**

- **Steps and decisions carry ids; terminals and legend nodes do not.** An id in the diagram must
  have a `###` block, and a block must have an id in the diagram — the gate reports either alone.
  `START`, `END`, a refusal, and every node inside the legend are unidentified, which is what keeps
  them out of that check.
- **The flow has a start and an end.** If every node is pointed at by another, nothing says where it
  begins. Two ends are fine, and so is a cycle.
- **Every class a node names is defined by a `classDef`** in the same chapter. Use one that is not
  and the node renders unstyled, so the gate names it rather than letting the mistake be invisible.

**What is advice, and worth taking:**

- **Shape carries the role** — rectangle acts, diamond asks, stadium terminates.
- **A refusal is a real ending.** *The order is short, so nothing is charged* is an outcome the
  system produces on purpose. Flows that draw only the happy path ship with unhandled failures.
- **Colour is never the only encoding** (see below).

**The drawing is what finds the defects.** A defect can sit undisturbed for as long as it is prose
and become obvious the moment it has to be a box with edges — an activity happening twice under two
names, for instance, which is how a step gets done twice or not at all.

### The shapes, and how to draw the ones that are not boxes

Mermaid `flowchart`, and seven roles. Copy this block into your first chapter and you have the whole
dialect:

| Role | Mermaid | What it is |
|---|---|---|
| start / end | `([…])` `:::terminal` | where the flow begins, and where it finishes |
| action | `[…]` `:::process` | a step somebody performs |
| decision | `{…}` `:::question` | a question with named arms |
| sub-flow | `[[…]]` `:::subroutine` | a step that drills down into its own chapter |
| reached | `([…])` `:::good` | a successful ending |
| refused | `[/…/]` `:::bad` | an ending that is a refusal, and is on purpose |
| parameter | `>"…"]` `:::parameter` | a value still to discover, hanging off the step it tunes |

Seven shapes, and the set is closed. Six of them are steps of the flow. The seventh hangs off one:

**A parameter may be drawn, and an unknown or a decision never is.** A parameter is a quantity the
step needs a number for, so showing it beside that step is how a reader sees what is still being
tuned. What is undecided and what is imposed carry ids under the node they affect (§5) instead —
drawing them turns a flow into a noticeboard.

```mermaid
flowchart TD
    STOCK{<b>ch1-2</b> · is every line<br/>actually available?}:::question
    CHARGE[<b>ch1-3</b> · charge once]:::process

    P1>"<b>ch1-P1</b> how long a reservation<br/>is held"]:::parameter
    STOCK -.tuned by.-> P1

    classDef question fill:#fdf3d8,stroke:#b8860b,color:#0b0b0b;
    classDef process fill:#e9eef5,stroke:#2a78d6,color:#0b0b0b;
    classDef parameter fill:#f4f2ee,stroke:#8a6212,color:#0b0b0b,stroke-dasharray:2 2;
```

**Quote a parameter's label — `P1>"…"]`, with the quotes.** This is the one shape where that is
not optional. A parameter is not a step, so it gets no `###` block; unquoted, its id reads as a
node the diagram draws, and the gate then asks for the block that is never coming. The quotes are
what keep it out of that check, exactly as a legend node's lack of an id keeps the legend out.

**Everything else that is undecided or imposed stays out of the picture**, under the node it
affects (§5), where a reader meets it beside the step rather than in the margin of a drawing.

**Colour is never the only encoding**, and this dialect needs the help: *start / end* and *reached*
are both `([…])`, so in greyscale they are the same box. The text is what separates them — shout
`START`, `END` and `REFUSED` in the label, as the example does. A reviewer may be colour-blind and a
printed page is always grey.

**Quote any label that contains a `"`, `(`, `[` or `{`.** One of those inside an unquoted label
makes Mermaid read the start of another shape, the parse dies, and it takes the **whole diagram**
with it — nothing renders, and every gate that reads the markdown around the fence still passes.
The rule is about what is *inside* a label: `LD{question}` is fine because the braces are the
shape's own, and `subgraph LEGEND["…"]` is fine because it is already quoted. A label reading
`ch1-2 · check the price (before tax)` is not.

**Ship a legend, and the `classDef` lines under it.** Both go inside the same mermaid fence as your
flow. The legend is a `subgraph` holding one sample node per role; its nodes carry short names of
their own — `LT`, `LA`, `LD` — and **no ids**, which keeps them out of the node-block check, and they
connect to nothing, which the start-and-end check does not mind. The `classDef` lines are identical
in every chapter, and a class you use without defining is a fault the gate will name.

This is the whole block, drawn and then given as source. Paste it into your chapter and you have the
dialect:

```mermaid
flowchart TD
    subgraph LEGEND["legend — shape carries the role"]
        direction LR
        LT([START / END — named in caps, so it reads in greyscale]):::terminal
        LA[action]:::process
        LS[[sub-flow — drills down]]:::subroutine
        LD{question}:::question
        LG([reached]):::good
        LB[/REFUSED — a different shape, so it reads in greyscale/]:::bad
        LP>parameter — a value to discover]:::parameter
    end

    classDef terminal fill:#eef0ee,stroke:#52514e,color:#0b0b0b;
    classDef process fill:#e9eef5,stroke:#2a78d6,color:#0b0b0b;
    classDef question fill:#fdf3d8,stroke:#b8860b,color:#0b0b0b;
    classDef subroutine fill:#e9eef5,stroke:#2a78d6,color:#0b0b0b;
    classDef good fill:#e2f2e2,stroke:#0ca30c,color:#0b0b0b;
    classDef bad fill:#f7e4e4,stroke:#b02a2a,color:#0b0b0b;
    classDef parameter fill:#f4f2ee,stroke:#8a6212,color:#0b0b0b,stroke-dasharray:2 2;
```

**Draw a sub-flow only once the chapter it drills into exists.** `[[…]]` `:::subroutine` is a
promise the gate collects: a node drawn as a sub-flow with no chapter expanding it is reported as
`is drawn as a sub-flow and no chapter expands it`. While `ch1-3` is still one step, draw it as an
ordinary action; redraw it as a sub-flow in the same edit that creates
`chapter-01.3-charging.md`.

In the parent, a sub-flow node keeps an ordinary `###` block with its Information table stated at
the parent's altitude — what the whole sub-process takes and leaves, not what its steps do. The two
sides are held against each other: the parent may not claim to leave with what no step of the child
produces, may not take what no step of the child consumes, and must take what the child needs and
neither makes for itself nor gets from outside any step. Those are matched on the Description cell,
by the rule in §4, so the two files have to spell a thing the same way.

**Everything in the child is prefixed by the parent's node id**, and nothing about the child is
abbreviated — same sections, same legend, same stamp. Written out, because a sub-chapter is the one
shape the [worked example](example/) does not carry:

| in the parent | in the child `chapter-01.3-charging.md` |
|---|---|
| node `ch1-3`, drawn `[[…]]` `:::subroutine` | its steps are `ch1-3-1`, `ch1-3-2`, … |
| — | an Information row is `ch1-3-1-inf1` — node id, then kind, then number |
| — | a requirement is `ch1-3-1-ur1`, an unknown `ch1-3-1-u1` |
| — | a parameter is `ch1-3-P1` and a decision `ch1-3-D1` — one series per chapter, as anywhere |
| its `###` block says what the whole sub-process takes and leaves | its entry rows say `parent` in Provenance |

The child's H1 names the process from a person's side like any other chapter, and carries the
drill-down number: `# Chapter 1.3 — the card is charged exactly once`. Nothing checks that wording,
and a title that disagrees with the parent's node text is a thing only a reader catches.

**Node labels may carry markup, and usually should.** The snippets on this page are written plainly
so the shape is visible, but real labels get long: `<b>ch1-1</b>` sets the id off from the text and
`<br/>` wraps a label that would otherwise stretch the diagram into one very wide row. The
[worked example](example/spec/diagrams/chapter-01-ordering.md) does both. Nothing is checked here —
it is the legibility rule again, applied to the drawing.

---

## 4. `## Nodes` — the story, and the information it moves

One `###` block per node. The node carries its story, then a table of what it takes and leaves:

    ### ch1-2 · is every line actually available?

    > **As a customer I want to be told a line is short before my card is touched, so that I am not
    > refunding money I should never have paid.**

    #### Information

    | Information | IO | Description | Required | Provenance |
    |---|---|---|---|---|
    | ch1-2-inf1 | In | `order` | yes | ch1-1 |
    | ch1-2-inf2 | Out | `reservation` | optional | derived |
    | ch1-2-inf3 | Out | `refusal` | optional | derived |

**The information lives with the step that moves it, and nowhere else.** A reader holding one node
should not have to hold a diagram, a chapter-level table and a glossary in their head to answer
*where does this arrive from*. So the answer sits in the row that raises the question.

**Every row carries an id**, because a constraint on one piece of information is a thing a room has
to be able to point at by name.

**`IO`** is `In` or `Out`. In is what the step needs to begin; Out is what it leaves behind.

**`Description`** names the information. Backtick an element name where the corpus has one —
`order.reference` means one thing everywhere — and write plain words where it does not: *the team's
own backlog* is a real input that no step produces and no corpus defines.

**This cell is what makes two rows the same thing, and it is matched exactly.** A row carrying
backticks names what is inside them; a row with none names its whole description. So `` `order` ``
in one step and `` `order` `` in another are one piece of information, and `` `order` `` against
*the customer's order* are two — the chain will report the second as arriving from nowhere, and a
sub-flow's two halves as disagreeing about what crosses between them. A dotted name is the one
exception: a step producing `` `order` `` satisfies a step taking `` `order.reference` ``, because
the part comes with the whole.

Pick a spelling for each thing once and use it everywhere, including across chapters. That is the
whole of the convention, and it is the fact every derived check rests on.

**`Required`** says whether the person must have it, which is a different question from where it
comes from. **An arm of a question is `optional` on the way out and may be `yes` on the way in**:
`ch1-2` leaves with a `reservation` *or* a `refusal`, so each is `optional` there, and the step down
the yes-arm takes the reservation as `yes` because that arm does not run without one. The two
columns are answering about different things — one about the step that made it, one about the step
that needs it.

Two values: **`yes`** and **`optional`**. `yes` is the only one that means *this step does not run
without it*, and it is the only one the chain and the provenance checks hold you to — anything else
is read as *can proceed without*, so a row a step genuinely needs must say `yes` exactly. A backlog is required and has no producer; a board has a producer and is not required,
because on a first run no run has written one.

**`Provenance`** is the column the rest of the table exists to carry, and it is a closed set:

| it says | it means | legal on |
|---|---|---|
| a step's id, like `ch1-1` | that step, in this flow, produced it | `In` |
| `parent` | the flow that hands this one its entry — the chapter drilling into it | `In` |
| `authored` | somebody wrote it down; nothing produces it | both |
| `observed` | read off a run, or the world as it stands | both |
| `generated` | made by a tool, and not recomputable | both |
| `derived` | computed by this step from what it took in | `Out` |

Read the column as the answer to *if this were lost, could it be got back* — ask its author, run it
again, recompute it, or it is gone.

**The last column is checked against the flow, not just against the list.** Name a step and that
step must actually have an `Out` row for the same thing; where the row is `Required: yes`, the
drawing must reach this node from that one. A row saying `ch1-1` for something `ch1-1` never
produces is the habit the column exists to catch, and it survives every other gate.

**Types, lengths, keys and nullability are not here.** A spec is read by the people who own the
work, and a chapter that mixes their language with storage detail stops being theirs. Those belong
in a document behind the node, for whoever is building against it.

## 5. The requirements, and what is undecided

Under the Information table, four headings, always in this order and always present even when empty:

    #### User Requirements
      * ch1-2-ur1 - a short line is said before the card is touched, and the refusal names the line

    #### System Requirements
      * ch1-2-sr1 - the reservation is released whichever way the charge goes

    #### Non-Functional Requirements
      * ch1-2-nfr1 - refusing an order that could have been filled loses a sale; charging for one
        that cannot takes money for nothing

    #### Unknowns
      * ch1-2-u1 - how long a reservation is held is not measured

**A bullet is `  * <id> - <what it requires>`**, with a hyphen between the id and the text. Not a
colon, not an em dash: the separator is what the parser reads, and a bullet written another way
used to parse as nothing at all — so the requirement was held to no check, on a line that looks
exactly right. The gate names one now rather than passing over it.

**A constraint is a requirement with an id, on the step it constrains.** There is no chapter-level
list of them — that would move a constraint away from the thing it constrains.

**Split by kind**, because the three are argued with by different readers: what the person needs,
what the system must do, and what holds whatever the design.

**If the story is complete and the requirements are complete, there is no prose left to write.** A
paragraph inside a node is a requirement that has not been given an id yet.

### Everything a node block holds, in order

    ### ch1-2 · <the step, named as the flow names it>

    > **As a <role> I want <something> so that <goal>.**       <- the story

    #### Information                                           <- the five-column table

    | Information | IO | Description | Required | Provenance |
    |---|---|---|---|---|
    | ch1-2-inf1 | In | `order` | yes | ch1-1 |

    #### User Requirements                                     <- the three kinds of
    #### System Requirements                                      requirement, always
    #### Non-Functional Requirements                              in this order
    #### Unknowns                                              <- last

    **Parameter `ch1-P1` — …**   <- parameters and decisions, last of all
    **Decision `ch1-D1` — …**

**The five `####` headings are one set in one order.** State any of them and you owe all five, in
exactly this sequence; the gate names a node that drops one, adds one, or runs two together. An
empty heading is how a node says *none of these yet*, and it is simply the heading with nothing
under it:

    #### Non-Functional Requirements
      * ch1-4-nfr1 - a confirmation carrying no handle is a courtesy rather than a record

    #### Unknowns

    ---

That is the normal state of a chapter somebody is still writing, and the [worked
example](example/) carries three of them.

**Parameters and decisions live at the foot of the node they constrain.** There is no
`## Parameters` section and no `## Decisions` section — adding one fails the section-set check, and
the fault names the wrong set without telling you where the content should have gone. A parameter
or a decision belongs to the step it constrains, so it sits with that step.

There is one other place, and only one, for the case where a constraint is genuinely not any single
step's:

**A constraint on the whole flow goes between the diagram and `## Nodes`**, in the same bold form:

    ```mermaid … ```

    **Decision `ch1-D1` — the processor's reconciliation window closes at 02:00.** …

    ## Nodes

Some constraints genuinely are not one step's — a regulatory clock that binds the whole process is
not the property of whichever node happens to start it, and hanging it on one node to satisfy the
format is bending the model to fit the tool. Flow-level and node-level decisions share one number series
per chapter.

### The four kinds of subject

**A subject is anything that carries an id**, and there are four kinds. Three of them hang off the
node they affect. The discriminators are worth learning once:

| Kind | Id | Known? | Has a model? | Waiting on |
|---|---|---|---|---|
| **Story** | `ch1-2` | the want is known | — | proof it is done |
| **Open unknown** | `ch1-2-u1` | the question is; the answer is not | no | a **decision** |
| **Parameter** | `ch1-P1` | it exists; the value does not | **yes** | a **discovery** |
| **Decision** | `ch1-D1` | already made; its influences may be external | no | its consequence observed |

**An unknown is numbered under its node and the other two under the chapter**, and the shapes are
what make that read: an unknown is a bullet in a list belonging to one step, so it is `ch1-2-u1`.
A parameter and a decision are run-in paragraphs that may hang off a node or off the whole flow,
so they share one series per chapter — `ch1-P1`, `ch1-D1` — and a chapter's third decision is
`ch1-D3` wherever in the file it is written.

**Unknown or parameter?** Both are not-knowing. An unknown is settled by *deciding*; a parameter is
settled by *measuring*, and what makes it a parameter is that you can write the **model** today — a
statement of what would confirm the value. *How long is a reservation held* has a model (the
distribution of reservation-to-charge times bounds it from below; stock held-and-abandoned bounds it
from above), so it is `ch1-P1`. *What should happen to a basket abandoned mid-charge* has no model,
only a choice, so it is `ch1-2-u1`, under the node it affects.

A parameter that nothing has measured shows on the board as **`unvalidated`** — the honest word for a
constant nobody has tested. **That word is derived and you never type it into a chapter.** Write the
model; whether it has been run is a fact about runs, and a parameter carrying its own status in the
prose would be the authored verdict this method exists to remove, wearing a different word.

**What is a decision?** A **choice already made**, often because of an external imposition that restricts how the process can work, rather than
something it enables, which the flow has to account for:

    **Decision `ch1-D1` — the processor's reconciliation window closes at 02:00.** External, known, and
    restricting: a charge submitted near it may settle on either side of the boundary, so nothing
    here may assume same-day settlement. It is not this shop's to negotiate.

A plain bold run-in paragraph, never a blockquote — the blockquote is reserved for a story, which is
how a reader tells the two apart at a glance. Parameters take the same form.

**The id sits inside the first bold run of the line**, before any other emphasis. That is what
separates *declaring* a decision from *mentioning* one: a node whose argument cites `ch3-U1`, an
unknown another chapter owns, is pointing at somebody else's subject and is not claiming to own it.
Citing across chapters is ordinary and nothing is checked about it.

It gets an id even though nothing is undecided about it, and the reason is different from every
other id here: **so that a room full of people can point at the same thing.** A second reason shows
up as soon as you write two — constraints in tension become visible. In prose, two constraints fifty
words apart read as one continuous line of reasoning.

---

## 6. Unknowns, and why there is no backlog

An unknown is a bullet under the node it affects, in that node's `#### Unknowns`:

      * ch1-2-u1 - how long a reservation is held is not measured; too short and a slow card
        releases stock somebody has been promised, too long and a browsing customer holds stock
        nobody can sell

**This is what replaces a backlog.** An unknown is a question anchored to a step; an **unproven
subject is the work item**. Anything anchored to nothing is not undefined — it is *uncommitted*, and
it should be dropped rather than filed. A side list of open questions is how a backlog regrows under
a new name, and it goes stale exactly the same way.

Write what would settle it. *We should look into caching* is not an unknown. *Whether the
processor's reconciliation window closes before ours does — needs their documentation read* is one,
because a reader knows what to go and do.

**A boundary is not an unknown.** Something the work deliberately does not do is a requirement. An
unknown says nobody has decided; unknowns that are really boundaries accumulate as false debt.

---

## 7. `## Glossary` — the words this flow uses differently

Last section, and it is not a dictionary of every noun. It is for words that mean something
**specific to this process**, and likely mean something else in a neighbouring one or in ordinary
English:

    | Term | Meaning |
    |---|---|
    | Order | A basket the shop has accepted responsibility for. It has a reference from the moment it exists |
    | Short | A line the shop cannot fill in the quantity asked for. Not the same as *out of stock*, which is a property of the item rather than of this order |

*Order* earns a row because the moment a basket becomes one is exactly what this chapter is about.
*Short* earns one because a neighbouring flow uses it to mean something else.

---

## 8. The whole file, in order

Two `##` sections, and the gate enforces both the set and the order:

    # Chapter 1 — <the process, named from a person's side>      <- H1 title
    **Last updated** 2026-09-15 v1                               <- the stamp
    > **As a <role> I want <something> so that <goal>.**          <- the flow's story
    <a paragraph or two of context, optional>
    ```mermaid … ```                                             <- the flow
    **Decision `ch1-D1` — …**                                    <- flow-level only, optional
    ## Nodes
    ## Glossary

The title, stamp, story and diagram come first, in that order, above the sections. A reader looking
for the glossary should never have to hunt for it.

**The stamp is checked, and the version matters as much as the date.** `**Last updated**
YYYY-MM-DD vN`, immediately under the title. A chapter revised between a morning session and an
afternoon one is two documents on the same day, and a room needs to know which is on the table, so
**every change is a version** — a corrected typo included, because a misspelling in a requirement
stops a session while people work out whether it is a mistake or a distinction. `derived` or
`authored` may follow the version and is optional.

**`## Working notes` is the only other `##` heading a chapter may carry**, and it goes last. It
says of itself that it is not part of the chapter, which is what makes ignoring it honest rather
than lenient. Every other heading fails the section check: there is no `## Elements`, no
`## Parameters`, no `## Decisions`, and no `## Input → process → output`.

**Small things that are part of the format, so you do not have to guess them:**

- The `###` node headings read `### ch1-2 · take the order`. The id comes first; the `·` is
  conventional and a `—` or `-` reads the same.
- `---` rules between node blocks are decoration. Use them or do not.
- The Information table's header row is the five column names, spelled as §4 spells them.
- **The argument goes in a requirement, not in a loose paragraph.** Why the step is the way it is —
  usually which failure is the more expensive one — is where most of a chapter's value ends up, and
  it belongs in a Non-Functional Requirement, carrying an id a room can point at. The example's
  `ch1-2-nfr1` is exactly that. A bare paragraph inside a node is a requirement nobody has given an
  id to yet.
- **Every id series is padded to the width its own largest member needs.** Nine unknowns are
  `u1`..`u9`; a tenth takes the series to `u01`..`u10` and every citation with it. A series with
  mixed widths does not sort, and the gate says so.
- A **cycle is legal**. Rework loops, retries and *go back and amend* are real shapes of real
  processes, and drawing a back-edge does not trip the start-and-end check. Model the process you
  actually have.
- An empty section is legal. A chapter with no open unknowns still carries the heading.

---

## 9. Run the gate

    $ goldspec spec
    goldspec: conventions from goldspec.toml
    goldspec: ids namespaced 'ch', flows in diagrams/chapter-*.md
    goldspec: 6 subject(s) declared in spec/
    goldspec: 0 cited id(s) read from .
    goldspec: 1 process flow(s) render
    goldspec: 1 of 1 chapter(s) in the node format, 4 node(s)
    goldspec: chapter-01-ordering.md: 2 observation(s) — an element nothing downstream takes …
    goldspec:   chapter-01-ordering.md#ch1-2 leaves with refusal, reservation, which nothing …
    goldspec:   chapter-01-ordering.md#ch1-4 leaves with confirmation, which nothing …
    0 fault(s) in spec

Exit `0` clean, `1` with faults, `2` when the run could not start — an unreadable `goldspec.toml`,
or a spec directory that is not there. A `2` writes nothing to stdout, so a redirected report is
empty rather than clean; the reason is on stderr.

**Every `goldspec:` line is on stderr, and the faults and the count are on stdout.** So
`goldspec spec > report.txt` gives you a file holding the faults and their count and nothing else,
and `2>&1` is how you keep the rest. An exit `2` writes to neither — check the code, not the file. That split is deliberate — a report that carried its own context
would be stating something its source does not — and it is worth knowing, because the lines you
most want when a fault surprises you are the ones a redirect throws away.

**Read the conventions line first.** Every message the gate emits is phrased as a verdict on your
spec, and *being handed the wrong strings* is the one cause it cannot phrase. A project that wrote
no file — which is the right thing for a project on the defaults — sees the other spelling of it:

    goldspec: no goldspec.toml found — checking against the defaults

Those two lines are how you tell *I took the defaults* from *my file is somewhere the tool does not
look*, and they are the only way to tell, because the two are the same thing to every other check.

**Read the counts second.** A gate is only worth its output if it read something, and `0 fault(s)`
looks identical whether it parsed four nodes or found no chapters at all. If those numbers are not
the size of what you wrote, the run did not judge what you think it judged.

**`subject(s)` counts what a test can cite** — the nodes, the parameters and the decisions. Your
requirements, your unknowns written as bullets, and your Information rows all carry ids so a room
can point at them, and none of them is in that number. `node(s)` is the one to check your chapter
against.

### What a refusal looks like

Faults name the file, the id where one applies, and what to do:

    chapter-01-ordering.md#ch1-2 needs coupon, which no earlier step produces — either
      a step is missing an output, or a step is missing
    chapter-01-ordering.md#ch1-5 is drawn in the flow and has no node block — the
      diagram is the authority and the expansion is what a reader follows it into
    chapter-01-ordering.md: sections are ['Glossary', 'Nodes'], not ['Nodes',
      'Glossary'] — a reader looking for the glossary should never have to hunt for it
    chapter-01-ordering.md#ch1-2 takes coupon from ch1-1, which does not produce it

The last one catches a habit rather than a typo: a row names where its information came from, and a
row naming a step that never produced the thing reads exactly as authoritative as one that did.

### Everything the gate holds you to, in one table

Expect a round or two on your first chapter. This is the whole list; anything that fires and is not
here is a defect in this page.

| It reads | and refuses |
|---|---|
| the `##` headings | anything but `## Nodes` then `## Glossary`, plus an optional trailing `## Working notes` |
| the line under the title | a missing or malformed `**Last updated** YYYY-MM-DD vN` |
| node ids | an id not namespaced to its own chapter; a node expanded twice; a node that states no Information at all |
| the drawing against the blocks | an id that appears in the diagram with no `###` block, and a `###` block whose id appears nowhere in the diagram. Two things it does not do: it checks the id's *presence* in the fence, not that an arrow reaches it, so a node declared and connected to nothing passes; and it only looks at ids namespaced to this chapter, so a foreign id drawn and never expanded is invisible to it |
| the drawing's shape | a flow with no start, or none with an end — a start has a way out and nothing pointing at it |
| node labels | a bare `"`, `(`, `[` or `{` in an unquoted label, which stops the **whole** diagram rendering |
| `classDef` | a class a node names that no `classDef` in the chapter defines, and a `classDef` setting no `color:` |
| the `####` headings | a node that states some of the five and not all five, or states them out of order |
| requirement ids | a requirement named for a step other than the one it sits under; an id stated twice; and a bullet opening with a requirement-shaped id that nothing can read |
| the chain | an `In` that no earlier step produces and no provenance accounts for |
| provenance | an empty cell; a value outside the closed set; a step named that does not produce the thing, or that the flow does not reach this node from |
| id numbering | a series padded to mixed widths, so a plain sort will not order it |
| the prose | a chapter colouring its diagram by what is built, or carrying one of a short list of build-status phrases — *unbuilt*, *nothing implements*, *not yet built* and their neighbours |
| the prose, narrowly | a **click link** to a test file, a trace table keyed by test name, or a `Spec source:` line — the three shapes of a chapter naming its own proof. Prose that names a test in a sentence is not caught |
| the prose, narrowly | a sentence carrying both a measurement and a phrase naming whose run produced it (*measured on a customer's suite*) |
| node titles | a step that produces nothing and reads as a prohibition — that is a rule the process obeys, not an act |
| row descriptions | a row that names a step this chapter already has as a node — it may be a layer below the node it sits in |
| the corpus, not just this file | one id declared twice, whether in one chapter or across two — usually a drill-down whose prefix is wrong, colliding with its own parent |
| the spec as a whole | a spec that declares no subjects at all, and a `## Nodes` section that declares no nodes. Neither is a state anybody intends, so neither is read as a pass |
| a decision or parameter's id | one not namespaced to its chapter, wherever it is stated, and one stated twice |
| a citation | an id cited by a test that no chapter in this spec declares |
| sub-flows | a node drawn `[[…]]` that no chapter expands, and a parent and child disagreeing about what crosses between them |

**`parent` is not checked against the corpus.** Nothing confirms that a chapter using it is one
something else actually drills into, and nothing can: with `siblings`, the flow that hands this one
its entry may live in a repository this run cannot see. So it is the one provenance value that
excuses an input from the chain on your word — use it at a sub-flow's entry and nowhere else.

### What it does not check, and you should not assume it does

A reviewer who believes a machine already looked stops looking, so this is the more expensive half
to get wrong:

- **A status somebody typed.** `Status: accepted`, *(done, verified in staging)* — §1 calls this the
  failure the whole method exists to remove and **nothing refuses it**. What fires is a short list
  of *build*-status phrases, and a `classDef` named for whether a thing is built.
- **A story.** A node with no blockquote, or with its story written as a plain paragraph, passes.
  Every page here says a node is a user story; no check holds you to one.
- **What a requirement says.** An argument inside one, a benefit clause naming the mechanism, a
  role that is not a role: all a reader's, all listed as such in
  [reviewing a chapter](reviewing-a-chapter.md).
- **A requirement's kind against the heading it sits under.** `ch1-1-sr9` under
  `#### User Requirements` passes: the kind letter in the id and the heading above it are never
  compared.
- **Where the stamp sits.** Its shape is checked and its position is not, so a stamp at the foot of
  the file passes. What may follow the version is not a closed set either, whatever it looks like.
- **Altitude**, which is why a word-by-word read has not been retired.

**A fault may cite an id of goldspec's own spec** — `` (`spe6`) `` on the stamp, `(alt4)` on the
start-and-end check. Those name the subject inside this methodology's own chapters that the check
comes from. They are a pointer for whoever maintains the gate; nothing about your chapter depends
on being able to resolve one, and you can read straight past them.

**One thing is counted and never fails a run**: information a node leaves with that nothing
downstream takes. Every flow ends by producing something for a person, so that is a flow's product
about as often as it is waste — the run says what it saw and you decide.

---

## 10. Your conventions, in one file

Ids namespaced `REQ` or `sh`, flows in a directory named to suit you: all yours. Say so in a
`goldspec.toml`, **inside your spec directory or beside it** — `spec/goldspec.toml` or
`goldspec.toml` next to `spec/`, those two and no other:

```toml
[conventions]
namespace = "ord"              # ids read ord1-1, ord1-2
flow_dir  = "flows"            # where the process flows live, relative to the spec
flow_glob = "story-*.md"       # how a flow file is named
siblings  = ["../shared/spec"] # more of this corpus, read for what it defines, never checked
```

Every key is optional, and the defaults are our habits: `namespace = "ch"`, `flow_dir = "diagrams"`,
`flow_glob = "chapter-*.md"`, no siblings. A
project that took all of them writes no file at all.

**Write only what differs.** A key restating a default is a copy, and it will not rot at the same
rate as the original — if a default ever moves, your file silently disagrees with it. The
[example's](example/goldspec.toml) whole conventions table is one line.

**The file name decides the id prefix, and it is checked.** The namespace, then the number the
file name carries, and a drill-down keeps its parent's number with it:

| `flow_glob` | `namespace` | the file | the prefix every id in it carries |
|---|---|---|---|
| `chapter-*.md` | `ch` | `chapter-01-ordering.md` | `ch1` |
| `chapter-*.md` | `ch` | `chapter-01.3-charging.md` | `ch1-3` |
| `flow-*.md` | `req` | `flow-01-repairs.md` | `req1` |
| `story-*.md` | `ord` | `story-07.2-refunds.md` | `ord7-2` |

Get the number wrong and every id in the file is reported as not namespaced to its chapter.

What a step moves is stated in the step's own rows, with a provenance per row, so there is no
chapter-level table to hold to separate rules and no flag deciding whether it is held.

**The command reads this file and so does the library**, so a project running both cannot end up with
two gates over one spec that disagree.

Put it **inside the spec directory** if one repository holds more than one spec — a file beside it
is found for every spec directory next to it, which is right for a project with one spec and wrong
for a project with two. A `goldspec.toml` anywhere else, `spec/diagrams/` included, is not read and
nothing reports that: a directory with no file and a project that took every default are the same
thing to the gate. The run's first line is what separates them, which is why it prints on clean
runs too.

**A chapter is held to the shape it is written in**, and nothing has to be declared for that.
Every corpus written before this format exists in the older shape — one
`## Input → process → output` and one `## Data definitions` per chapter — and a chapter in that
shape is counted and never held to the node format's checks. Convert one and it is held to what
the node shape owes, the moment it is converted and not before.

Two limits, stated because they bite during a conversion. An unconverted chapter **declares no
subjects**, so a test citing one is reported as citing something declared nowhere; and a spec in
which **nothing** is converted fails, because the gate finds no subjects at all and refuses that
rather than calling it a pass. Convert the chapters your tests cite first.

---

## 11. What a spec does not hold

| Not this | Why | Where it goes |
|---|---|---|
| Status, percent complete, `Status: accepted` | typed, therefore true; the superseded ones read exactly like the current ones | derived from a run |
| A backlog or task list | grows endlessly, stale the moment it is written | an unproven subject *is* the work item |
| What went wrong on a given day | history, and it stops being true | the commit message |
| A second copy of a decision | two homes for one fact, drifting from the moment either moves | one subject, cited by id |
| A mapping table of old ids to new | an id resolving only through a lookup is a second name for something that already has one | rewrite the citations |

**A spec states the plan, not the state.** A subject says what the design is; whether you have got
there is what a run reports, and it is never folded back into the claim. An unproven subject is not
a failure of the spec — it is the work, visible.

---

## Where to go next

- **[The worked example](example/)** — the chapter above as a spec directory you can copy and run
  `goldspec` against.
- **[Plumb](https://plumbspec.org/)** — derives whether a story is actually proven by a test run.
  goldspec checks that what you wrote down is coherent; Plumb checks that the code honours it.
  Neither requires the other.
