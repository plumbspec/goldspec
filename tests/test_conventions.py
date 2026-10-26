"""A project's conventions have one home, and both gates read it.

A spec whose subjects are `sh*`, checked by a command that reads `sh` ids as `ch`, produces faults
that are artifacts of the strings it was handed and none of them true of that spec. The command built its conventions
from module defaults and exposed no way to say otherwise, while the library had always taken them —
so the only adopters the command served were the ones whose ids already looked like ours.

**The property asserted here is that the conventions the gate uses came from the project.** A test
that only checks a correct file parses would be satisfied by a loader whose result nothing consults,
which is the inert-check failure this method complains about more than any other. So the centrepiece
is a *comparison*: one spec, checked twice, differing only in whether the project's file was there.
A loader that parsed perfectly and was then ignored fails that and passes almost anything else.

The other half is refusal. Every way a conventions file can be wrong is refused rather than absorbed,
because a project that wrote a file and got our defaults anyway is told its spec is broken in exactly
the same words as a project that wrote no file — and cannot tell which happened from the output.
"""

from pathlib import Path

import pytest

from goldspec.cli import main
from goldspec.conventions import CONFIG_NAME, ConfigError, Conventions, conventions_for, find_config
from goldspec.specgate import check_spec_directory

#: The same one-subject spec as `test_cli`, in somebody else's namespace. Kept minimal deliberately:
#: what is under test is which strings the gate was handed, and a larger spec would only add ways
#: for it to fail for reasons that are not this.
FOREIGN = """# Chapter 1 — a spec that is not in our namespace

**Last updated** 2026-09-15 v1

> **As somebody with their own id scheme I want the gate to read it, so that adopting the method
> is not adopting somebody's prefixes.**

```mermaid
flowchart TD
    START([START]):::terminal
    P1[sh1-1 the subject]:::process
    DONE([END]):::good
    START --> P1 --> DONE

    classDef terminal fill:#eef0ee,stroke:#52514e,color:#0b0b0b;
    classDef process fill:#e9eef5,stroke:#2a78d6,color:#0b0b0b;
    classDef good fill:#e2f2e2,stroke:#0ca30c,color:#0b0b0b;
```

## Nodes

### sh1-1 · the subject

> **As somebody reading this I want one step to exist, so that the gate has something to read.**

#### Information

| Information | IO | Description | Required | Provenance |
|---|---|---|---|---|
| sh1-1-inf1 | In | `request` | yes | authored |
| sh1-1-inf2 | Out | `answer` | yes | derived |

#### User Requirements
  * sh1-1-ur1 - the step produces an answer for the request it was given

#### System Requirements

#### Non-Functional Requirements

#### Unknowns

## Glossary

| Term | Meaning |
|---|---|
| Request | What arrives |
"""


def _foreign_spec(root: Path) -> Path:
    chapter = root / "spec" / "diagrams" / "chapter-01-example.md"
    chapter.parent.mkdir(parents=True, exist_ok=True)
    chapter.write_text(FOREIGN, encoding="utf-8")
    return root / "spec"


def _config(where: Path, body: str) -> Path:
    where.mkdir(parents=True, exist_ok=True)
    (where / CONFIG_NAME).write_text(body, encoding="utf-8")
    return where / CONFIG_NAME


# ── the measured defect, proved by the difference ──────────────────────────────────────────────


def test_a_spec_in_another_namespace_is_judged_by_its_own_conventions(tmp_path):
    """An adopter's own namespace, both ways round. The assertion is the *difference* between them.

    Without the file the gate reads `sh` ids as `ch`, finds nothing it recognises, and says the spec
    declares no subjects at all — which reads as a verdict on the spec rather than as the gate
    having been handed the wrong strings. With the file the same bytes check clean.
    """
    spec = _foreign_spec(tmp_path)

    ours = check_spec_directory(spec, conventions_for(spec), cited_from=spec.parent)
    assert any("not namespaced to its chapter" in problem for problem in ours.problems), (
        "the fixture no longer triggers the mismatch it exists to demonstrate, so the comparison "
        f"below proves nothing: {ours.problems}")

    _config(tmp_path, '[conventions]\nnamespace = "sh"\n')
    theirs = check_spec_directory(spec, conventions_for(spec), cited_from=spec.parent)

    assert theirs.problems == [], (
        "a spec that states its own namespace is still being checked against ours — the conventions "
        f"were loaded and then not used, which is the failure this file exists to catch: "
        f"{theirs.problems}")


def test_the_command_reads_the_projects_file(tmp_path, capsys):
    """The same property through the entry point, because that is where the defect was found.

    The command is what an adopter runs first and is the only reader that had no way to be told.
    """
    spec = _foreign_spec(tmp_path)

    assert main([str(spec)]) == 1, "the command found no fault on a spec it cannot read"

    _config(tmp_path, '[conventions]\nnamespace = "sh"\n')
    capsys.readouterr()

    assert main([str(spec)]) == 0, (
        f"the command ignored {CONFIG_NAME}:\n{capsys.readouterr().out}")


def test_the_command_names_the_conventions_it_judged_by(tmp_path, capsys):
    """Printed on every run, and on stderr so stdout stays exactly the gate's report (`spe6-3-7`).

    Every fault the command can print is phrased as a verdict on the spec. Where the real cause is a
    convention mismatch, nothing in that output lets the reader suspect it — which is how a wrong
    verdict becomes a reason to conclude the method does not fit.
    """
    spec = _foreign_spec(tmp_path)

    main([str(spec)])
    said = capsys.readouterr().err
    assert CONFIG_NAME in said and "defaults" in said, (
        f"a run with no conventions file did not say so: {said!r}")
    assert "'ch'" in said, f"the run did not name the namespace it judged by: {said!r}"

    _config(tmp_path, '[conventions]\nnamespace = "sh"\n')
    main([str(spec)])
    said = capsys.readouterr().err
    assert str(tmp_path / CONFIG_NAME) in said, f"the run did not name the file it read: {said!r}"
    assert "'sh'" in said, f"the run named the file but not what it got from it: {said!r}"


# ── where the file lives ───────────────────────────────────────────────────────────────────────


def test_the_file_is_found_beside_the_chapters_or_beside_the_spec(tmp_path):
    spec = _foreign_spec(tmp_path)
    assert find_config(spec) is None

    beside_the_spec = _config(tmp_path, '[conventions]\nnamespace = "sh"\n')
    assert find_config(spec) == beside_the_spec

    inside = _config(spec, '[conventions]\nnamespace = "in"\n')
    assert find_config(spec) == inside, (
        "the file beside the chapters must win — it is the more specific of the two, and a project "
        "that put one there did it to override whatever sits above")


def test_no_file_means_the_defaults_and_never_an_error(tmp_path):
    """The ordinary case, and the one that must not have changed: an adopter who took our habits."""
    spec = _foreign_spec(tmp_path)
    assert conventions_for(spec) == Conventions()


def test_the_search_does_not_climb_out_of_the_project(tmp_path):
    """Two locations, not a walk to the root.

    An upward search finds a file the adopter did not write, in a directory they may not own, and
    reports its conventions as theirs — silently, and correctly as far as any check can tell.
    """
    deep = tmp_path / "a" / "b"
    spec = _foreign_spec(deep)
    _config(tmp_path, '[conventions]\nnamespace = "sh"\n')

    assert find_config(spec) is None
    assert conventions_for(spec).namespace == "ch"


# ── every way it can be wrong is refused, never absorbed ───────────────────────────────────────


def test_an_unknown_key_is_refused(tmp_path):
    """A dropped key leaves the project checked under a convention it believes it changed, and the
    evidence of the typo is the absence of an effect — the hardest thing there is to notice."""
    spec = _foreign_spec(tmp_path)
    _config(tmp_path, '[conventions]\nnamespaec = "sh"\n')

    with pytest.raises(ConfigError) as refused:
        conventions_for(spec)
    assert "namespaec" in str(refused.value) and "namespace" in str(refused.value), (
        "the refusal must name the key it did not know and the ones it does — a reader with a typo "
        f"needs the list to spot it: {refused.value}")


@pytest.mark.parametrize("body, why", [
    ('[conventions]\nnamespace = 3\n', "a number where a name goes"),
    ('[conventions]\nnamespace = ""\n', "an empty namespace matches everything and nothing"),
    ('[conventions]\nnamespace = 7\n', "a number where a string goes"),
    ('[conventions]\nsiblings = "../other/spec"\n', "one path where a list goes"),
    ('[conventions]\nsiblings = [1, 2]\n', "a list that is not of paths"),
])
def test_a_wrong_value_is_refused(tmp_path, body, why):
    spec = _foreign_spec(tmp_path)
    _config(tmp_path, body)

    with pytest.raises(ConfigError):
        conventions_for(spec)


def test_a_right_value_is_not_refused(tmp_path):
    """The counterpart to the case above: a refusal that fired on everything would pass it."""
    spec = _foreign_spec(tmp_path)
    _config(tmp_path, '[conventions]\nnamespace = "sh"\nsiblings = []\n')

    conv = conventions_for(spec)
    assert (conv.namespace, conv.siblings) == ("sh", ())


def test_a_file_that_is_not_toml_is_refused(tmp_path):
    spec = _foreign_spec(tmp_path)
    _config(tmp_path, "namespace: sh\n")

    with pytest.raises(ConfigError) as refused:
        conventions_for(spec)
    assert "not valid TOML" in str(refused.value)


def test_the_table_must_be_a_table(tmp_path):
    spec = _foreign_spec(tmp_path)
    _config(tmp_path, 'conventions = "sh"\n')

    with pytest.raises(ConfigError) as refused:
        conventions_for(spec)
    assert "must be a table" in str(refused.value)


def test_a_file_with_no_conventions_table_is_the_defaults(tmp_path):
    """The file may be shared with other tooling. Only `[conventions]` is ours."""
    spec = _foreign_spec(tmp_path)
    _config(tmp_path, '[something-else]\nkey = "value"\n')

    assert conventions_for(spec) == Conventions()


def test_the_command_refuses_a_bad_file_rather_than_checking_against_the_defaults(tmp_path):
    """Exit 2, argparse's own — a usage error, because the invocation cannot be honoured.

    Distinct from exit 1, which means the gate ran and found faults. A project whose conventions
    file is broken must never receive a fault list computed against strings it did not choose.
    """
    spec = _foreign_spec(tmp_path)
    _config(tmp_path, '[conventions]\nnamespaec = "sh"\n')

    with pytest.raises(SystemExit) as left:
        main([str(spec)])
    assert left.value.code == 2


# ── siblings: a location, not a convention ─────────────────────────────────────────────────────


def test_siblings_resolve_against_the_file_that_names_them(tmp_path):
    """Which is what a reader of that file assumes, and is stable wherever the command is run."""
    spec = _foreign_spec(tmp_path)
    (tmp_path / "other" / "spec").mkdir(parents=True)
    _config(tmp_path, '[conventions]\nsiblings = ["other/spec"]\n')

    assert conventions_for(spec).siblings == ((tmp_path / "other" / "spec").resolve(),)


def test_a_caller_may_add_a_sibling_without_replacing_the_declared_ones(tmp_path):
    """The file says what the corpus is; a caller may know about one more on this machine.

    Additive rather than overriding, because a sibling is a location and not a convention — passing
    one is not the project changing its mind about the extent of its corpus.
    """
    spec = _foreign_spec(tmp_path)
    (tmp_path / "other" / "spec").mkdir(parents=True)
    _config(tmp_path, '[conventions]\nsiblings = ["other/spec"]\n')

    conv = conventions_for(spec, siblings=(Path("/elsewhere/spec"),))
    assert conv.siblings == ((tmp_path / "other" / "spec").resolve(), Path("/elsewhere/spec"))


# ── the defaults have one home ─────────────────────────────────────────────────────────────────


def test_the_readme_example_is_a_file_the_loader_accepts(tmp_path):
    """A published example that fails if copied is worse than no example.

    The block in the README is the first `goldspec.toml` most adopters will see, and it is prose:
    nothing stops a key being renamed here and left standing there. Lifted and run rather than
    eyeballed, because the way it goes stale — a key the loader no longer knows — is now a refusal,
    so a stale example fails on the first command an adopter runs.
    """
    import re

    readme = (Path(__file__).resolve().parent.parent / "README.md").read_text(encoding="utf-8")
    blocks = re.findall(r"```toml\n(.*?)```", readme, re.DOTALL)
    assert blocks, "the README no longer shows a goldspec.toml, and this test is checking nothing"

    spec = _foreign_spec(tmp_path)
    (tmp_path / "other" / "spec").mkdir(parents=True)
    for block in blocks:
        _config(tmp_path, block)
        conventions_for(spec)  # raises ConfigError if the README has drifted from the loader


def test_the_readme_documents_every_key_the_loader_reads(tmp_path):
    """The other direction: a key nobody documented is one adopters learn by reading source.

    That is the whole complaint this file's feature answers — the method's surface being larger than
    what it says about itself, with the difference absorbed by adopters as archaeology.
    """
    from dataclasses import fields as dataclass_fields

    readme = (Path(__file__).resolve().parent.parent / "README.md").read_text(encoding="utf-8")
    undocumented = [f.name for f in dataclass_fields(Conventions) if f.name not in readme]
    assert not undocumented, (
        f"the loader reads keys the README never mentions: {undocumented}. An adopter who cannot "
        "find a construct does not stop — they invent a worse one and ship it")


def test_the_dataclass_defaults_are_the_module_constants(tmp_path):
    """`"ch"` was typed in two files — the constant and the dataclass — which is this method's own
    defect at the smallest scale it comes in. Asserted rather than trusted, because the two drifting
    apart would show up as the command and a gate-as-test disagreeing about an unconfigured spec."""
    from goldspec import conventions

    assert Conventions().namespace == conventions.NAMESPACE
    assert Conventions().flow_dir == conventions.FLOW_DIR
    assert Conventions().flow_glob == conventions.FLOW_GLOB


def test_a_sibling_spec_is_actually_read(tmp_path):
    """`siblings` was parsed, validated, resolved — and read by nothing.

    So `siblings` in a `goldspec.toml` and `--sibling` on the command line both did exactly
    nothing, while the line the run prints said an element was taken by nothing "in this chapter
    **or anywhere linked**" — asserting a corpus-wide search on a run that had linked nothing. A
    check that says out loud it looked is the worst one to have looking nowhere.
    """
    from goldspec import check_spec_directory
    from goldspec.conventions import Conventions

    here = Path(__file__).resolve().parent.parent / "docs/example/spec/diagrams"
    base = (here / "chapter-01-ordering.md").read_text(encoding="utf-8")

    mine = tmp_path / "mine" / "diagrams"
    mine.mkdir(parents=True)
    (mine / "chapter-01-ordering.md").write_text(base, encoding="utf-8")

    theirs = tmp_path / "theirs" / "diagrams"
    theirs.mkdir(parents=True)
    # A neighbour that plainly consumes what chapter 1 leaves with.
    (theirs / "chapter-09-fulfilment.md").write_text(
        base.replace("ch1", "ch9").replace("Chapter 1", "Chapter 9")
            .replace("| ch9-1-inf1 | In | `basket` | yes | authored |",
                     "| ch9-1-inf1 | In | `confirmation` | yes | authored |"),
        encoding="utf-8")

    def observations(conv):
        report = check_spec_directory(tmp_path / "mine", conv)
        return [line for line in report.checked if "leaves with confirmation" in line]

    assert observations(Conventions()), (
        "the fixture is wrong — `confirmation` should read as taken by nobody with no sibling")
    assert not observations(Conventions(siblings=(tmp_path / "theirs",))), (
        "the sibling's chapter consumes `confirmation` and the run still says nothing anywhere "
        "linked takes it — `siblings` is not being read")


def test_the_padding_check_runs_under_a_projects_own_conventions(tmp_path):
    """`padded` took its id prefix from the FILENAME, so it was dead for a renamed flow.

    Handed `story` for a project whose flows are `story-*.md`, it found no series under that
    prefix, compared nothing, and passed — silently, for exactly the population the conventions
    chapter is written for.
    """
    from goldspec import check_spec_directory
    from goldspec.conventions import Conventions

    here = Path(__file__).resolve().parent.parent / "docs/example/spec/diagrams"
    base = (here / "chapter-01-ordering.md").read_text(encoding="utf-8")
    mixed = base.replace("ch1-1-ur2 -", "ch1-1-ur02 -")

    def faults_for(conv, name):
        flows = tmp_path / name / conv.flow_dir
        flows.mkdir(parents=True)
        (flows / name).write_text(mixed.replace("ch1", conv.namespace + "1"), encoding="utf-8")
        return [p for p in check_spec_directory(tmp_path / name, conv).problems if "padded" in p]

    assert faults_for(Conventions(), "chapter-01-ordering.md"), "the fixture no longer mixes widths"
    assert faults_for(Conventions(namespace="ord", flow_glob="story-*.md"),
                      "story-01-ordering.md"), (
        "the same mixed-width series passes under a custom flow glob — the padding check is "
        "looking for ids under a prefix no project id starts with")


def test_the_library_names_what_it_judged_by(tmp_path):
    """Every fault is a statement about somebody's corpus; being handed the wrong strings is not.

    The command has named its basis on every run for exactly that reason. The library did not, so a
    caller who built a `Conventions` by hand had nothing to check it against — and one did: the
    namespace was corrected, `flow_glob` kept its default, the glob matched no file, and a corpus
    of 34 nodes was reported as declaring nothing at all. The report says what it read by now.
    """
    from goldspec import check_spec_directory
    from goldspec.conventions import Conventions

    flows = tmp_path / "diagrams"
    flows.mkdir()
    (flows / "alt-weigh-it.md").write_text("# not in the node format\n", encoding="utf-8")

    conv = Conventions(namespace="ch", flow_dir="diagrams")
    report = check_spec_directory(tmp_path, conv)

    basis = report.checked[0]
    assert "ch" in basis and "diagrams/chapter-*.md" in basis, (
        f"the report does not say what it judged by: {report.checked}")


def test_a_glob_that_matched_nothing_says_so_against_what_is_there(tmp_path):
    """`matched 0 of 7` is the sentence that ends the search; prose about shapes is not.

    The fault reads as a verdict on the corpus — *declares no subjects at all* — and the reader's
    obvious next move is to go and look at their spec. Counting what the glob matched against what
    is sitting in the directory points at the glob instead, which is where the fault actually is.
    """
    from goldspec import check_spec_directory
    from goldspec.conventions import Conventions

    flows = tmp_path / "diagrams"
    flows.mkdir()
    for name in ("alt-weigh-it.md", "spe-specify-it.md", "vie-answer-it.md"):
        (flows / name).write_text("# a chapter this glob will not match\n", encoding="utf-8")

    report = check_spec_directory(tmp_path, Conventions(namespace="ch", flow_dir="diagrams"))

    empty = [p for p in report.problems if "declares no subjects" in p]
    assert empty, report.problems
    assert "matched 0 of the 3 markdown file(s)" in empty[0], empty[0]
