# Legend — what a shape means

One legend for every flow in this corpus. Each chapter's diagram carries its own `classDef` lines,
so a flow can be copied and rendered on its own; the shapes those classes stand for are here.

```mermaid
flowchart TD
    LT([START / END — named in caps, so it reads in greyscale]):::terminal
    LA[action]:::process
    LD{question}:::question
    LS[[sub-flow — drills down into its own chapter]]:::subroutine
    LG([reached]):::good
    LB[/REFUSED — a different shape, so it reads in greyscale/]:::bad
    LP>"parameter — a value still to discover"]:::parameter
    LA -.tuned by.-> LP

    classDef terminal fill:#eef0ee,stroke:#52514e,color:#0b0b0b;
    classDef process fill:#e9eef5,stroke:#2a78d6,color:#0b0b0b;
    classDef question fill:#fdf3d8,stroke:#b8860b,color:#0b0b0b;
    classDef subroutine fill:#e9eef5,stroke:#2a78d6,color:#0b0b0b;
    classDef good fill:#e2f2e2,stroke:#0ca30c,color:#0b0b0b;
    classDef bad fill:#f7e4e4,stroke:#b02a2a,color:#0b0b0b;
    classDef parameter fill:#f4f2ee,stroke:#8a6212,color:#0b0b0b,stroke-dasharray:2 2;
```

Shape carries the role, so a flow reads in greyscale and in print.

Seven shapes, and the set is closed: six are steps of a flow, and a parameter hangs off the step it
tunes. What is undecided and what is imposed are **not** shapes: they carry ids under the node they affect, where a reader meets them beside the step
rather than in the margin of a picture.
