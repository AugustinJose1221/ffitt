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
    assert api_doc.DIAGRAM_INDEX_PATH in documents

    for name, path, title in api_doc.MODULES:
        expected = os.path.join(api_doc.MODULE_DIRECTORY, "%s.md" % name)
        assert expected in documents, "no file for the module %s" % name

    # Two indexes, the API and the diagrams, and one file for each module.
    assert len(documents) == len(api_doc.MODULES) + 2


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


def test_a_method_written_in_a_header_reaches_its_document():
    """A header that writes `Method:` must get a Method section.

    A method block needs an empty line above it, or it joins the block before
    it and becomes part of the overview. That happened twice, and both times
    the block sat in the header saying nothing to anybody.
    """
    for name, path, title in api_doc.MODULES:
        if name in api_doc.HEADERS_WITHOUT_A_MODULE:
            continue

        with open(os.path.join(api_doc.REPOSITORY, path), encoding="utf-8") as handle:
            text = handle.read()

        if "// Method:" not in text:
            continue

        document = api_doc.build_module_document(name, path, title)
        assert "## Method" in document, (
            "%s writes a method block that never reaches its document; "
            "an empty line above it is what that needs" % name)


def test_the_preview_branch_holds_the_diagrams():
    """The branch the link names must be one that actually holds the files.

    main was named first and holds no diagram at all until a release, thus
    every link written that way gave nothing. This holds the branch to one
    that has them.
    """
    import subprocess

    links = api_doc.diagram_links("fft")
    assert "/blob/%s/" % api_doc.PREVIEW_BRANCH in links

    listing = subprocess.run(
        ["git", "ls-tree", "-r", "--name-only", api_doc.PREVIEW_BRANCH],
        cwd=api_doc.REPOSITORY, capture_output=True, text=True)
    if listing.returncode != 0:
        return  # no such branch here, which a shallow clone can give

    assert "docs/diagrams/" in listing.stdout, (
        "the branch %s holds no diagram, thus every preview link is dead"
        % api_doc.PREVIEW_BRANCH)


def test_the_diagram_index_lists_every_module():
    """Every module must stand in the index, drawn or not yet drawn."""
    page = api_doc.build_diagram_index()

    for name, path, _ in api_doc.MODULES:
        if name in api_doc.HEADERS_WITHOUT_A_MODULE:
            continue
        assert "[`%s`](api/%s.md)" % (name, name) in page, (
            "%s is missing from the diagram index" % name)


def test_the_diagram_index_counts_what_is_really_there():
    """The count at the top must be the number of diagrams on disk."""
    page = api_doc.build_diagram_index()

    drawn = sum(1 for name, _, _ in api_doc.MODULES
                if api_doc.diagram_of(name) is not None)
    known = sum(1 for name, _, _ in api_doc.MODULES
                if api_doc.area_of(name) is not None)

    assert "%d of the %d modules have a diagram." % (drawn, known) in page


def test_a_module_with_no_diagram_says_so_rather_than_linking_nowhere():
    """A row with no diagram must not carry a link that gives nothing."""
    page = api_doc.build_diagram_index()

    for line in page.splitlines():
        if "not yet drawn" in line:
            assert "htmlpreview" not in line
            assert line.count("|") == 4, "the row must keep its three columns"


def test_a_macro_that_runs_over_lines_does_not_end_the_search():
    """A #define may continue on the next line, which begins with no mark.

    Read as it stands that line looks like a declaration and ends the search,
    thus everything the header says after such a macro is lost. kalman has
    one, and its whole method block went missing that way.
    """
    text = "\n".join([
        "#ifndef EXAMPLE_H",
        "#define EXAMPLE_H",
        "",
        "// How much memory the thing needs.",
        "#define EXAMPLE_SIZE(a, b)   ((6*(a)*(a)) + (5*(a)*(b)) \\",
        "                             + (4*(a)) + (b))",
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
    overview, method = api_doc.read_module_comment(text.splitlines())
    assert method == ["The value is the mean of the samples."]
    assert "How much memory the thing needs." in overview


def test_kalman_carries_its_method():
    """kalman has a macro that runs over two lines, and lost everything after."""
    with open(os.path.join(api_doc.REPOSITORY, "ffitt/estimate/kalman.h"),
              encoding="utf-8") as handle:
        _, method = api_doc.read_module_comment(handle.read().splitlines())

    assert method != [], "kalman writes a method block that never arrives"
    assert any("K is the whole idea" in line for line in method)


def test_code_is_not_read_as_a_link(tmp_path):
    """An equation between backticks or inside a block is not a link.

    An equation of the shape c[k](mu) was reported as a link to mu, and it
    stands inside a block of code where Markdown reads no link at all.
    """
    text = "\n".join([
        "# Example",
        "",
        "Inline: `c[k](mu)` is code.",
        "",
        "    y[n] = sum over k of c[k](mu) * x[n-k]",
        "",
        "```",
        "f[i][j](x)",
        "```",
        "",
    ])
    kept = api_doc.without_code(text)
    assert "c[k](mu)" not in kept
    assert "f[i][j](x)" not in kept


def test_a_real_broken_link_is_still_found(tmp_path, monkeypatch):
    """Taking code out must not blind the check to a link that is broken."""
    page = tmp_path / "example.md"
    page.write_text("See [the guide](guide-that-is-not-there.md).\n", encoding="utf-8")

    monkeypatch.setattr(api_doc, "REPOSITORY", str(tmp_path))
    faults = api_doc.find_links_that_point_nowhere()

    assert any("guide-that-is-not-there.md" in fault for fault in faults)


def test_a_link_that_is_there_is_not_named(tmp_path, monkeypatch):
    page = tmp_path / "example.md"
    page.write_text("See [the guide](guide.md).\n", encoding="utf-8")
    (tmp_path / "guide.md").write_text("# Guide\n", encoding="utf-8")

    monkeypatch.setattr(api_doc, "REPOSITORY", str(tmp_path))
    assert api_doc.find_links_that_point_nowhere() == []
