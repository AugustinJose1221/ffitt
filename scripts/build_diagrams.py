#!/usr/bin/env python3
"""Make every diagram again from the specification beside it.

Each module of the library has a drawing that says how the module does its
work. The drawing is delivered by archify, which is a separate project:

    https://github.com/tt-a1i/archify

The specification is the source and the page is the result. Neither is edited
by hand: the specification is written, and the page comes from it.

    python3 scripts/build_diagrams.py            make every page again
    python3 scripts/build_diagrams.py --check    examine, and give 1 if a page
                                                 does not agree with its
                                                 specification

Say where archify lies with ARCHIFY_HOME, or let this find it beside the
repository:

    ARCHIFY_HOME=/path/to/archify/archify python3 scripts/build_diagrams.py

A page is accepted only on a delivery that passes all nine artifact checks
with no errors and no warnings. Anything less is not a diagram of this
library.
"""

import json
import os
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import check_naming  # noqa: E402

REPOSITORY = check_naming.REPOSITORY
DIAGRAM_DIRECTORY = os.path.join(REPOSITORY, "docs", "diagrams")

# The version this repository draws with. archify is a separate project and its
# renderer changes, thus a page made by another version may differ from the one
# beside it here for no reason of ours.
ARCHIFY_VERSION = "2.17.0-dev.1"

# Where to look for archify when ARCHIFY_HOME does not say.
LIKELY_PLACES = [
    os.path.join(os.path.dirname(REPOSITORY), "archify", "archify"),
    os.path.join(REPOSITORY, "..", "archify", "archify"),
]


def find_archify():
    """Give the directory that holds bin/archify.mjs, or None."""
    named = os.environ.get("ARCHIFY_HOME")
    places = [named] if named else LIKELY_PLACES

    for place in places:
        if place and os.path.isfile(os.path.join(place, "bin", "archify.mjs")):
            return os.path.abspath(place)

    return None


def installed_version(home):
    """Give the version of the archify that was found, or None."""
    try:
        with open(os.path.join(home, "package.json"), encoding="utf-8") as handle:
            return json.load(handle).get("version")
    except (OSError, ValueError):
        return None


def specifications():
    """Give every specification under docs/diagrams, in order."""
    found = []

    for area in sorted(os.listdir(DIAGRAM_DIRECTORY)):
        directory = os.path.join(DIAGRAM_DIRECTORY, area)
        if not os.path.isdir(directory):
            continue
        for name in sorted(os.listdir(directory)):
            if name.endswith(".architecture.json"):
                found.append(os.path.join(directory, name))

    return found


def deliver(home, specification, page):
    """Deliver one page, and give the receipt that archify wrote."""
    result = subprocess.run(
        ["node", "bin/archify.mjs", "deliver", "architecture",
         specification, page, "--quality", "showcase", "--json"],
        cwd=home, capture_output=True, text=True)

    try:
        return json.loads(result.stdout)
    except ValueError:
        return {"ok": False, "error": (result.stdout + result.stderr).strip()[:400]}


def main(argv):
    check = "--check" in argv[1:]

    home = find_archify()
    if home is None:
        print("archify was not found. Say where it lies:\n")
        print("    ARCHIFY_HOME=/path/to/archify/archify python3 %s\n" % argv[0])
        print("It is at https://github.com/tt-a1i/archify, version %s."
              % ARCHIFY_VERSION)
        return 1

    found = installed_version(home)
    if found != ARCHIFY_VERSION:
        print("Warning: this repository draws with archify %s, and %s is here."
              % (ARCHIFY_VERSION, found or "an unknown version"))
        print("A page made by another version may differ for no reason of ours.\n")

    faults = []
    made = 0

    for specification in specifications():
        page = specification.replace(".architecture.json", ".html")
        relative = os.path.relpath(page, REPOSITORY)

        before = None
        if check and os.path.isfile(page):
            with open(page, "rb") as handle:
                before = handle.read()

        receipt = deliver(home, specification, page)

        if not receipt.get("ok"):
            faults.append("%s was refused: %s"
                          % (relative, str(receipt.get("error"))[:200]))
            continue

        validation = receipt.get("validation", {})
        if (validation.get("checksPassed") != validation.get("checkCount")
                or validation.get("errors") or validation.get("warnings")):
            faults.append("%s did not pass every check: %s" % (relative, validation))
            continue

        made += 1

        if check and before is not None:
            with open(page, "rb") as handle:
                if handle.read() != before:
                    faults.append("%s does not agree with its specification. "
                                  "Run scripts/build_diagrams.py." % relative)

    if faults:
        print("The diagram build found %d fault(s):\n" % len(faults))
        for line in faults:
            print("  " + line)
        return 1

    if check:
        print("Every one of the %d diagrams agrees with its specification." % made)
    else:
        print("Delivered %d diagram(s), each with nine checks and no warnings." % made)

    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
