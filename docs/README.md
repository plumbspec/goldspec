# goldspec documentation

**The gold-spec methodology — how to write a spec in it, and why it is shaped this way.**

| Page | For | What it is |
|---|---|---|
| [Getting started](getting-started.md) | anybody writing their first chapter | one complete chapter walked part by part, with the rules the gate enforces stated where an author looks for them |
| [Writing a process flow](writing-a-process-flow.md) | anybody writing a chapter | how to write one that passes, habit by habit |
| [Reviewing a chapter](reviewing-a-chapter.md) | anybody reading a chapter and deciding whether it is right | the judgements a gate cannot make, and the failures that look like style |
| [`example/`](example/) | anybody who would rather read a file than a page | the worked chapter from the tutorial, as a spec directory you can run `goldspec` against |

The example is checked by this project's own suite on every run, so an example that fails when
copied cannot ship.

## The short version

- A spec is **markdown a person reads**. There is no vocabulary to import and no module a runner has
  to collect.
- **One chapter is one process flow**, and it holds **many** user stories — one for every step in
  it. Each is written from a person's side: *as a \<role\> I want \<something\> so that \<goal\>*.
- **A subject is anything with an id** — a node, an open unknown, a parameter, a decision — and it is
  declared where it is written, never in a list beside it. A second list of ids is a second home, and
  it drifts.
- **A chapter never carries status.** What is proven is derived from a run. A status somebody typed
  is true because they typed it.
- **An open question is anchored** to the subject it affects. Anything anchored to nothing is not
  undefined, it is uncommitted — drop it. There is no backlog; an unproven subject *is* the work
  item.
- **The conventions are yours.** Ids namespaced `REQ` or `sh`, flows in a directory named to suit
  you: say so in a `goldspec.toml` and the same checks run against your layout.

## Not this, and deliberately

goldspec has many opinions about your workflow, and you opted into every one by installing it.
[Plumb](https://plumbspec.org/) has none — it observes a test run and derives whether a story is
proven, works for any project with any workflow, requires no spec, and does not know this package
exists. Neither requires the other, and the boundary is enforced by a test rather than promised.
