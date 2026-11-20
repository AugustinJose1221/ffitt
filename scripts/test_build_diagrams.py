#!/usr/bin/env python3
"""Hold what the diagram build promises, with no archify needed.

The renderer is a separate project and is not present on the build machine,
thus these tests put a stand-in where it would be called. What they hold is
what this repository decides, and not what archify draws.
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import build_diagrams  # noqa: E402


def setup(tmp_path, monkeypatch, drawn, accepted=True):
    """A repository with one specification and the page committed beside it."""
    directory = tmp_path / "docs" / "diagrams" / "core"
    directory.mkdir(parents=True)
    specification = directory / "example.architecture.json"
    specification.write_text("{}", encoding="utf-8")
    page = directory / "example.html"
    page.write_bytes(b"THE PAGE AS IT WAS COMMITTED")

    def stand_in(home, spec, target):
        if not accepted:
            return {"ok": False, "error": "refused"}
        with open(target, "wb") as handle:
            handle.write(drawn)
        return {"ok": True, "validation": {"checksPassed": 9, "checkCount": 9,
                                           "errors": 0, "warnings": 0}}

    monkeypatch.setattr(build_diagrams, "REPOSITORY", str(tmp_path))
    monkeypatch.setattr(build_diagrams, "deliver", stand_in)
    return str(specification), page


def test_a_check_never_writes_over_the_page_it_checks(tmp_path, monkeypatch):
    """The fault this test exists for.

    The check once delivered each page onto the page itself and then compared.
    A renderer that accepted a specification and drew it differently would
    have written over the committed page, ready to be committed in turn.
    """
    specification, page = setup(tmp_path, monkeypatch, b"DRAWN DIFFERENTLY")
    scratch = tmp_path / "scratch"
    scratch.mkdir()

    fault = build_diagrams.make_one("home", specification, str(scratch))

    assert fault is not None and "does not agree" in fault
    assert page.read_bytes() == b"THE PAGE AS IT WAS COMMITTED"


def test_a_check_is_quiet_when_the_page_agrees(tmp_path, monkeypatch):
    specification, page = setup(tmp_path, monkeypatch,
                                b"THE PAGE AS IT WAS COMMITTED")
    scratch = tmp_path / "scratch"
    scratch.mkdir()

    assert build_diagrams.make_one("home", specification, str(scratch)) is None
    assert page.read_bytes() == b"THE PAGE AS IT WAS COMMITTED"


def test_a_refused_page_is_named_and_left_alone(tmp_path, monkeypatch):
    specification, page = setup(tmp_path, monkeypatch, b"", accepted=False)
    scratch = tmp_path / "scratch"
    scratch.mkdir()

    fault = build_diagrams.make_one("home", specification, str(scratch))

    assert fault is not None and "refused" in fault
    assert page.read_bytes() == b"THE PAGE AS IT WAS COMMITTED"


def test_a_build_writes_the_page_where_it_belongs(tmp_path, monkeypatch):
    """Without a check, making the page again is the whole point."""
    specification, page = setup(tmp_path, monkeypatch, b"MADE AGAIN")

    assert build_diagrams.make_one("home", specification, None) is None
    assert page.read_bytes() == b"MADE AGAIN"


def test_the_pin_is_a_commit_and_not_only_a_version():
    """A version that ends in -dev names no one commit."""
    commit = build_diagrams.ARCHIFY_COMMIT
    assert len(commit) == 40
    assert all(c in "0123456789abcdef" for c in commit)


def test_the_way_back_names_the_commit():
    """Whoever lost the renderer must be told how to get the right one."""
    advice = build_diagrams.how_to_get_it()
    assert build_diagrams.ARCHIFY_COMMIT in advice
    assert "clone" in advice and "checkout" in advice


def test_a_place_that_is_not_a_checkout_gives_no_commit(tmp_path):
    assert build_diagrams.installed_commit(str(tmp_path)) is None
