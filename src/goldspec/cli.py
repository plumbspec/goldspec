"""`goldspec` — run the methodology's gates over a spec directory.

Deliberately thin, and deliberately separate from `plumb`. The gates are ordinarily run as tests in
your own suite, which is what lets Plumb observe them without learning they are methodology gates.
This command exists for the other moment: checking a spec directory before you have wired anything,
or from a shell while authoring.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from goldspec import __version__
from goldspec.conventions import CONFIG_NAME, ConfigError, conventions_for, find_config
from goldspec.specgate import check_spec_directory


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="goldspec", description=__doc__.splitlines()[0])
    parser.add_argument("--version", action="version", version=f"goldspec {__version__}")
    parser.add_argument("spec", nargs="?", default="spec", help="the spec directory (default: spec)")
    parser.add_argument(
        "--sibling", action="append", default=[], metavar="DIR",
        help="another spec directory of the same corpus, read for the elements it defines and not "
             "checked. Repeatable. A corpus that spans repositories has to say so, because a gate "
             "seeing half of one cannot tell a wrong reference from a distant one")
    args = parser.parse_args(argv)

    spec = Path(args.spec)
    if not spec.is_dir():
        parser.error(f"no spec directory at {spec} — goldspec checks a spec you have written")

    # The project's own conventions, from the project's own file, by the loader an adopter's
    # gate-as-test calls too. This line used to build them from the module defaults with no way to
    # override, so the only specs the command could read were the ones whose ids already looked like
    # ours: a spec namespaced `sh` was told it "declares no subjects at all", which reads as a
    # verdict on the spec rather than as the command having been handed the wrong strings.
    try:
        conv = conventions_for(spec, siblings=tuple(Path(s) for s in args.sibling))
    except ConfigError as bad:
        parser.error(str(bad))

    # Which strings this run judged the spec by, on stderr so stdout stays exactly the gate's report
    # (`vie7`). Printed on every run, including the clean ones: every fault this command can report
    # is phrased as a verdict on the spec, and where the real cause is a convention mismatch the
    # reader has no way to suspect it. Naming the basis is what makes a wrong verdict diagnosable
    # instead of a reason to conclude the method does not fit.
    source = find_config(spec)
    print(f"goldspec: conventions from {source}" if source
          else f"goldspec: no {CONFIG_NAME} found — checking against the defaults", file=sys.stderr)
    # The strings themselves now travel on the report, so a library caller sees the same basis the
    # command does. Only WHICH FILE they came from is the command's to say — `check_spec_directory`
    # is handed a `Conventions` and never learns where it was read from.

    report = check_spec_directory(spec, conv, cited_from=spec.parent)

    # What the run actually read, on stderr beside the conventions and for the same reason: stdout
    # is exactly the gate's problems and their count (`vie7`), and a line of context there would be
    # a view stating something its source does not.
    #
    # Printed at all because `Report.checked` says of itself that it matters as much as `problems`
    # — a run that checked nothing and found nothing is not a pass — and the command had been
    # computing every one of these lines and dropping them. So `0 fault(s)` was the whole output
    # whether the gate had read seven chapters or none, and the observations three pages of
    # documentation promise a reader ("the run says what it saw and you decide") were never said.
    for line in report.checked:
        print(f"goldspec: {line}", file=sys.stderr)

    # Read straight off the report, never through `getattr(report, ..., default)`. This line spent
    # its whole life as `getattr(report, "faults", None) or []` — an attribute `Report` has never
    # had — so every run printed no faults and exited 0 whatever the spec contained. The guard is
    # what made it silent: a plain attribute access on a name that moved raises, and a crash on the
    # first run is cheap. A default turns the same mistake into a gate that passes unconditionally,
    # which is the one failure this command exists to make impossible.
    for problem in report.problems:
        print(problem)
    print(f"{len(report.problems)} fault(s) in {spec}")
    return 1 if report.problems else 0


if __name__ == "__main__":
    raise SystemExit(main())
