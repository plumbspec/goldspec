"""The gold-spec methodology — the conventions for writing a spec, and the gates that keep it honest.

**This is not plumb.** Plumb observes a run and derives a board; it works for any project with any
workflow, and it neither requires a spec nor knows this package exists. That separation is the whole
design: a project adopts a methodology by installing one, never by being handed one.

What lives here is everything that presumes *conventions* — how a subject is declared, where flows
live, what a chapter looks like. Those checks could never be part of the tool, because to run them a
tool must decide what a story is and where it lives, which is mandating a workflow. Opted into, the
same checks are simply the method a project chose.

There is no importable vocabulary here and no longer any reason for one. A subject is declared by
its row in a chapter's trace table, so a spec is markdown a person reads and not a module somebody's
runner has to collect — which is what makes the method sayable to a project in any language.

The dependency runs one way and must keep running one way: goldspec may read plumb's manifest and a
project's spec; nothing under ``src/plumb`` may import this package.
"""

#: The one authored version. The cut derives `<base>.dev<n>+<sha>` from it and stamps
#: the artifact, so this is never the version anybody reads back — see plumb's releasing runbook.
BASE_VERSION = "0.5.0"

try:  # written into the artifact at build time; absent in a checkout, which is not a build
    from goldspec._built import VERSION as __version__
except ImportError:
    __version__ = BASE_VERSION

from goldspec.conventions import (
    CITATION_MARKER,
    CONFIG_NAME,
    FLOW_DIR,
    FLOW_GLOB,
    NAMESPACE,
    ConfigError,
    Conventions,
    conventions_for,
    find_config,
)
from goldspec.specgate import Report, check_spec_directory

# `conventions_for` is exported because it is the point: the command calls it, and a project holding
# its spec to the gates on every run calls the same one from its own suite. Reaching instead for
# `Conventions(...)` with values typed into a test is what leaves two gates over one spec that
# cannot see each other.
__all__ = [
    "NAMESPACE",
    "FLOW_DIR",
    "FLOW_GLOB",
    "CITATION_MARKER",
    "CONFIG_NAME",
    "ConfigError",
    "Conventions",
    "conventions_for",
    "find_config",
    "Report",
    "check_spec_directory",
]
