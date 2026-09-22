# tomli — vendored

`tomli` 2.4.1, unmodified, MIT (see `LICENSE`). This is the parser that became `tomllib` in
Python 3.11: the same code by the same author, so a project below 3.11 gets the same reading of
its `goldspec.toml` as one above it rather than an approximation of it.

**Read `goldspec.conventions` before changing anything here.** The standard library is preferred
wherever it exists, so on 3.11 and up not a line of this is imported.

**Why a copy of our own, when plumb carries one too.** Nothing under `src/` may import the tool —
`test_boundary.py` reads this source and fails on a single import — because a spec has to be
checkable by somebody who has not installed it. Sharing the parser would be that import. Two
copies of an unmodified upstream release is the price of a boundary worth having.

Updating it: copy the release wholesale, keep this file and `LICENSE`, change nothing else.
