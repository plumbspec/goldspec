# goldspec

The **gold-spec methodology** — a process flow whose every step is a user story, carrying the
information it moves, the requirements that hold it and the questions still open, and the gates that
keep all of it honest.

**New here?** [Getting started](docs/getting-started.md) walks one complete chapter part by part and
gets the gate green; [Cite the spec from a test](docs/getting-started.md#10-cite-the-spec-from-a-test)
shows the mark a test carries to say which story it proves. [All the documentation](docs/README.md).
goldspec runs on Python 3.9 or later.

**Already using it?** [CHANGELOG.md](CHANGELOG.md) says what each release changed and whether
taking it asks anything of you.

## This is not plumb, and nothing plumb ships imports it

[`plumb`](https://github.com/plumbspec/plumb) observes a run and derives a board. It works for any
project with any workflow, and requires no spec. **Nothing under its `src/` may import this
package**, and a project adopts a methodology by installing one — never by being handed one with its
tooling.

**The line is about delivery.** The two specs may cite one another; nothing plumb ships may import
this package. The import half is enforced by a test in each repository that reads the other's
shipped modules as source data.

That separation is not a preference. Everything here presumes *conventions*: how a subject is
declared, where flows live, what a chapter looks like. To check that every story is described and
placed on a flow, a tool must decide what a story is and where it lives — which is mandating a
workflow. Opted into, the identical checks are simply the method a project chose.

A declared set handed over as data is a second home for subjects the spec already owns, and it
drifts from the moment either moves.

## The dependency runs one way

`goldspec` reads a project's spec and the test sources that cite it, and imports nothing from
`plumb` — a test in this repository holds it to that. Nothing under
`plumb`'s `src/` may import `goldspec`, and that is enforced rather than promised —
`test_nothing_shipped_imports_the_methodology` in plumb's own suite reads its source as data and
fails on a single import.

## How it is delivered

The gates are **tests**. A project runs them in its own suite, so `plumb` observes a test that ran
and passed, exactly as it observes any other, and never learns the test was a methodology gate. No
new interface was needed for any of this.

Two artifacts ship from the same release, listed in one `SHA256SUMS` and covered by one signature:

| | what it is for |
| --- | --- |
| `goldspec.pyz` | the **command**. Checking a spec by hand, or before anything is wired up. Install it by following the [instructions on the site](https://plumbspec.org/gold/), which check its checksum and signature; it needs no project of yours to be a Python one |
| `goldspec-<version>-py3-none-any.whl` | the **library**. `pip install` it and import `check_spec_directory` into your own test — which is what the paragraph above actually describes |

If you are reading a spec, take the command. If you are holding a spec to its gates on every run,
take the library.

## Your conventions, in one place both forms read

Adopting goldspec means adopting the **shape** — a subject is declared once, where it is written, and
placed in a flow — and never our particular strings. Ids namespaced `REQ` or `sh`, flows in a directory called something
else, chapters named to suit you: all of it is yours, and the gates check it just the same.

Say so in a `goldspec.toml`, **inside your spec directory or beside it** — those two places and no
other, so a file that is being ignored is a file in a place you can see is wrong:

```toml
[conventions]
namespace = "sh"                  # the prefix every subject id carries
flow_dir  = "flows"               # where the process flows live, relative to the spec
flow_glob = "story-*.md"          # how a flow file is named
siblings = ["../other/spec"]      # more of this corpus, read for what it defines, never checked
main_flow = "story-01-orders.md"  # the one flow the corpus starts from; every flow must be reached from it
```

Those five keys are the whole set — shown here with values that differ from the defaults
(`ch`, `diagrams`, `chapter-*.md`, no siblings, no main flow), because a file states only what
differs. A key this version does not read stops the run rather than being ignored. Once
`main_flow` is named, every other flow is a drill-down named for the step it is entered from, and a
flow neither drawn from the main flow nor linked from a flow that is reached fails the gate.

**A chapter is held to the shape it is written in.** Written as a flow, its information lives with
the node that moves it — a `## Nodes` section where each node carries its story and states what it
takes and leaves, each row saying where it came from. Written in the older shape, with one
`## Input → process → output` and one `## Data definitions` per chapter, it is **counted and not
held to the node format's checks**. So a corpus converts a chapter at a time and an unconverted
chapter is not failed for the shape it is in; there is no flag to set, and none to remember to
unset.

Two limits on that, because they are real and a reader should meet them here rather than in a
run. **An unconverted chapter declares no subjects**, so a test citing one is reported as citing
something nobody wrote down, and **a spec in which nothing is converted fails** — the gate finds no
subjects at all, which it refuses rather than calls a pass. Convert the chapters your tests cite
first and the rest follow at their own pace.

Every key is optional and the defaults are our habits, so a project that took them writes no file
at all. **The command reads it and so does the library** — `conventions_for(spec)` is what both
call — because a project that states its conventions twice has two gates over one spec that cannot
see each other, which is the defect this whole method exists to remove.

Two locations, in that order, and deliberately not a search up to the filesystem root: an upward
search finds a file you did not write, in a directory you may not own, and reports its conventions
as yours. Put the file *inside* the spec directory if one repository holds more than one spec — a
file beside it is found for every spec directory next to it, which is right for a project with one
spec and wrong for a project with two.

A file anywhere else is not read and nothing says so, because nothing can: a directory with no
`goldspec.toml` in it and a project that took the defaults are the same thing. The run's first line
is what tells you which happened.

Every run says which conventions it judged by, and where they came from. That line is worth reading
when a fault surprises you: every message this gate emits is phrased as a verdict on your spec, and
the one cause it cannot phrase is having been handed the wrong strings.

