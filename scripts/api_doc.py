#!/usr/bin/env python3
"""Make the API documentation from the headers, and examine it.

The headers are the one place that holds the description of each function. This
program reads them and writes docs/API.md. Thus the documentation and the code
cannot say two different things.

    python3 scripts/api_doc.py            write the files under docs/
    python3 scripts/api_doc.py --check    examine, and give 1 if something is wrong

The program writes one file for each module in docs/api/, an index in
docs/API.md, and a list of the drawings in docs/DIAGRAMS.md. One file for each
module keeps each file short, and a reader who works with one module opens one
file only.

The check finds four faults:

- a function that a header declares and that has no comment above it;
- a file under docs/ that does not agree with the headers;
- a file in docs/api/ that belongs to no module any more;
- an area of the library that holds no guide.
"""

import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import check_naming  # noqa: E402

REPOSITORY = check_naming.REPOSITORY
INDEX_PATH = os.path.join(REPOSITORY, "docs", "API.md")
DIAGRAM_INDEX_PATH = os.path.join(REPOSITORY, "docs", "DIAGRAMS.md")
MODULE_DIRECTORY = os.path.join(REPOSITORY, "docs", "api")

# The order of the modules in the documentation. A reader meets the simple
# modules first and the modules that build on them later.
# The library lies under this directory.
LIBRARY_DIRECTORY = "ffitt"

# The headers that hold no module of their own. They give a type or a macro,
# and no document is made for them.
HEADERS_WITHOUT_A_MODULE = {"callback", "defs"}

MODULES = [
    ("matrix", "ffitt/linalg/matrix.h", "Matrices of float values"),
    ("cnum", "ffitt/linalg/cnum.h", "Complex numbers"),
    ("cmatrix", "ffitt/linalg/cmatrix.h", "Matrices of complex numbers"),
    ("pmatrix", "ffitt/linalg/pmatrix.h", "Matrices with a parameter"),
    ("poly", "ffitt/linalg/poly.h", "Polynomials, and where they cross nothing"),
    ("eigen", "ffitt/linalg/eigen.h", "The directions a matrix stretches"),
    ("quaternion", "ffitt/linalg/quaternion.h", "Which way something points"),
    ("lstsq", "ffitt/linalg/lstsq.h", "Fitting a curve through readings"),
    ("fft", "ffitt/transform/fft.h", "The fast Fourier transform"),
    ("bluestein", "ffitt/transform/bluestein.h", "A transform of any size"),
    ("window", "ffitt/transform/window.h", "Windows for a transform"),
    ("correlate", "ffitt/transform/correlate.h", "How alike two signals are"),
    ("convolve", "ffitt/transform/convolve.h", "Sliding one signal along another"),
    ("psd", "ffitt/transform/psd.h", "Power at each frequency"),
    ("csd", "ffitt/transform/csd.h", "What two signals have in common"),
    ("stft", "ffitt/transform/stft.h", "The transform in short pieces"),
    ("spectrogram", "ffitt/transform/spectrogram.h", "What the short pieces mean"),
    ("hilbert", "ffitt/transform/hilbert.h", "The Hilbert transform"),
    ("hht", "ffitt/transform/hht.h", "The Hilbert-Huang transform"),
    ("fir", "ffitt/filter/fir.h", "Filters with a finite impulse response"),
    ("iir", "ffitt/filter/iir.h", "Filters with an infinite impulse response"),
    ("vector", "ffitt/linalg/vector.h", "Vectors of float values"),
    ("vector2d", "ffitt/linalg/vector2d.h", "Vectors with two values"),
    ("cspline", "ffitt/interpolate/cspline.h", "Cubic splines"),
    ("interp", "ffitt/interpolate/interp.h", "Reading between the points of a table"),
    ("imf", "ffitt/decompose/imf.h", "Intrinsic mode functions"),
    ("emd", "ffitt/decompose/emd.h", "Empirical mode decomposition"),
    ("pll", "ffitt/estimate/pll.h", "Following a tone that will not stay still"),
    ("propagate", "ffitt/estimate/propagate.h", "Carrying a state forward through a rate of change"),
    ("kalman", "ffitt/estimate/kalman.h", "The Kalman filter"),
    ("ekf", "ffitt/estimate/ekf.h", "The extended Kalman filter"),
    ("ukf", "ffitt/estimate/ukf.h", "The unscented Kalman filter"),
    ("slide", "ffitt/transform/slide.h", "One frequency, answered at every sample"),
    ("goertzel", "ffitt/transform/goertzel.h", "Detection of one frequency"),
    ("cepstrum", "ffitt/transform/cepstrum.h", "Finding what repeats in a spectrum"),
    ("dct", "ffitt/transform/dct.h", "Turning a signal into cosines"),
    ("dwt", "ffitt/transform/dwt.h", "The discrete wavelet transform"),
    ("savgol", "ffitt/filter/savgol.h", "The filter of Savitzky and Golay"),
    ("movavg", "ffitt/filter/movavg.h", "The mean of the last samples"),
    ("medfilt", "ffitt/filter/medfilt.h", "The median of the last samples"),
    ("dcblock", "ffitt/filter/dcblock.h", "Taking the level of a signal away"),
    ("detrend", "ffitt/filter/detrend.h", "Taking the level and the drift out of a block"),
    ("hampel", "ffitt/filter/hampel.h", "Replacing only the samples that are wrong"),
    ("lattice", "ffitt/filter/lattice.h", "A filter built as a ladder of stages"),
    ("rls", "ffitt/filter/rls.h", "A filter that solves least squares at every sample"),
    ("adaptive", "ffitt/filter/adaptive.h", "A filter that finds its own coefficients"),
    ("resample", "ffitt/filter/resample.h", "Changing the rate of a signal"),
    ("filtfilt", "ffitt/filter/filtfilt.h", "Filtering with no delay"),
    ("farrow", "ffitt/filter/farrow.h", "Delaying by a part of a sample"),
    ("matched", "ffitt/detect/matched.h", "Looking for a known shape"),
    ("delay", "ffitt/detect/delay.h", "How far one reading stands behind another"),
    ("changepoint", "ffitt/detect/changepoint.h", "Saying when a reading has changed"),
    ("generate", "ffitt/util/generate.h", "Making the signals to test with"),
    ("curve", "ffitt/util/curve.h", "The shapes a peak can have"),
    ("quantise", "ffitt/util/quantise.h", "Putting a signal into steps"),
    ("stats", "ffitt/util/stats.h", "Measures of a list of samples"),
    ("binarysearch", "ffitt/util/binarysearch.h", "Binary search"),
    ("peakdetect", "ffitt/util/peakdetect.h", "Peak detection"),
    ("valleydetect", "ffitt/util/valleydetect.h", "Valley detection"),
    ("real", "ffitt/core/real.h", "The one type that holds every number"),
    ("nolibm", "ffitt/core/nolibm.h", "The arithmetic, without a maths library"),
    ("ringbuf", "ffitt/core/ringbuf.h", "A buffer of the last samples"),
    ("point2d", "ffitt/core/point2d.h", "A point on a plane"),
    ("callback", "ffitt/core/callback.h", "The print callback"),
]

COMMENT = re.compile(r"^\s*//\s?(.*)$")
TYPEDEF_START = re.compile(r"^\s*typedef\s+struct")
TYPEDEF_END = re.compile(r"^\s*\}\s*(?P<name>\w+)\s*;")
DEFINE = re.compile(r"^\s*#\s*define\s+(?P<name>[A-Z_][A-Z0-9_]*)")
GUARD = re.compile(r"^\s*#\s*ifndef\s+(?P<name>\w+)")
INLINE_CODE = re.compile(r"`[^`]*`")


def comment_above(lines, index):
    """Give the comment that stands directly above the given line."""
    collected = []
    position = index - 1

    while position >= 0:
        match = COMMENT.match(lines[position])
        if not match:
            break
        collected.append(match.group(1).rstrip())
        position -= 1

    collected.reverse()
    while collected and collected[0] == "":
        collected.pop(0)
    while collected and collected[-1] == "":
        collected.pop()

    return collected


def line_of_offset(text, offset):
    return text.count("\n", 0, offset)


def read_module_comment(lines):
    """Give the overview and the method that the top of a header holds.

    The overview is the first block of comment that stands above the first
    declaration. The method is the block that opens with `Method:`, and it
    holds the simplified equation of what the module works out.

    Exactly one space after the two slashes is taken away. What is left of the
    indent stays, thus an equation that is written indented reaches the
    documentation as a block of code and keeps its shape.
    """
    blocks = []
    current = []
    continued = False

    for line in lines:
        stripped = line.strip()

        # A #define whose line ends in a backslash runs on to the next one, and
        # that next line begins with none of the marks below. Read as it
        # stands it looks like a declaration and ends the search, thus
        # everything the header says after such a macro would be lost.
        if continued:
            continued = line.rstrip().endswith("\\")
            continue

        if stripped.startswith("//"):
            body = stripped[2:]
            if body.startswith(" "):
                body = body[1:]
            current.append(body)
            continue

        # An empty line and a line of the preprocessor stand between the guard,
        # the includes and the comment of the module. A declaration does not,
        # thus the first of those ends the search.
        if stripped == "" or stripped.startswith("#"):
            if current:
                blocks.append(current)
                current = []
            continued = line.rstrip().endswith("\\")
            continue

        # A comment that stands directly above a declaration, with no empty
        # line between, belongs to that declaration and not to the module.
        # comment_above reads it there, and reading it here as well would say
        # the same thing twice. Thus it is thrown away rather than kept.
        current = []
        break

    # Anything still gathered ran to the end of the file with no declaration
    # after it, thus it belongs to the module.
    if current:
        blocks.append(current)

    overview = []
    method = []
    for block in blocks:
        if block[0].lower().startswith("method:") and not method:
            rest = block[0][len("method:"):].strip()
            method = ([rest] if rest else []) + block[1:]
            continue

        # Every other block belongs to the overview, and not the first one
        # alone. A header may say more after its method block, and what it says
        # there must not be dropped.
        if overview:
            overview.append("")
        overview.extend(block)

    for block in (overview, method):
        while block and block[0] == "":
            block.pop(0)
        while block and block[-1] == "":
            block.pop()

    return overview, method


def read_header(path):
    """Give the declarations of one header with the comment of each."""
    with open(path, encoding="utf-8") as handle:
        raw = handle.read()
    lines = raw.splitlines()

    # The naming check strips the comments before it looks for a declaration.
    # Here the position in the file must stay the same, thus the strings only
    # become empty and the comments stay.
    stripped = re.sub(r'"(\\.|[^"\\])*"', '""', raw)

    types = []
    macros = []
    functions = []

    # The first #ifndef of a header is the include guard. Its #define is not a
    # part of the interface of the module, thus the documentation leaves it out.
    guard = None
    for line in lines:
        match = GUARD.match(line)
        if match:
            guard = match.group("name")
            break

    for number, line in enumerate(lines):
        match = DEFINE.match(line)
        if match and match.group("name") != guard:
            macros.append((match.group("name"), line.strip(), comment_above(lines, number)))

    start = None
    for number, line in enumerate(lines):
        if TYPEDEF_START.match(line):
            start = number
        match = TYPEDEF_END.match(line)
        if match and start is not None:
            body = lines[start:number + 1]
            types.append((match.group("name"), body, comment_above(lines, start)))
            start = None

    for match in check_naming.PROTOTYPE.finditer(stripped):
        number = line_of_offset(stripped, match.start())
        # The declaration may stand over more than one line.
        end = line_of_offset(stripped, match.end())
        declaration = " ".join(part.strip() for part in lines[number:end + 1])
        functions.append((match.group("name"), declaration.strip(),
                          comment_above(lines, number)))

    return types, macros, functions


# The areas of the library. Each one is a directory under ffitt/, and each one
# holds a README.md that says how its modules work.
AREAS = [
    ("transform", "Transforms", ["fft", "bluestein", "window", "psd", "csd",
                                 "stft", "spectrogram", "correlate",
                                 "convolve", "goertzel", "slide", "hilbert",
                                 "hht", "dwt", "dct", "cepstrum"]),
    ("filter", "Filters", ["fir", "iir", "savgol", "movavg", "medfilt",
                           "dcblock", "detrend", "hampel", "adaptive", "rls", "lattice",
                           "resample", "filtfilt", "farrow"]),
    ("estimate", "Estimation", ["kalman", "ekf", "ukf", "propagate", "pll"]),
    ("decompose", "Decomposition", ["emd", "imf"]),
    ("interpolate", "Interpolation", ["cspline", "interp"]),
    ("linalg", "Linear algebra", ["matrix", "cmatrix", "pmatrix", "cnum",
                                  "quaternion", "eigen", "poly", "lstsq",
                                  "vector",
                                  "vector2d"]),
    ("detect", "Detection", ["matched", "delay", "changepoint"]),
    ("util", "Utilities", ["generate", "curve", "quantise", "stats", "binarysearch",
                           "peakdetect", "valleydetect"]),
    ("core", "Core", ["real", "nolibm", "ringbuf", "point2d", "callback"]),
]

GENERATED_NOTE = ("This file comes from the comments in the headers. Do not change it by "
                  "hand.\nTo make it again, give:\n\n```bash\npython3 scripts/api_doc.py\n```\n")

# The diagrams lie under this directory, one for each module, in the directory
# of its area.
DIAGRAM_DIRECTORY = os.path.join("docs", "diagrams")

# A page of HTML in a repository is given to a reader as source, not as a page.
# This service fetches such a page and shows it.
#
# The link names a branch, and it names development.
#
# main was tried first, on the thought that a reader opens the documentation of
# the released library. That link is broken for as long as the diagrams are
# being made, because they reach development first and main only at a release.
# Every link written that way gave nothing at all.
#
# development always holds what main holds and usually more, thus a link that
# names it resolves at every moment. The cost is that a reader on main may be
# shown a diagram newer than the release beside it. A diagram that explains a
# method changes rarely, thus that is the cheaper of the two faults.
PREVIEW_SERVICE = "https://htmlpreview.github.io/?"
PREVIEW_REPOSITORY = "https://github.com/AugustinJose1221/ffitt"
PREVIEW_BRANCH = "development"


def diagram_of(module):
    """Give the path of the diagram of a module, or None when it has none.

    A module with no diagram gets no link. A link that names a file which is
    not there is worse than no link at all.
    """
    area = area_of(module)
    if area is None:
        return None

    path = os.path.join(DIAGRAM_DIRECTORY, area, "%s.html" % module)
    if not os.path.isfile(os.path.join(REPOSITORY, path)):
        return None

    return path


def diagram_links(module):
    """Give the markdown that points at the diagram of a module, or ''."""
    path = diagram_of(module)
    if path is None:
        return ""

    preview = "%s%s/blob/%s/%s" % (PREVIEW_SERVICE, PREVIEW_REPOSITORY,
                                   PREVIEW_BRANCH, path)
    beside = os.path.relpath(path, os.path.join("docs", "api"))

    return " | [How it works](%s) ([preview](%s))" % (beside, preview)


def area_of(module):
    """Give the area that a module belongs to, or None."""
    for area, title, names in AREAS:
        if module in names:
            return area
    return None


def module_title(name):
    for module_name, path, title in MODULES:
        if module_name == name:
            return title
    return name


def build_index():
    """Give the text of docs/API.md, which points to the file of each module."""
    known = {name for name, path, title in MODULES}
    parts = ["# API reference\n", GENERATED_NOTE]
    parts.append("Each module has its own file. Open the file of the module that you "
                 "work with.\n")
    parts.append("Each area also holds a guide that says how its modules work and "
                 "which one to\nreach for. The guide explains the method; the file "
                 "of a module gives the exact\nname and shape of every function.\n")

    for area, title, names in AREAS:
        parts.append("## %s\n" % title)
        parts.append("[How the %s modules work](../ffitt/%s/README.md)\n" % (area, area))
        parts.append("| Module | What it holds |")
        parts.append("| --- | --- |")
        for name in names:
            if name in known:
                parts.append("| [`%s`](api/%s.md) | %s |" % (name, name, module_title(name)))
        parts.append("")

    listed = {name for area, title, names in AREAS for name in names}
    rest = [name for name, path, title in MODULES if name not in listed]
    if rest:
        parts.append("## Other\n")
        parts.append("| Module | What it holds |")
        parts.append("| --- | --- |")
        for name in rest:
            parts.append("| [`%s`](api/%s.md) | %s |" % (name, name, module_title(name)))
        parts.append("")

    return "\n".join(parts).rstrip() + "\n"


def build_module_document(name, path, title):
    """Give the text of the file of one module."""
    full_path = os.path.join(REPOSITORY, path)
    types, macros, functions = read_header(full_path)
    with open(full_path, encoding="utf-8") as handle:
        overview, method = read_module_comment(handle.read().splitlines())

    parts = ["# %s\n" % name, GENERATED_NOTE]
    parts.append("%s. Declared in `%s`.\n" % (title, path))
    area = area_of(name)
    if area:
        parts.append("[Back to the index](../API.md) | "
                     "[How the %s modules work](../../ffitt/%s/README.md)%s\n"
                     % (area, area, diagram_links(name)))
    else:
        parts.append("[Back to the index](../API.md)%s\n" % diagram_links(name))

    if overview:
        parts.append("## Overview\n")
        parts.append("\n".join(overview) + "\n")

    if method:
        parts.append("## Method\n")
        parts.append("\n".join(method) + "\n")

    if macros:
        parts.append("## Macros\n")
        for macro_name, line, comment in macros:
            parts.append("### `%s`\n" % macro_name)
            parts.append("```c\n%s\n```\n" % line)
            if comment:
                parts.append("\n".join(comment) + "\n")

    if types:
        parts.append("## Types\n")
        for type_name, body, comment in types:
            parts.append("### `%s`\n" % type_name)
            if comment:
                parts.append("\n".join(comment) + "\n")
            parts.append("```c\n%s\n```\n" % "\n".join(body))

    if functions:
        parts.append("## Functions\n")
        for function_name, declaration, comment in functions:
            parts.append("### `%s`\n" % function_name)
            parts.append("```c\n%s\n```\n" % declaration)
            if comment:
                parts.append("\n".join(comment) + "\n")

    return "\n".join(parts).rstrip() + "\n"


def build_diagram_index():
    """Give the text of docs/DIAGRAMS.md, which lists every diagram there is.

    The page is made from the diagrams that are on disk, and not from a list
    that somebody keeps. A list kept by hand is wrong within a month.
    """
    note = ("This file comes from the diagrams under docs/diagrams. Do not "
            "change it by hand.\nTo make it again, give:\n\n```bash\n"
            "python3 scripts/api_doc.py\n```\n")

    parts = ["# Diagrams\n", note]
    parts.append(
        "One page for each module, showing how that module does its work. Each "
        "page holds\na few chapters that walk through it a step at a time.\n")
    parts.append(
        "**Preview** opens the page in a browser. **File** is the page itself, "
        "which a\nreader with a clone can open with no service at all.\n")

    drawn = 0
    known = 0
    body = []

    for area, area_title, names in AREAS:
        rows = []
        for name in names:
            if not any(name == module for module, _, _ in MODULES):
                continue

            known += 1
            path = diagram_of(name)
            if path is None:
                rows.append("| [`%s`](api/%s.md) | not yet drawn | |" % (name, name))
                continue

            drawn += 1
            preview = "%s%s/blob/%s/%s" % (PREVIEW_SERVICE, PREVIEW_REPOSITORY,
                                           PREVIEW_BRANCH, path)
            rows.append("| [`%s`](api/%s.md) | [preview](%s) | [%s](%s) |"
                        % (name, name, preview, os.path.basename(path),
                           os.path.relpath(path, "docs")))

        if not rows:
            continue

        body.append("## %s\n" % area_title)
        body.append("| Module | Diagram | File |")
        body.append("|---|---|---|")
        body.extend(rows)
        body.append("")

    parts.append("%d of the %d modules have a diagram.\n" % (drawn, known))
    parts.extend(body)

    return "\n".join(parts).rstrip() + "\n"


def build_documents():
    """Give a dictionary of the path of each file and the text that belongs in it."""
    documents = {INDEX_PATH: build_index(),
                 DIAGRAM_INDEX_PATH: build_diagram_index()}

    for name, path, title in MODULES:
        if not os.path.exists(os.path.join(REPOSITORY, path)):
            continue
        documents[os.path.join(MODULE_DIRECTORY, "%s.md" % name)] = \
            build_module_document(name, path, title)

    return documents


def find_areas_without_a_guide():
    """Give the areas whose directory holds no README.md."""
    missing = []

    for area, title, names in AREAS:
        guide = os.path.join(REPOSITORY, "ffitt", area, "README.md")
        if not os.path.exists(guide):
            missing.append("ffitt/%s/README.md is not there. Each area needs a "
                           "guide that says how its modules work." % area)

    return missing


def find_modules_with_no_document():
    """Name every module of the library that MODULES does not list.

    WHY THIS IS EXAMINED. MODULES is written by hand, and a module left out of
    it is simply skipped: no file is made for it, no fault is reported, and the
    check passes. The slide module was added and documented nowhere, and this
    check said all was well. The other direction - a file for a module that
    went away - was already caught; this is the half that was missing.
    """
    faults = []
    listed = {name for name, path, title in MODULES}

    for area, title, names in AREAS:
        directory = os.path.join(REPOSITORY, LIBRARY_DIRECTORY, area)

        if not os.path.isdir(directory):
            continue

        for name in sorted(os.listdir(directory)):
            if not name.endswith(".h"):
                continue

            module = name[:-2]

            if (module not in listed) and (module not in HEADERS_WITHOUT_A_MODULE):
                faults.append("the module %s/%s has no place in MODULES, thus "
                              "no documentation is made for it."
                              % (area, module))

    return faults


def find_files_that_belong_to_no_module(documents):
    """Give the files in docs/api that no module writes any more."""
    if not os.path.isdir(MODULE_DIRECTORY):
        return []

    expected = set(documents)
    extra = []

    for name in sorted(os.listdir(MODULE_DIRECTORY)):
        path = os.path.join(MODULE_DIRECTORY, name)
        if os.path.isfile(path) and path not in expected:
            extra.append(path)

    return extra


def find_functions_without_a_comment():
    faults = []
    for name, path, title in MODULES:
        full_path = os.path.join(REPOSITORY, path)
        if not os.path.exists(full_path):
            continue
        _, _, functions = read_header(full_path)
        for function_name, declaration, comment in functions:
            if not comment:
                faults.append("%s: the function '%s' has no comment above it"
                              % (path, function_name))
    return faults


# A link in a Markdown file of this repository, and where it points.
MARKDOWN_LINK = re.compile(r"\[[^\]]*\]\(([^)#]+?)(?:#[^)]*)?\)")


def without_code(text):
    """Give the text with every piece of code taken out.

    A link is a link only where Markdown reads one. Inside a fence, inside an
    indented block, or between backticks, `name[index](argument)` is code and
    means nothing. Reading those as links names faults that are not there, and
    it did: an equation of the shape c[k](mu) was reported as a link to mu.
    """
    kept = []
    fenced = False

    for line in text.split("\n"):
        if line.lstrip().startswith("```"):
            fenced = not fenced
            continue

        if fenced:
            continue

        # Four spaces at the start of a line is a block of code in Markdown.
        if line.startswith("    ") and line.strip():
            continue

        kept.append(INLINE_CODE.sub(" ", line))

    return "\n".join(kept)


def find_links_that_point_nowhere():
    """Name every link of a Markdown file that points at a file not there.

    WHY THIS IS EXAMINED. README.md was split, and the parts that moved out of
    it left a pointer behind. A pointer that names a file that is not there is
    worse than no pointer: it reads as an answer and gives none. Nothing caught
    such a link, thus a file could be moved or renamed and every pointer to it
    left broken with the build still green.

    A link that names something outside this repository is left alone; only a
    path is followed.
    """
    faults = []

    for root, directories, names in os.walk(REPOSITORY):
        directories[:] = [d for d in directories
                          if d not in ("build", "vendor", "node_modules")
                          and not d.startswith(".")]

        for name in sorted(names):
            if not name.endswith(".md"):
                continue

            path = os.path.join(root, name)

            with open(path, encoding="utf-8", errors="replace") as handle:
                text = without_code(handle.read())

            for match in MARKDOWN_LINK.finditer(text):
                target = match.group(1).strip()

                if target.startswith(("http://", "https://", "mailto:")):
                    continue

                if not os.path.exists(os.path.join(root, target)):
                    faults.append("%s points at %s, which is not there."
                                  % (os.path.relpath(path, REPOSITORY), target))

    return faults


def main(argv):
    check = "--check" in argv[1:]
    documents = build_documents()

    faults = find_functions_without_a_comment()

    faults.extend(find_areas_without_a_guide())

    faults.extend(find_modules_with_no_document())

    faults.extend(find_links_that_point_nowhere())

    for path in find_files_that_belong_to_no_module(documents):
        faults.append("%s belongs to no module any more. Remove it."
                      % os.path.relpath(path, REPOSITORY))

    if check:
        for path, text in sorted(documents.items()):
            relative = os.path.relpath(path, REPOSITORY)
            if not os.path.exists(path):
                faults.append("%s is not there. Run scripts/api_doc.py." % relative)
                continue
            with open(path, encoding="utf-8") as handle:
                if handle.read() != text:
                    faults.append("%s does not agree with the headers. "
                                  "Run scripts/api_doc.py." % relative)

        if faults:
            print("The documentation check found %d fault(s):\n" % len(faults))
            for line in faults:
                print("  " + line)
            return 1

        print("The documentation check found no fault.")
        return 0

    if faults:
        print("Warning:")
        for line in faults:
            print("  " + line)

    os.makedirs(MODULE_DIRECTORY, exist_ok=True)
    for path, text in sorted(documents.items()):
        with open(path, "w", encoding="utf-8") as handle:
            handle.write(text)

    print("Wrote %d file(s) under docs/" % len(documents))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
