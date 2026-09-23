"""The Python this package declares it runs on, held against what it ships (`ent6`).

The command is a single archive that imports nothing outside the standard library, so a floor
here is a promise about an adopter's machine that nothing else can keep. Read as source rather
than imported: what is being checked is which version the code *needs*, and importing it on a
runtime that has everything proves nothing about one that does not.
"""

import ast
import re
from pathlib import Path

SRC = Path(__file__).resolve().parent.parent / "src"

#: The Python version each name arrived in. A name is refused when it arrived after the floor.
#: Known to be incomplete: this narrows the work, and running the suite under the floor finishes it.
ARRIVED = {
    "tomllib": (3, 11),
    "ExceptionGroup": (3, 11),
    "BaseExceptionGroup": (3, 11),
    "StrEnum": (3, 11),
    "removeprefix": (3, 9),
    "removesuffix": (3, 9),
}


def floor() -> tuple:
    """`requires-python` out of the project's own metadata."""
    found = re.search(r'requires-python\s*=\s*">=(\d+)\.(\d+)"',
                      (SRC.parent / "pyproject.toml").read_text(encoding="utf-8"))
    assert found, "the project declares no requires-python"
    return int(found.group(1)), int(found.group(2))


def shipped() -> dict:
    """Every module the package carries, the vendored parser included — it ships, so it holds."""
    found = {str(p.relative_to(SRC)): p for p in sorted(SRC.rglob("*.py"))
             if "__pycache__" not in str(p)}
    assert len(found) > 5, f"only {len(found)} modules found — has the layout moved?"
    return found


def test_everything_shipped_parses_at_the_declared_floor():
    here = floor()
    refused = []
    for name, path in sorted(shipped().items()):
        try:
            ast.parse(path.read_text(encoding="utf-8"), feature_version=here)
        except SyntaxError as bad:
            refused.append(f"{name}:{bad.lineno} {bad.msg}")
    assert not refused, f"syntax newer than the declared floor {here}: {refused}"


def test_nothing_shipped_uses_an_api_newer_than_the_floor():
    here = floor()
    late = []
    for name, path in sorted(shipped().items()):
        text = path.read_text(encoding="utf-8")
        for node in ast.walk(ast.parse(text)):
            used = node.attr if isinstance(node, ast.Attribute) else (
                node.id if isinstance(node, ast.Name) else None)
            if isinstance(node, ast.alias):
                used = node.name.split(".")[0]
            if used in ARRIVED and ARRIVED[used] > here:
                # `tomllib` is reached through a guarded import, with the vendored copy behind it.
                if used == "tomllib" and "except ModuleNotFoundError" in text:
                    continue
                late.append(f"{name}:{getattr(node, 'lineno', '?')} {used}")
    assert not late, f"newer than the declared floor {here}: {sorted(set(late))}"


def test_the_runner_the_package_asks_for_can_be_installed_at_the_floor():
    """pytest 9 does not reach 3.9, and a floor the dependency cannot be met at is not one."""
    declared = (SRC.parent / "pyproject.toml").read_text(encoding="utf-8")
    pin = re.search(r'dependencies\s*=\s*\["pytest>=(\d+)"', declared)
    assert pin, "the package no longer pins pytest, and this test is guessing"
    if floor() < (3, 10):
        assert int(pin.group(1)) < 9, (
            f"pytest>={pin.group(1)} cannot be installed on Python {floor()[0]}.{floor()[1]}")


def test_every_vendored_licence_is_declared_as_package_data():
    """Code that ships under someone else's licence ships with it (`ado4`).

    `packages.find` collects modules and nothing else, so the notice beside a vendored parser is
    left out of the wheel while the code it covers goes in — a licence fault rather than a missing
    convenience, and invisible from the zipapp, which carries whole directories and was never
    short of it.
    """
    declared = (SRC.parent / "pyproject.toml").read_text(encoding="utf-8")
    missing = []
    for licence in sorted(SRC.rglob("_vendor/*/LICENSE")):
        owner = ".".join(licence.parent.relative_to(SRC).parts)
        if f'"{owner}"' not in declared or "LICENSE" not in declared:
            missing.append(owner)
    assert missing == [], (
        f"vendored under a licence the wheel would not carry: {missing} — name the package "
        f"under [tool.setuptools.package-data] with LICENSE among its files")
