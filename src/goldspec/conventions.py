"""What the spec gate reads — settings, not a standard.

These configure ``specgate.py``, and they are **defaults**: a spec laid out differently states its
own and is checked just the same. Nothing here is a claim on anybody who has not installed goldspec,
and none of it reaches Plumb. Plumb does not read a spec, so it holds no opinion about how a project
names its subjects, where it keeps them, or whether it keeps any at all: a board answers for the ids
a run's tests cited, against ids that stay opaque to it (``ch2-14``, ``ch2-2``).

**A project's conventions have one home, and both readers use it.** The gates reach a project two
ways — as the ``goldspec`` command while authoring, and as ``check_spec_directory`` called from the
project's own suite — and for as long as only the second could be told a project's conventions, the
first enforced ours on everybody. A spec whose ids read ``sh`` was told it declared no subjects at
all: a verdict on the spec, phrased as though the method did not fit, when the command had simply
read ``sh`` as ``ch``. The workaround was to call the gate from a test with the right values, which
left two gates over one spec holding different conventions and unable to see each other — a second
home for a fact the project already owns, arriving through the tooling rather than the corpus.

So the conventions are read from a file the project owns, by :func:`conventions_for`, which the
command calls and an adopter's own gate-as-test calls. One loader, one answer. A project that has
no such file gets the values below, which is every adopter who took our habits and is why adding
this changed nothing for them.
"""

from __future__ import annotations

try:
    import tomllib
except ModuleNotFoundError:
    # Below 3.11 the same parser rides inside this package rather than being installed beside it
    # (`goldspec._vendor`). One reading of an adopter's file on every version goldspec runs on.
    from goldspec._vendor import tomli as tomllib
from dataclasses import dataclass, fields
from pathlib import Path

#: The prefix every story id carries — ``ch`` here, ``REQ`` or ``op`` elsewhere.
NAMESPACE = "ch"

#: Where the process flows live, relative to the spec directory.
FLOW_DIR = "diagrams"

#: How a flow file is named.
FLOW_GLOB = "chapter-*.md"

#: What a citing test looks like, for the gate that refuses a citation to a story nobody declared.
CITATION_MARKER = "proves"

#: What the file is called. Named for the product rather than for the spec, because it configures
#: the *method* a project adopted and not the corpus a chapter belongs to.
CONFIG_NAME = "goldspec.toml"

#: The one table read out of it. Everything else in the file belongs to whoever put it there — a
#: project may keep other tooling's settings in the same file, and a key this version does not know
#: inside ``[conventions]`` is refused rather than ignored (see :func:`conventions_for`).
CONFIG_TABLE = "conventions"


class ConfigError(Exception):
    """A ``goldspec.toml`` that could not be honoured. Never falls back to the defaults.

    Silence is the failure mode this whole module was rewritten for. A project that wrote a
    conventions file and got our conventions anyway would be told its spec is wrong in the same
    words as a project that wrote no file at all, and the two situations could not be told apart
    from the output. Refusing costs one loud run; defaulting costs a corpus judged against strings
    nobody chose.
    """


@dataclass(frozen=True)
class Conventions:
    """Where a spec lives, and what it names things.

    The defaults are this project's own habits, and they are defaults rather than a format: a
    caller points the same checks at whatever layout their spec actually has. Nobody is asked to
    match them, and adopting goldspec means adopting the *shape* — a subject is a trace row, placed
    in a flow — not these particular strings.

    Built from a project's own file by :func:`conventions_for`, or constructed directly by a caller
    that has its values from somewhere else. The defaults are the module constants above rather than
    literals repeated here, so the command and this dataclass cannot drift apart.
    """

    namespace: str = NAMESPACE
    flow_glob: str = FLOW_GLOB
    flow_dir: str = FLOW_DIR
    #: Other spec directories of the same corpus — **resolved against, never checked**.
    #:
    #: A namespace spans repositories (`cus2`) and so does the element corpus: this methodology's
    #: chapter 7 consumes elements the tool's chapters 1 and 2 define, and the tool's chapter 0
    #: consumes one of ours. Run over either directory alone, four correct references read as
    #: consumed-and-defined-nowhere.
    #:
    #: The gate cannot prove an element is undefined while it can only see part of the corpus, so
    #: the corpus states its own extent instead of the gate guessing at it. A sibling's chapters are
    #: read for the names they define and are not gated here — they are gated by their own run,
    #: where they are the subject rather than the context. Unresolved *after* siblings is what
    #: `spe5` was always about.
    siblings: tuple = ()


def find_config(spec: Path) -> Path | None:
    """Where a project's ``goldspec.toml`` is, or ``None``.

    Two places, in order: beside the chapters, then beside the spec directory. Deliberately not a
    walk to the filesystem root — an upward search finds a file the adopter did not write, in a
    parent directory they may not own, and reports its conventions as theirs. Two locations can be
    stated in a sentence and checked by eye, which is what a first-contact tool owes.
    """
    spec = Path(spec)
    for where in (spec / CONFIG_NAME, spec.parent / CONFIG_NAME):
        if where.is_file():
            return where
    return None


def conventions_for(spec: Path, siblings: tuple = ()) -> Conventions:
    """The conventions a spec directory is checked under. The one home, read by both gates.

    ``siblings`` names further spec directories of the same corpus, from a caller that knows them —
    the command's repeatable ``--sibling``. They are *added* to any the file names rather than
    replacing them, because a sibling is a location and not a convention: the file says what the
    corpus is, and a caller may know about one more on this machine without the project having
    changed its mind about anything.

    Paths in the file resolve against the file's own directory, which is what a reader of that file
    would assume, and is stable wherever the command is invoked from.
    """
    spec = Path(spec)
    found = find_config(spec)
    if found is None:
        return Conventions(siblings=tuple(siblings))

    try:
        loaded = tomllib.loads(found.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError) as bad:
        raise ConfigError(f"{found} could not be read — {bad}") from bad
    except tomllib.TOMLDecodeError as bad:
        raise ConfigError(f"{found} is not valid TOML — {bad}") from bad

    table = loaded.get(CONFIG_TABLE, {})
    if not isinstance(table, dict):
        raise ConfigError(f"{found}: [{CONFIG_TABLE}] must be a table, not {type(table).__name__}")

    known = {f.name: f for f in fields(Conventions)}
    settings: dict = {}
    for key, value in table.items():
        if key not in known:
            # Refused rather than ignored. A misspelled key that is quietly dropped leaves the
            # project checked under a convention it believes it changed, and the evidence of the
            # typo is the absence of an effect — which is the hardest thing there is to notice.
            raise ConfigError(
                f"{found}: [{CONFIG_TABLE}] has no key {key!r}. This version reads: "
                f"{', '.join(sorted(known))}")
        if key == "siblings":
            if not isinstance(value, list) or not all(isinstance(p, str) for p in value):
                raise ConfigError(f"{found}: siblings must be a list of paths")
            settings[key] = tuple((found.parent / p).resolve() for p in value)
        elif isinstance(known[key].default, bool):
            # Dispatched on the field's own type rather than on its name. Naming them one at a time
            # meant the second flag added was refused as "must be a non-empty string", by a loader
            # that had every fact it needed to know better.
            if not isinstance(value, bool):
                raise ConfigError(f"{found}: {key} must be true or false")
            settings[key] = value
        else:
            if not isinstance(value, str) or not value.strip():
                raise ConfigError(f"{found}: {key} must be a non-empty string")
            settings[key] = value

    settings["siblings"] = tuple(settings.get("siblings", ())) + tuple(siblings)
    return Conventions(**settings)
