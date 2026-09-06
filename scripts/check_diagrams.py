#!/usr/bin/env python3
"""Examine that every module has its method, its diagram and a link that works.

    python3 scripts/check_diagrams.py

Sixty four diagrams and sixty four method blocks are correct today, and
nothing stops the sixty fifth from being forgotten. This finds five faults:

- a module whose header writes no method block;
- a module that has no diagram;
- a diagram or a specification left behind by a module that went away;
- a specification with no page beside it, or a page with no specification;
- a preview link that names a file which is not in the repository.

WHAT THIS DOES NOT DO. It never asks whether a diagram is a good diagram. No
program can judge that. It answers only whether the file is there, whether it
has a source, and whether the link points at something real.

Whether a page still agrees with its specification is a separate question,
because answering it means delivering the page again and that needs archify.
scripts/build_diagrams.py --check answers it.
"""

import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import api_doc  # noqa: E402

REPOSITORY = api_doc.REPOSITORY
DIAGRAM_DIRECTORY = os.path.join(REPOSITORY, "docs", "diagrams")

PREVIEW_LINK = re.compile(r"\[preview\]\((?P<url>[^)]+)\)")


def modules_with_no_method():
    """Name every module whose header writes no method block."""
    faults = []

    for name, path, _ in api_doc.MODULES:
        full = os.path.join(REPOSITORY, path)
        if not os.path.isfile(full):
            continue

        with open(full, encoding="utf-8") as handle:
            _, method = api_doc.read_module_comment(handle.read().splitlines())

        if not method:
            faults.append("%s writes no method block. Its header must say what "
                          "the module works out." % name)

    return faults


def modules_with_no_diagram():
    """Name every module that has no diagram."""
    faults = []

    for name, path, _ in api_doc.MODULES:
        if not os.path.isfile(os.path.join(REPOSITORY, path)):
            continue
        if api_doc.area_of(name) is None:
            continue
        if api_doc.diagram_of(name) is None:
            faults.append("%s has no diagram under docs/diagrams." % name)

    return faults


def files_that_belong_to_no_module():
    """Name every diagram or specification of a module that went away."""
    faults = []
    known = set()

    for name, _, _ in api_doc.MODULES:
        area = api_doc.area_of(name)
        if area is None:
            continue
        known.add(os.path.join(area, "%s.html" % name))
        known.add(os.path.join(area, "%s.architecture.json" % name))

    if not os.path.isdir(DIAGRAM_DIRECTORY):
        return faults

    for area in sorted(os.listdir(DIAGRAM_DIRECTORY)):
        directory = os.path.join(DIAGRAM_DIRECTORY, area)
        if not os.path.isdir(directory):
            continue

        for name in sorted(os.listdir(directory)):
            if os.path.join(area, name) not in known:
                faults.append("docs/diagrams/%s belongs to no module any more. "
                              "Remove it." % os.path.join(area, name))

    return faults


def pages_without_a_source():
    """Name every page with no specification, and every specification with no page."""
    faults = []

    if not os.path.isdir(DIAGRAM_DIRECTORY):
        return faults

    for area in sorted(os.listdir(DIAGRAM_DIRECTORY)):
        directory = os.path.join(DIAGRAM_DIRECTORY, area)
        if not os.path.isdir(directory):
            continue

        for name in sorted(os.listdir(directory)):
            path = os.path.join(directory, name)

            if name.endswith(".html"):
                source = path[:-len(".html")] + ".architecture.json"
                if not os.path.isfile(source):
                    faults.append("docs/diagrams/%s/%s has no specification. A "
                                  "page nobody can make again is not a source."
                                  % (area, name))

            elif name.endswith(".architecture.json"):
                page = path[:-len(".architecture.json")] + ".html"
                if not os.path.isfile(page):
                    faults.append("docs/diagrams/%s/%s has no page beside it."
                                  % (area, name))

    return faults


def preview_links_that_name_nothing():
    """Name every preview link that points at a file not in the repository.

    The link goes through a service and names a branch, thus it cannot be
    followed here. What can be examined is the path inside it, which must name
    a file that this repository holds.
    """
    faults = []
    marker = "/blob/%s/" % api_doc.PREVIEW_BRANCH

    for root, directories, names in os.walk(os.path.join(REPOSITORY, "docs")):
        directories[:] = [d for d in directories if not d.startswith(".")]

        for name in sorted(names):
            if not name.endswith(".md"):
                continue

            path = os.path.join(root, name)
            with open(path, encoding="utf-8") as handle:
                text = handle.read()

            for match in PREVIEW_LINK.finditer(text):
                url = match.group("url")
                if marker not in url:
                    continue

                inside = url.split(marker, 1)[1]
                if not os.path.isfile(os.path.join(REPOSITORY, inside)):
                    faults.append("%s previews %s, which is not in the "
                                  "repository." % (os.path.relpath(path, REPOSITORY),
                                                   inside))

    return faults


def main(argv):
    faults = []
    faults.extend(modules_with_no_method())
    faults.extend(modules_with_no_diagram())
    faults.extend(files_that_belong_to_no_module())
    faults.extend(pages_without_a_source())
    faults.extend(preview_links_that_name_nothing())

    if faults:
        print("The diagram check found %d fault(s):\n" % len(faults))
        for line in faults:
            print("  " + line)
        return 1

    drawn = sum(1 for name, _, _ in api_doc.MODULES
                if api_doc.diagram_of(name) is not None)
    print("The diagram check found no fault. %d modules, each with a method "
          "and a diagram." % drawn)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
