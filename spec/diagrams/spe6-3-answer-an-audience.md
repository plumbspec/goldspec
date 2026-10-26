# spe6-3 · answer an audience

**Last updated** 2026-10-26 v2

What somebody does to answer one of the several audiences a plan has — an executive reading budget
and schedule, whoever asks what is actually in place, whoever asks what a change would cost —
without maintaining a document beside the spec for each of them. Reads what
[spe6-2 · keep the corpus](spe6-2-keep-the-corpus.md) holds, and the run that gives it status.

```mermaid
flowchart TD
    IN([<b>START</b> · a spec, the run that gives it status,<br/>and an audience with a question]):::terminal

    ASKQ{what is the<br/>audience asking?}:::question
    PROJ[<b>spe6-3-1</b> · project the view its audience needs]:::process
    ACTUAL[<b>spe6-3-2</b> · read what is in place as the ideal plus its status]:::process
    IMPACT[<b>spe6-3-3</b> · answer what a change would put in question]:::process

    OVERQ{are there planning facts<br/>the spec cannot prove?}:::question
    JOIN[<b>spe6-3-4</b> · join the planning overlay by subject]:::process
    POLICY[<b>spe6-3-5</b> · report declared policy against derived reality]:::process

    STAMP[<b>spe6-3-6</b> · stamp what it was made from]:::process
    GATE[<b>spe6-3-7</b> · refuse a view that asserts more than its source]:::process

    OUT([<b>END</b> · a document nobody had to maintain,<br/>saying only what its source supports]):::good

    IN --> ASKQ
    ASKQ -->|what is planned| PROJ --> OVERQ
    ASKQ -->|what is actually in place| ACTUAL --> STAMP
    ASKQ -->|what would this change affect| IMPACT --> STAMP
    OVERQ -->|yes| JOIN --> POLICY --> STAMP
    OVERQ -->|no| STAMP
    STAMP --> GATE
    GATE -->|asserts more than its source| PROJ
    GATE -->|within its source| OUT

    classDef terminal fill:#eef0ee,stroke:#52514e,color:#0b0b0b;
    classDef process fill:#e9eef5,stroke:#2a78d6,color:#0b0b0b;
    classDef question fill:#fdf3d8,stroke:#b8860b,color:#0b0b0b;
    classDef good fill:#e2f2e2,stroke:#0ca30c,color:#0b0b0b;
```

## Nodes

### spe6-3-1 · project the view its audience needs

> **As one of a plan's audiences I want my document computed from the spec, so that nobody has to
> remember to update it and nobody has to wonder whether they did.**

#### Information

| Information | IO | Description | Required | Provenance |
|---|---|---|---|---|
| spe6-3-1-inf1 | In | `spec` | yes | authored |
| spe6-3-1-inf2 | In | `run` | yes | observed |
| spe6-3-1-inf3 | Out | `view` | yes | derived |

#### User Requirements
  * spe6-3-1-ur1 - every audience-facing rendering is computed from the spec on demand, never authored
    and never maintained
  * spe6-3-1-ur2 - each audience gets the document it needs rather than one document everybody reads
    past
  * spe6-3-1-ur3 - a view is produced for a request and kept by nobody

#### System Requirements

#### Non-Functional Requirements
  * spe6-3-1-nfr1 - an authored view is a second source of truth and drifts by default

#### Unknowns
  * spe6-3-1-u1 - how a generated view is known to be faithful is undecided: the spec is the one thing
    in the method with no upstream source to check against, so a wrong view is undetectable in a
    way a wrong status never is; the candidates are generating wholly and verifying somehow,
    generating only the mechanical parts and authoring the drawing, or authoring and parity-checking


---

### spe6-3-2 · read what is in place as the ideal plus its status

> **As whoever asks what is actually built I want the answer read off the ideal and its run, so
> that there is no second document for the first one to disagree with.**

#### Information

| Information | IO | Description | Required | Provenance |
|---|---|---|---|---|
| spe6-3-2-inf1 | In | `spec` | yes | authored |
| spe6-3-2-inf2 | In | `run` | yes | observed |
| spe6-3-2-inf3 | Out | `view` | yes | derived |

#### User Requirements
  * spe6-3-2-ur1 - what is really in place is the ideal plus its derived status; the unproven
    subjects **are** what is not there
  * spe6-3-2-ur2 - no separate as-built document is authored

#### System Requirements

#### Non-Functional Requirements
  * spe6-3-2-nfr1 - two documents that disagree leave the reader believing whichever they opened

#### Unknowns


---

### spe6-3-3 · answer what a change would put in question

> **As somebody about to edit a claim I want to be told which proofs that puts in doubt, so that
> the question I actually ask before editing has an answer worth waiting for.**

#### Information

| Information | IO | Description | Required | Provenance |
|---|---|---|---|---|
| spe6-3-3-inf1 | In | `manifest` | yes | observed |
| spe6-3-3-inf2 | In | `citation.ref` | yes | observed |
| spe6-3-3-inf3 | In | `subject.key` | yes | parent |
| spe6-3-3-inf4 | Out | `view` | yes | derived |

#### User Requirements
  * spe6-3-3-ur1 - the proofs a change puts in doubt are a lookup rather than an investigation
  * spe6-3-3-ur2 - the answer is *which proofs are now in question* and never *what else might
    break*

#### System Requirements
  * spe6-3-3-sr1 - only direct citations are reported — the tests that name the subject — never
    transitive code impact

#### Non-Functional Requirements
  * spe6-3-3-nfr1 - a map from subject to code that rots is worse than no map

#### Unknowns


---

### spe6-3-4 · join the planning overlay by subject

> **As an executive I want budget, schedule and resource beside the subjects they belong to, so
> that the facts I plan with are not smuggled into a spec that cannot prove them.**

#### Information

| Information | IO | Description | Required | Provenance |
|---|---|---|---|---|
| spe6-3-4-inf1 | In | `view` | yes | spe6-3-1 |
| spe6-3-4-inf2 | In | `overlay` | yes | authored |
| spe6-3-4-inf3 | In | `overlay.entry` | yes | authored |
| spe6-3-4-inf4 | Out | `view` — joined | yes | derived |

#### User Requirements
  * spe6-3-4-ur1 - the overlay is keyed by subject and joined at view time, never merged into the spec
  * spe6-3-4-ur2 - an overlay may **add** facts and may never restate one the spec holds
  * spe6-3-4-ur3 - an overlay carries the facts nothing can prove: budget, schedule, resource,
    priority, estimate

#### System Requirements

#### Non-Functional Requirements
  * spe6-3-4-nfr1 - a defined place for these facts is what stops them being smuggled into the spec

#### Unknowns
  * spe6-3-4-u1 - what keeps the overlay honest is undecided: none of it is provable, the discipline
    protecting the spec does not reach it, and these are the fields an executive view leans on
    hardest; whether it is versioned, reviewed, expiring, or marked unverifiable wherever it
    surfaces is open


---

### spe6-3-5 · report declared policy against derived reality

> **As a team with a standard I want the view to tell me where we are not meeting it, so that our
> policy is somewhere it can be checked rather than somewhere it cannot.**

#### Information

| Information | IO | Description | Required | Provenance |
|---|---|---|---|---|
| spe6-3-5-inf1 | In | `overlay.entry.required_depth` | yes | authored |
| spe6-3-5-inf2 | In | `verdict.achieved` | yes | observed |
| spe6-3-5-inf3 | Out | `view` — with the gap named | yes | derived |

#### User Requirements
  * spe6-3-5-ur1 - what a team expects is authored, what it achieved is derived, and the comparison
    is reported as a fact
  * spe6-3-5-ur2 - nothing here enforces the policy; failing a build on the gap is the team's own
    gate to add

#### System Requirements
  * spe6-3-5-sr1 - the comparison is mechanical: what was achieved either meets what was declared or
    does not

#### Non-Functional Requirements
  * spe6-3-5-nfr1 - a tool that refuses to carry a team's policy makes them keep it somewhere it
    cannot be checked

#### Unknowns


---

### spe6-3-6 · stamp what it was made from

> **As somebody being shown a roll-up I want it to say what it was made from and when, so that I
> can tell a report from a slide.**

#### Information

| Information | IO | Description | Required | Provenance |
|---|---|---|---|---|
| spe6-3-6-inf1 | In | `view` | yes | spe6-3-1 |
| spe6-3-6-inf2 | Out | `view.provenance` | yes | derived |

#### User Requirements
  * spe6-3-6-ur1 - every rendering states which spec, which run, which overlay, and when it was made

#### System Requirements

#### Non-Functional Requirements
  * spe6-3-6-nfr1 - a roll-up without provenance is indistinguishable from a slide, and a stale one
    is worse than none

#### Unknowns


---

### spe6-3-7 · refuse a view that asserts more than its source

> **As anybody downstream of a number I want it to be the number the run produced, so that the
> whole apparatus underneath it is worth having.**

#### Information

| Information | IO | Description | Required | Provenance |
|---|---|---|---|---|
| spe6-3-7-inf1 | In | `view` | yes | spe6-3-1 |
| spe6-3-7-inf2 | In | `view.provenance` | yes | spe6-3-6 |
| spe6-3-7-inf3 | Out | `view.assertion` | yes | derived |

#### User Requirements
  * spe6-3-7-ur1 - a projection may summarise, aggregate and omit
  * spe6-3-7-ur2 - a projection may never state a status, a completion or a date its source does not
    support
  * spe6-3-7-ur3 - a refused view goes back to be projected again rather than onward

#### System Requirements

#### Non-Functional Requirements
  * spe6-3-7-nfr1 - aggregation is where fakery re-enters a verified system
  * spe6-3-7-nfr2 - the method is worthless if the number shown upward is not the number the run
    produced

#### Unknowns


## Glossary

| Term | Meaning |
|---|---|
| View | A projection of the spec for an audience — a roll-up, a flow, a trace table. Derived on demand, never authored or maintained. |
| Overlay | Planning facts the spec does not own because nothing can prove them, keyed by subject and joined at view time. Additive only. |
| Required depth | What a team expects a subject to reach. Authored in the overlay, compared against what was achieved, never imposed. |
| View provenance | Which spec, which run, which overlay, and when — stamped on every rendering. |
| Assertion | What a view says. May summarise and omit; may never exceed its source. |

---

## Working notes — not part of the chapter

**Three questions, one apparatus.** spe6-3-1, spe6-3-2 and spe6-3-3 are the three things an audience actually
asks, and they are separate steps rather than one because their inputs differ: the first needs the
run for status, the second *is* the run read against the ideal, and the third needs what cites what.
All three converge on the same stamp and the same refusal, which is what stops one of them
acquiring a private set of rules.

**`manifest`, `citation.ref` and `verdict.achieved` are the neighbour's.** They are consumed here
and defined in the sibling corpus, which is what spe1-1-2 exists to let a gate resolve.
