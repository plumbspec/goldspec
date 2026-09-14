# ent · enter the method

**Last updated** 2026-09-15 v4

What a team with years of specifications in whatever shape they accumulated does to start using
this method on them — without hand-converting everything first, and without a day where nothing
resolves. Exits to [spe · specify a process](spe-specify-a-process.md), which is what they do
afterwards.

```mermaid
flowchart TD
    IN([<b>START</b> · specifications in whatever shape<br/>they accumulated, and no method yet]):::terminal

    BRING[<b>ent1</b> · bring the corpus in, in one audited pass]:::process
    EXTENT[<b>ent2</b> · state what the corpus is]:::process
    MULTIQ{does the project<br/>carry more than one spec?}:::question
    OWN[<b>ent3</b> · let each spec own its domain outright]:::process
    ADD[<b>ent4</b> · add to a spec without forking it]:::process
    CONV[<b>ent5</b> · convert one chapter, renumbering nothing]:::process
    HELD[<b>ent6</b> · declare what this project is held to]:::process

    OUT([<b>END</b> · a corpus the gates read, converted<br/>as far as the team has got]):::good

    IN --> BRING --> EXTENT --> MULTIQ
    MULTIQ -->|yes| OWN --> ADD --> CONV
    MULTIQ -->|no| CONV
    CONV --> HELD
    HELD -->|chapters remain| CONV
    HELD -->|all converted| OUT

    classDef terminal fill:#eef0ee,stroke:#52514e,color:#0b0b0b;
    classDef process fill:#e9eef5,stroke:#2a78d6,color:#0b0b0b;
    classDef question fill:#fdf3d8,stroke:#b8860b,color:#0b0b0b;
    classDef good fill:#e2f2e2,stroke:#0ca30c,color:#0b0b0b;
```

## Nodes

### ent1 · bring the corpus in, in one audited pass

> **As somebody with years of decisions in whatever shape they accumulated I want to enter the
> method without hand-converting them first, so that the cost of trying it is a run rather than a
> project.**

#### Information

| Information | IO | Description | Required | Provenance |
|---|---|---|---|---|
| ent1-inf1 | In | `existing_corpus` | yes | authored |
| ent1-inf2 | Out | `migration` | yes | derived |
| ent1-inf3 | Out | `subject.label` | yes | derived |

#### User Requirements
  * ent1-ur1 - the pass records what it changed, in the same shape as any other change report
  * ent1-ur2 - the ids a corpus arrived with are kept, so entering costs nobody a re-minted
    corpus
  * ent1-ur3 - the pass is reversible, and says so where somebody deciding whether to try it
    will read it

#### System Requirements
  * ent1-sr1 - the pass is bounded and reported: what it read, what it changed, and what it
    could not

#### Non-Functional Requirements
  * ent1-nfr1 - the normal adopter is not a fresh repository

#### Unknowns


---

### ent2 · state what the corpus is

> **As a gate reading half a corpus I want the spec to say where the rest of it is, so that I can
> tell a correct reference to a neighbour from a reference to nothing.**

#### Information

| Information | IO | Description | Required | Provenance |
|---|---|---|---|---|
| ent2-inf1 | In | `migration` | yes | ent1 |
| ent2-inf2 | Out | `conventions` | yes | authored |
| ent2-inf3 | Out | `sibling_spec` | yes | authored |

#### User Requirements
  * ent2-ur1 - a spec names its sibling specs, which are read for the names they define and
    never checked here
  * ent2-ur2 - a project says what its own subjects are called
  * ent2-ur3 - the conventions live in one place, read by the command and by whatever the
    project runs as a test

#### System Requirements
  * ent2-sr1 - what the corpus is cannot be inferred; a gate reading one spec directory is told
    rather than guesses
  * ent2-sr2 - a project carrying two specs in two namespaces puts a conventions file beside
    each

#### Non-Functional Requirements
  * ent2-nfr1 - *defined nowhere* means nowhere after the siblings have been read

#### Unknowns


---

### ent3 · let each spec own its domain outright

> **As somebody reading one of a project's several specs I want to know that nothing in it is
> restated from another, so that I never have to work out which of two statements is current.**

#### Information

| Information | IO | Description | Required | Provenance |
|---|---|---|---|---|
| ent3-inf1 | In | `conventions` | yes | ent2 |
| ent3-inf2 | Out | `spec` | yes | authored |

#### User Requirements
  * ent3-ur1 - no spec restates what another owns, and every cross-reference is a citation
  * ent3-ur2 - where the work spans repositories, the spec splits per repository and the
    contract is stated from both sides

#### System Requirements
  * ent3-sr1 - a name defined in two specs demands an entry saying what the two mean to each
    other

#### Non-Functional Requirements
  * ent3-nfr1 - several specs are one truth by that rule, never by anybody remembering which
    document is current

#### Unknowns


---

### ent4 · add to a spec without forking it

> **As whoever maintains an extension I want its steps specified without forking the spec it
> extends, so that the two cannot drift into disagreeing about anything.**

#### Information

| Information | IO | Description | Required | Provenance |
|---|---|---|---|---|
| ent4-inf1 | In | `spec` | yes | ent3 |
| ent4-inf2 | Out | `spec.extends` | yes | authored |

#### User Requirements
  * ent4-ur1 - an extension declares the spec it builds on, and may contribute steps, unknowns
    and flows of its own
  * ent4-ur2 - an extension may not redefine, restate or contradict anything the base owns
  * ent4-ur3 - a base stands on its own and works when no extension is present

#### System Requirements
  * ent4-sr1 - citation runs one way: an extension cites its base, and a base never cites an
    extension
  * ent4-sr2 - a base cannot enumerate what extends it

#### Non-Functional Requirements
  * ent4-nfr1 - stating the base once, completely, is what makes the two incapable of disagreeing

#### Unknowns
  * ent4-u1 - a base cannot rewrite citations held in an extension it does not know about, so a
    renumber clean in the base silently breaks anything extending it; the candidate answer is that
    publishing freezes ids, which makes renumbering a breaking change rather than a tidy-up


---

### ent5 · convert one chapter, renumbering nothing

> **As somebody holding a spec in an older shape I want to convert one chapter at a time without
> renumbering anything, so that every citation into it keeps resolving while I work.**

#### Information

| Information | IO | Description | Required | Provenance |
|---|---|---|---|---|
| ent5-inf1 | In | `chapter` | yes | parent |
| ent5-inf2 | Out | `step` | yes | authored |
| ent5-inf3 | Out | `requirement` | yes | authored |
| ent5-inf4 | Out | `open_unknown` | optional | authored |

#### User Requirements
  * ent5-ur1 - a chapter converts without renumbering
  * ent5-ur2 - each claim of the older shape is read for what **kinds** of thing are in it, and
    each kind gets its own id
  * ent5-ur3 - what comes out was already written down, in the one place the older shape had for
    everything
  * ent5-ur4 - a chapter is brought to the current shape when it is touched

#### System Requirements
  * ent5-sr1 - the kind-finding half runs last

#### Non-Functional Requirements
  * ent5-nfr1 - a corpus may be half converted for as long as its owner likes

#### Unknowns


---

### ent6 · declare what this project is held to

> **As the owner of a corpus written before this format I want a chapter judged by the shape it is
> written in, so that converting is something I can start on a Tuesday with one chapter.**

#### Information

| Information | IO | Description | Required | Provenance |
|---|---|---|---|---|
| ent6-inf1 | In | `fault` | yes | parent |
| ent6-inf2 | In | `conventions` | yes | ent2 |
| ent6-inf3 | Out | `conventions.held` | yes | authored |

#### User Requirements
  * ent6-ur1 - a chapter is held to the shape it is written in; one in an older shape is read
    the old way and counted
  * ent6-ur2 - converting one chapter puts that chapter in scope and no other
  * ent6-ur3 - nothing has to be declared, unset or remembered for a half-converted corpus to be
    judged correctly
  * ent6-ur4 - every check the gate carries runs on every spec; there is no flag holding one
    back

#### System Requirements
  * ent6-sr1 - what a reader must judge is reported and never gated; what has an invariant is
    gated and never merely reported

#### Non-Functional Requirements
  * ent6-nfr1 - every corpus that exists predates a new format

#### Unknowns

## Glossary

| Term | Meaning |
|---|---|
| Conventions | What a project's subjects are called and where its spec lives. One home, read by the command and by whatever the project runs as a test. |
| Sibling spec | Another spec directory of the same corpus. Read for what it defines, never checked here. |
| Corpus | Every spec directory whose flows exchange information — one body, whatever number of repositories it spans. |
| Spec | One body of specification with a domain of its own. A project may carry several; none restates another. |
| Extension | A spec that declares a base and adds to it. Additive only, never restating, and meaningless without the base it names. |
| Base | The spec an extension builds on. Stands alone, and never cites what extends it. |
| Migration | One audited, reported, reversible pass over a corpus that predates the method. |
| Provenance | Where an input came from, or how an output was made. |
| Authored | Written by a person. An input nothing produces, or an output somebody typed. |
| Derived | Computed by this step from what it took in. |
| Parent | On a sub-flow's input: handed in by the chapter this one drills into. |

---

## Working notes — not part of the chapter

**ent5 and ent6 are the phase-in.** A chapter is judged by the shape it is written in, so converting one puts that chapter in scope and no other, and neither half of a half-converted
corpus is failed for being the half it is.

**The ordering question the flow answers.** ent2 comes before any conversion because *defined
nowhere* cannot be switched on until the corpus extent is stated (ent2-nfr1) — a conversion run
under an unstated extent reports faults that are references to neighbours.
