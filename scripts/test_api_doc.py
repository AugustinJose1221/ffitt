"""Tests for the documentation check.

A check that cannot find a fault has no value. These tests give the check a
header with a known fault and examine that it finds the fault.
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import api_doc  # noqa: E402


HEADER_WITH_COMMENTS = """#ifndef EXAMPLE_H
#define EXAMPLE_H

// The largest order that the module takes.
#define EXAMPLE_MAX_ORDER   16

// A thing with a size.
typedef struct{
    uint32_t size;
}example_t;

// Give a new thing of the given size.
example_t example_alloc(uint32_t size);

// Release the memory of the thing.
void example_free(example_t* thing);

#endif//EXAMPLE_H
"""

HEADER_WITHOUT_A_COMMENT = """#ifndef EXAMPLE_H
#define EXAMPLE_H

// Give a new thing of the given size.
example_t example_alloc(uint32_t size);

void example_free(example_t* thing);

#endif//EXAMPLE_H
"""


def read(tmp_path, text):
    path = tmp_path / "example.h"
    path.write_text(text)
    return api_doc.read_header(str(path))


def test_the_check_reads_every_function(tmp_path):
    types, macros, functions = read(tmp_path, HEADER_WITH_COMMENTS)
    names = [name for name, _, _ in functions]
    assert names == ["example_alloc", "example_free"]


def test_the_check_reads_the_comment_of_each_function(tmp_path):
    _, _, functions = read(tmp_path, HEADER_WITH_COMMENTS)
    comments = {name: comment for name, _, comment in functions}
    assert comments["example_alloc"] == ["Give a new thing of the given size."]
    assert comments["example_free"] == ["Release the memory of the thing."]


def test_the_check_finds_a_function_with_no_comment(tmp_path):
    _, _, functions = read(tmp_path, HEADER_WITHOUT_A_COMMENT)
    comments = {name: comment for name, _, comment in functions}
    assert comments["example_alloc"] != []
    assert comments["example_free"] == []


def test_the_check_reads_the_types_and_the_macros(tmp_path):
    types, macros, _ = read(tmp_path, HEADER_WITH_COMMENTS)
    assert [name for name, _, _ in types] == ["example_t"]
    assert [name for name, _, _ in macros] == ["EXAMPLE_MAX_ORDER"]
    assert types[0][2] == ["A thing with a size."]
    assert macros[0][2] == ["The largest order that the module takes."]


def test_a_comment_of_another_function_does_not_count(tmp_path):
    # A blank line stands between the comment and the second function, thus
    # the comment belongs to the first function only.
    text = """#ifndef EXAMPLE_H
#define EXAMPLE_H

// Give a new thing.
example_t example_alloc(uint32_t size);

example_t example_copy(example_t* thing);

#endif//EXAMPLE_H
"""
    _, _, functions = read(tmp_path, text)
    comments = {name: comment for name, _, comment in functions}
    assert comments["example_copy"] == []


def test_every_function_of_the_repository_has_a_comment():
    assert api_doc.find_functions_without_a_comment() == []


def test_the_documentation_of_the_repository_is_current():
    assert api_doc.main(["api_doc.py", "--check"]) == 0


def test_the_program_writes_one_file_for_each_module_and_an_index():
    documents = api_doc.build_documents()

    assert api_doc.INDEX_PATH in documents

    for name, path, title in api_doc.MODULES:
        expected = os.path.join(api_doc.MODULE_DIRECTORY, "%s.md" % name)
        assert expected in documents, "no file for the module %s" % name

    # The index and one file for each module.
    assert len(documents) == len(api_doc.MODULES) + 1


def test_the_index_points_to_the_file_of_each_module():
    index = api_doc.build_index()

    for name, path, title in api_doc.MODULES:
        assert "(api/%s.md)" % name in index, "the index does not point to %s" % name


def test_the_file_of_a_module_holds_its_functions_and_no_others():
    document = api_doc.build_module_document("goertzel", "ffitt/transform/goertzel.h",
                                             "Detection of one frequency")

    assert "### `goertzel_init`" in document
    assert "### `goertzel_magnitude`" in document
    # A function of another module must not stand in this file.
    assert "matrix_alloc" not in document


def test_the_check_finds_a_file_that_belongs_to_no_module(tmp_path, monkeypatch):
    # Put a file into the directory that no module writes. The check must see
    # it, so that a module that goes away leaves no old file behind.
    directory = tmp_path / "api"
    directory.mkdir()
    (directory / "gone.md").write_text("# gone\n")

    monkeypatch.setattr(api_doc, "MODULE_DIRECTORY", str(directory))

    extra = api_doc.find_files_that_belong_to_no_module({})

    assert len(extra) == 1
    assert extra[0].endswith("gone.md")


def test_the_check_is_quiet_when_every_file_belongs_to_a_module(tmp_path, monkeypatch):
    directory = tmp_path / "api"
    directory.mkdir()
    known = directory / "matrix.md"
    known.write_text("# matrix\n")

    monkeypatch.setattr(api_doc, "MODULE_DIRECTORY", str(directory))

    assert api_doc.find_files_that_belong_to_no_module({str(known): "# matrix\n"}) == []


def test_every_area_of_the_library_holds_a_guide():
    assert api_doc.find_areas_without_a_guide() == []


def test_the_check_finds_an_area_with_no_guide(tmp_path, monkeypatch):
    # Point the program at an empty tree. Every area must then be reported,
    # thus the check would see a guide that goes away.
    monkeypatch.setattr(api_doc, "REPOSITORY", str(tmp_path))

    missing = api_doc.find_areas_without_a_guide()

    assert len(missing) == len(api_doc.AREAS)
    assert "ffitt/transform/README.md" in missing[0]


def test_every_module_belongs_to_an_area():
    for name, path, title in api_doc.MODULES:
        # The three headers of the core area hold no module of their own, thus
        # two of them stand in the area list and defs stands nowhere.
        if name == "defs":
            continue
        assert api_doc.area_of(name) is not None, "%s belongs to no area" % name


def test_a_module_with_a_diagram_gets_a_link(tmp_path, monkeypatch):
    """A module whose diagram is there is given both ways to reach it."""
    directory = tmp_path / "docs" / "diagrams" / "transform"
    directory.mkdir(parents=True)
    (directory / "example.html").write_text("<svg></svg>", encoding="utf-8")

    monkeypatch.setattr(api_doc, "REPOSITORY", str(tmp_path))
    monkeypatch.setattr(api_doc, "AREAS", [("transform", "Transforms", ["example"])])

    links = api_doc.diagram_links("example")
    assert "../diagrams/transform/example.html" in links
    assert links.count("htmlpreview.github.io") == 1
    assert "/blob/%s/" % api_doc.PREVIEW_BRANCH in links


def test_a_module_with_no_diagram_gets_no_link(tmp_path, monkeypatch):
    """A link that names a file which is not there is worse than no link."""
    monkeypatch.setattr(api_doc, "REPOSITORY", str(tmp_path))
    monkeypatch.setattr(api_doc, "AREAS", [("transform", "Transforms", ["example"])])

    assert api_doc.diagram_links("example") == ""


def test_the_preview_link_names_the_file_that_is_there():
    """The link of a real module names the real file, in the real repository."""
    links = api_doc.diagram_links("fft")
    assert links != ""

    path = os.path.join(api_doc.REPOSITORY, "docs", "diagrams", "transform", "fft.html")
    assert os.path.isfile(path)
    assert "docs/diagrams/transform/fft.html" in links


HEADER_WITH_A_METHOD = """#ifndef EXAMPLE_H
#define EXAMPLE_H

#include <stdint.h>

// The example module.
//
// It stands here to be read by the test.

// Method:
//
// The value is the mean of the samples:
//
//     y = sum over n of x[n] / count
//
// The library keeps a running total, thus each sample costs one addition.

typedef struct{
    uint32_t size;
}example_t;
"""


def test_the_overview_of_a_module_is_read():
    lines = HEADER_WITH_A_METHOD.splitlines()
    overview, _ = api_doc.read_module_comment(lines)
    assert overview[0] == "The example module."
    assert overview[-1] == "It stands here to be read by the test."


def test_the_method_of_a_module_is_read_and_keeps_its_shape():
    """An equation is written indented, and the indent must survive."""
    lines = HEADER_WITH_A_METHOD.splitlines()
    _, method = api_doc.read_module_comment(lines)
    assert method[0] == "The value is the mean of the samples:"
    assert "    y = sum over n of x[n] / count" in method
    assert method[-1].startswith("The library keeps a running total")


def test_the_method_is_not_taken_into_the_overview():
    lines = HEADER_WITH_A_METHOD.splitlines()
    overview, _ = api_doc.read_module_comment(lines)
    assert not any("mean of the samples" in line for line in overview)


def test_a_module_with_no_method_gives_none(tmp_path):
    text = HEADER_WITH_A_METHOD.split("// Method:")[0] + "typedef struct{\n    int a;\n}example_t;\n"
    overview, method = api_doc.read_module_comment(text.splitlines())
    assert overview != []
    assert method == []


def test_the_comment_of_a_declaration_is_not_read_twice():
    """A comment directly above a declaration belongs to that declaration.

    Reading it into the overview as well printed the same words twice in one
    document, once at the top and once beside the function.
    """
    text = "\n".join([
        "#ifndef EXAMPLE_H",
        "#define EXAMPLE_H",
        "",
        "// The example module.",
        "",
        "// True if the size can be used.",
        "bool example_is_valid_size(uint32_t size);",
        "",
    ])
    overview, method = api_doc.read_module_comment(text.splitlines())
    assert overview == ["The example module."]
    assert method == []
    assert not any("size can be used" in line for line in overview)


def test_no_module_says_the_same_thing_twice():
    """No line of an overview may also stand as the comment of a function."""
    for name, path, _ in api_doc.MODULES:
        full = os.path.join(api_doc.REPOSITORY, path)
        with open(full, encoding="utf-8") as handle:
            overview, _ = api_doc.read_module_comment(handle.read().splitlines())

        _, _, functions = api_doc.read_header(full)
        for function_name, _, comment in functions:
            if not comment:
                continue
            assert comment[0] not in overview, (
                "%s says the comment of %s in its overview as well"
                % (name, function_name))


def test_no_text_above_the_first_declaration_is_lost():
    """Every comment block at the top of a header must reach the document.

    It may arrive as the Overview or as the Method. The block that sits
    directly on the first declaration is left out here, because it belongs to
    that declaration: for a struct it is printed beside the type, and for an
    enum it is lost, which is the fault that issue #92 holds.
    """
    for name, path, title in api_doc.MODULES:
        if name in api_doc.HEADERS_WITHOUT_A_MODULE:
            continue

        with open(os.path.join(api_doc.REPOSITORY, path), encoding="utf-8") as handle:
            lines = handle.read().splitlines()

        document = api_doc.build_module_document(name, path, title)

        standalone = []
        pending = []
        for line in lines:
            stripped = line.strip()
            if stripped.startswith("//"):
                body = stripped[2:]
                if body.startswith(" "):
                    body = body[1:]
                pending.append(body)
                continue
            if stripped == "" or stripped.startswith("#"):
                standalone.extend(pending)
                pending = []
                continue
            # The declaration ends the search, and takes its own comment away.
            break

        for body in standalone:
            if not body.strip() or body.lower().startswith("method:"):
                continue
            assert body in document, "%s loses the line %r" % (name, body)


def test_a_module_whose_comment_sits_on_its_declaration_keeps_it():
    """Some headers put their whole description on the first declaration.

    Those modules get no Overview, because the words already stand beside the
    declaration. They must not be printed twice, and must not be lost.
    """
    name, path, title = "point2d", "ffitt/core/point2d.h", "A point on a plane"
    with open(os.path.join(api_doc.REPOSITORY, path), encoding="utf-8") as handle:
        overview, _ = api_doc.read_module_comment(handle.read().splitlines())

    assert overview == []
    document = api_doc.build_module_document(name, path, title)
    # No Overview section, because the words stand beside the type instead.
    assert "## Overview" not in document
    assert "A point on a plane." in document
