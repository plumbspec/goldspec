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

Six shapes, and the set is closed. What is undecided, what is measured and what is imposed are
**not** shapes — they carry ids under the node they affect:

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

**Draw the steps and the questions, and nothing else.** What is undecided, what is measured and
what is imposed carry ids under the node they affect (§5), where a reader meets them beside the step
rather than in the margin of a picture.

**Colour is never the only encoding**, and this dialect needs the help: *start / end* and *reached*
are both `([…])`, so in greyscale they are the same box. The text is what separates them — shout
`START`, `END` and `REFUSED` in the label, as the example does. A reviewer may be colour-blind and a
printed page is always grey.

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

**A sub-flow node may point at a chapter you have not written yet.** Nothing requires
`chapter-01.3-charging.md` to exist before you draw `ch1-3` as a sub-flow. Draw the process you have;
the file follows when the node grows past a page. In the parent, a sub-flow node keeps an ordinary
`###` block with In / Held / Out stated at the parent's altitude — what the whole sub-process takes
and leaves, not what its steps do.

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

**`Required`** says whether the person must have it, which is a different question from where it
comes from. A backlog is required and has no producer; a board has a producer and is not required,
because on a first run no run has written one.

**`Provenance`** is the column the rest of the table exists to carry, and it is a closed set:

| it says | it means |
|---|---|
| a step's id, like `ch1-1` | that step, in this flow, produced it |
| `parent` | the chapter this one drills into handed it in |
| `authored` | somebody wrote it down; nothing produces it |
| `observed` | read off a run, or the world as it stands |
| `generated` | made by a tool, and not recomputable |
| `derived` | computed by this step from what it took in |

Read the column as the answer to *if this were lost, could it be got back* — ask its author, run it
again, recompute it, or it is gone.

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

**A constraint is a requirement with an id, on the step it constrains.** There is no chapter-level
list of them — that would move a constraint away from the thing it constrains.

**Split by kind**, because the three are argued with by different readers: what the person needs,
what the system must do, and what holds whatever the design.

**If the story is complete and the requirements are complete, there is no prose left to write.** A
paragraph inside a node is a requirement that has not been given an id yet.

### Everything a node block holds, in order

    ### ch1-2 · <the step, named as the flow names it>

    > **As a <role> I want <something> so that <goal>.**       <- the story

    | | |                                                      <- In / Held / Out
    |---|---|
    | **In** | … |
    | **Held** | … |
    | **Out** | … |

    <one paragraph: why the step is the way it is>             <- the closing argument

    **Parameter `ch1-P1` — …**   <- parameters and decisions, last
    **Decision `ch1-D1` — …**

**Parameters and decisions live at the foot of their node's block, and nowhere else.** There is no
`## Parameters` section and no `## Decisions` section — adding one fails the section-set check, and the
fault names the wrong set without telling you where the content should have gone. A parameter or an
decision belongs to the step it constrains, so it sits with that step.

**A constraint on the whole flow goes between the diagram and `## Elements`**, in the same bold form:

    ```mermaid … ```

    **Decision `ch1-D1` — the processor's reconciliation window closes at 02:00.** …

    ## Elements

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
| **Open unknown** | `ch1-U1` | the question is; the answer is not | no | a **decision** |
| **Parameter** | `ch1-P1` | it exists; the value does not | **yes** | a **discovery** |
| **Decision** | `ch1-D1` | already made; its influences may be external | no | its consequence observed |

**Unknown or parameter?** Both are not-knowing. An unknown is settled by *deciding*; a parameter is
settled by *measuring*, and what makes it a parameter is that you can write the **model** today — a
statement of what would confirm the value. *How long is a reservation held* has a model (the
distribution of reservation-to-charge times bounds it from below; stock held-and-abandoned bounds it
from above), so it is `ch1-P1`. *What should happen to a basket abandoned mid-charge* has no model,
only a choice, so it is `ch1-U1`.

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

Four `##` sections, and the gate enforces both the set and the order:

    # Chapter 1 — <the process, named from a person's side>      <- H1 title
    > **As a <role> I want <something> so that <goal>.**          <- the flow's story
    <a paragraph or two of context, optional>
    ```mermaid … ```                                             <- the flow
    ## Nodes
    ## Glossary

The title, story and diagram come first, in that order, above the sections. A reader looking for the
glossary should never have to hunt for it.

**Small things that are part of the format, so you do not have to guess them:**

- The `###` node headings read `### ch1-2 · take the order`. The id comes first; the `·` is
  conventional and a `—` or `-` reads the same.
- `---` rules between node blocks are decoration. Use them or do not.
- The In / Held / Out table has an **empty header row** — `| | |` then `|---|---|`. It is a
  two-column table whose columns are unlabelled, because the labels are in the rows.
- **A node's closing paragraph is part of the format**, and it is where most of a chapter's value
  ends up: a short argument for why the step is the way it is, usually about which failure is more
  expensive. The story says what somebody wants; this says why it is worth the trouble. Keep it to a
  paragraph — if it runs past that, see the density rule in §2.
- A **cycle is legal**. Rework loops, retries and *go back and amend* are real shapes of real
  processes, and drawing a back-edge does not trip the start-and-end check. Model the process you
  actually have.
- An empty section is legal. A chapter with no open unknowns still carries the heading.

---

## 9. Run the gate

    $ goldspec spec
    goldspec: conventions from goldspec.toml
    goldspec: ids namespaced 'ch', flows in diagrams/chapter-*.md
    0 fault(s) in spec

Exit `0` clean, `1` with faults. Every run names the conventions it judged by — read that line first
when a fault surprises you, because every message the gate emits is phrased as a verdict on your
spec, and *being handed the wrong strings* is the one cause it cannot phrase.

### What a refusal looks like

Faults name the file, the id where one applies, and what to do:

    chapter-01-ordering.md#ch1-2 moves `coupon`, which no element list defines here,
      imports, or resolves in a sibling
    chapter-01-ordering.md#ch1-5 is drawn in the flow and has no node block — the
      diagram is the authority and the expansion is what a reader follows it into
    chapter-01-ordering.md: sections are ['Glossary', 'Nodes'], not ['Nodes',
      'Glossary']
    chapter-01-ordering.md#ch1-2 takes coupon from ch1-1, which does not produce it

The last one catches a habit rather than a typo: a row names where its information came from, because
anything more is a second statement of a fact you do not own.

Expect a few rounds on your first chapter. Every convention the gate enforces is on this page; one
that is not is a defect in this page.

---

## 10. Your conventions, in one file

Ids namespaced `REQ` or `sh`, flows in a directory named to suit you: all yours. Say so in a
`goldspec.toml`, beside your chapters or beside the spec directory:

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

**The file name decides the id prefix, and it is checked.** `chapter-01-ordering.md` under namespace
`ch` gives `ch1`, so every id in it must read `ch1-…`; `chapter-01.3-charging.md` gives `ch1-3`. Get
the number wrong and every id in the file is reported as not namespaced to its chapter.

What a step moves is stated in the step's own rows, with a provenance per row, so there is no
chapter-level table to hold to separate rules and no flag deciding whether it is held.

**The command reads this file and so does the library**, so a project running both cannot end up with
two gates over one spec that disagree.

Put it **beside your chapters** if one repository holds more than one spec — a file at the root is
found for every spec directory beneath it, which is right for a project with one spec and wrong for
a project with two.

**A chapter is held to the shape it is written in**, and nothing has to be declared for that.
Every corpus written before this format exists in the older shape — one
`## Input → process → output` and one `## Data definitions` per chapter — and a chapter in that
shape is read that way and counted rather than failed. Convert one and it is held to what the
node shape owes, the moment it is converted and not before.

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
