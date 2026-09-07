#!/usr/bin/env python3
"""Give the diagram check a repository with a known fault, and see it found.

A check that cannot find a fault has no value. Each test here breaks one thing
and holds that the check names it.
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import api_doc          # noqa: E402
import check_diagrams   # noqa: E402


HEADER = "\n".join([
    "#ifndef EXAMPLE_H",
    "#define EXAMPLE_H",
    "",
    "// The example module.",
    "",
    "// Method:",
    "// The value is the mean of the samples.",
    "",
    "// The thing itself.",
    "typedef struct{",
    "    int a;",
    "}example_t;",
    "",
])


def build(tmp_path, monkeypatch, method=True, page=True, source=True):
    """Give a small repository with one module, broken as asked."""
    header = tmp_path / "ffitt" / "transform" / "example.h"
    header.parent.mkdir(parents=True)
    text = HEADER if method else HEADER.replace(
        "// Method:\n// The value is the mean of the samples.\n\n", "")
    header.write_text(text, encoding="utf-8")

    directory = tmp_path / "docs" / "diagrams" / "transform"
    directory.mkdir(parents=True)
    if page:
        (directory / "example.html").write_text("<svg></svg>", encoding="utf-8")
    if source:
        (directory / "example.architecture.json").write_text("{}", encoding="utf-8")

    monkeypatch.setattr(api_doc, "REPOSITORY", str(tmp_path))
    monkeypatch.setattr(check_diagrams, "REPOSITORY", str(tmp_path))
    monkeypatch.setattr(check_diagrams, "DIAGRAM_DIRECTORY",
                        str(tmp_path / "docs" / "diagrams"))
    monkeypatch.setattr(api_doc, "MODULES",
                        [("example", "ffitt/transform/example.h", "An example")])
    monkeypatch.setattr(api_doc, "AREAS",
                        [("transform", "Transforms", ["example"])])
    return tmp_path


def test_a_repository_with_nothing_wrong_gives_no_fault(tmp_path, monkeypatch):
    build(tmp_path, monkeypatch)
    assert check_diagrams.modules_with_no_method() == []
    assert check_diagrams.modules_with_no_diagram() == []
    assert check_diagrams.files_that_belong_to_no_module() == []
    assert check_diagrams.pages_without_a_source() == []


def test_a_module_with_no_method_is_found(tmp_path, monkeypatch):
    build(tmp_path, monkeypatch, method=False)
    faults = check_diagrams.modules_with_no_method()
    assert len(faults) == 1
    assert "example" in faults[0]


def test_a_module_with_no_diagram_is_found(tmp_path, monkeypatch):
    build(tmp_path, monkeypatch, page=False, source=False)
    faults = check_diagrams.modules_with_no_diagram()
    assert len(faults) == 1
    assert "example" in faults[0]


def test_a_page_with_no_specification_is_found(tmp_path, monkeypatch):
    build(tmp_path, monkeypatch, source=False)
    faults = check_diagrams.pages_without_a_source()
    assert len(faults) == 1
    assert "no specification" in faults[0]


def test_a_specification_with_no_page_is_found(tmp_path, monkeypatch):
    build(tmp_path, monkeypatch, page=False)
    faults = check_diagrams.pages_without_a_source()
    assert len(faults) == 1
    assert "no page beside it" in faults[0]


def test_a_file_of_a_module_that_went_away_is_found(tmp_path, monkeypatch):
    build(tmp_path, monkeypatch)
    left = tmp_path / "docs" / "diagrams" / "transform" / "gone.html"
    left.write_text("<svg></svg>", encoding="utf-8")

    faults = check_diagrams.files_that_belong_to_no_module()
    assert any("gone.html" in fault for fault in faults)


def test_a_preview_link_that_names_nothing_is_found(tmp_path, monkeypatch):
    build(tmp_path, monkeypatch)
    page = tmp_path / "docs" / "api"
    page.mkdir(parents=True)
    (page / "example.md").write_text(
        "[preview](https://htmlpreview.github.io/?https://github.com/a/b/blob/%s/"
        "docs/diagrams/transform/gone.html)\n" % api_doc.PREVIEW_BRANCH,
        encoding="utf-8")

    faults = check_diagrams.preview_links_that_name_nothing()
    assert len(faults) == 1
    assert "gone.html" in faults[0]


def test_a_preview_link_that_names_a_real_file_is_not_named(tmp_path, monkeypatch):
    build(tmp_path, monkeypatch)
    page = tmp_path / "docs" / "api"
    page.mkdir(parents=True)
    (page / "example.md").write_text(
        "[preview](https://htmlpreview.github.io/?https://github.com/a/b/blob/%s/"
        "docs/diagrams/transform/example.html)\n" % api_doc.PREVIEW_BRANCH,
        encoding="utf-8")

    assert check_diagrams.preview_links_that_name_nothing() == []


def test_the_real_repository_passes_every_one():
    """The library itself must hold to what this check asks."""
    assert check_diagrams.modules_with_no_method() == []
    assert check_diagrams.modules_with_no_diagram() == []
    assert check_diagrams.files_that_belong_to_no_module() == []
    assert check_diagrams.pages_without_a_source() == []
    assert check_diagrams.preview_links_that_name_nothing() == []
