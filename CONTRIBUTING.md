# Contributing to goldspec

Thanks for helping keep specifications honest.

## Running the suite

    pip install -e ".[dev]"
    pytest
    goldspec spec

`pytest` runs the tests; `goldspec spec` runs the gate over goldspec's own spec, and both must
pass. goldspec runs on Python 3.9 or later, and `tests/test_floor.py` holds what ships to that
floor.

## Ground rules

- **The spec is the authority.** `spec/` is goldspec's own gold-spec, starting from
  `spec/diagrams/spe-specify-a-process.md`. A change to what the gate does lands with the story it
  serves and the test that proves it.
- **The method is gated by itself.** goldspec's spec passes its own gate. A rule the gate would
  fail goldspec's spec on is a rule to fix in the spec or in the gate, never to exempt.
- **Nothing here imports plumb, and nothing plumb ships imports goldspec.** `tests/test_boundary.py`
  holds this side of it. See [the README](README.md#this-is-not-plumb-and-nothing-plumb-ships-imports-it).
- **Conventions are the project's.** A check that only works with goldspec's own namespace, file
  pattern or directory is a check that mandates a workflow; it reads `goldspec.toml` like every
  other.

## Checking the documentation is true

The guides are tested by people who have never seen goldspec: give one only the documentation and
ask for a spec that passes the gate. Whatever they had to guess is a gap in the documentation, and
whatever a test could hold becomes a test in `tests/test_docs.py`.

## Scope

goldspec keeps its scope tight on purpose. Before a large change, propose it at
[support.plumbspec.org](https://support.plumbspec.org) so we can agree it fits before you build it.
