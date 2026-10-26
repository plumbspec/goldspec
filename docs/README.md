# goldspec documentation

**The gold-spec methodology — how to write a spec in it, and why it is shaped this way.**

| Page | For | What it is |
|---|---|---|
| [Getting started](getting-started.md) | anybody writing their first chapter | one complete chapter walked part by part, with the rules the gate enforces stated where an author looks for them |
| [Writing a process flow](writing-a-process-flow.md) | anybody writing a chapter | how to write one that passes, habit by habit |
| [Reviewing a chapter](reviewing-a-chapter.md) | anybody reading a chapter and deciding whether it is right | the judgements a gate cannot make, and the failures that look like style |
| [The worked example](example/spec/diagrams/chapter-01-ordering.md) | anybody who would rather read a file than a page | the worked chapter from the tutorial and [its drill-down](example/spec/diagrams/chapter-01.3-charging.md), shipped in `docs/example/` as a spec directory you can run `goldspec` against |
| [Cite the spec from a test](getting-started.md#10-cite-the-spec-from-a-test) | anybody wiring tests to the spec | the `proves` and `informs` marks, where the gate looks for them, and what it refuses |
| [Bringing in a document you already have](getting-started.md#13-bringing-in-a-document-you-already-have) | anybody converting an existing document into a chapter | where each part of the old document goes, what is dropped, and what the conversion's commit says |

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
- **A test cites the spec, never the other way round** — `@pytest.mark.proves("ch1-3")` on a test,
  `@Proves("ch1-3")` in Java. The gate checks every cited id is declared.
- **A chapter never carries status.** What is proven is derived from a run. A status somebody typed
  is true because they typed it.
- **An open question is anchored** to the subject it affects. Anything anchored to nothing is not
  undefined, it is uncommitted — drop it. There is no backlog; an unproven subject *is* the work
  item.
- **The conventions are yours.** Ids namespaced `REQ` or `sh`, flows in a directory named to suit
  you: say so in a `goldspec.toml` and the same checks run against your layout.
- **One main flow, and one tree under it.** Name the flow a corpus starts from with `main_flow`;
  every other flow is a drill-down named for the step it is entered from, so the file names alone
  show where each chapter sits.

## Not this, and deliberately

goldspec has many opinions about your workflow, and you opted into every one by installing it.
[Plumb](https://plumbspec.org/) has none — it observes a test run and derives whether a story is
proven, works for any project with any workflow, requires no spec, and does not know this package
exists. Neither requires the other, and the boundary is enforced by a test rather than promised.
