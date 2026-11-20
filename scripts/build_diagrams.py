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
import shutil
import subprocess
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import check_naming  # noqa: E402

REPOSITORY = check_naming.REPOSITORY
DIAGRAM_DIRECTORY = os.path.join(REPOSITORY, "docs", "diagrams")

# What this repository draws with. archify is a separate project and its
# renderer changes, thus a page made by another version may differ from the one
# beside it here for no reason of ours.
#
# THE COMMIT IS THE PIN, AND THE VERSION IS ONLY A LABEL. A version that ends in
# -dev names no one commit: any number of them carry the same string. That was
# learned by losing the clone. A fresh one gave archify 3.2.0, a major version
# past the one the pages were drawn with, and the version string alone said
# nothing about how to get back. At this commit all 64 pages were made again and
# every one came out byte for byte the same.
ARCHIFY_VERSION = "2.17.0-dev.1"
ARCHIFY_COMMIT = "d8e4daf2610d512821365f41b139d874b29efe81"
ARCHIFY_REPOSITORY = "https://github.com/tt-a1i/archify.git"

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


def installed_commit(home):
    """Give the commit the archify that was found stands at, or None."""
    result = subprocess.run(["git", "-C", home, "rev-parse", "HEAD"],
                            capture_output=True, text=True)
    if result.returncode != 0:
        return None
    return result.stdout.strip()


def how_to_get_it():
    """Give the commands that put the right archify beside this repository."""
    beside = os.path.dirname(REPOSITORY)
    return ("    git -C %s clone %s archify\n"
            "    git -C %s checkout %s"
            % (beside, ARCHIFY_REPOSITORY,
               os.path.join(beside, "archify"), ARCHIFY_COMMIT))


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


def make_one(home, specification, scratch):
    """Deliver one page, and give a fault, or None when all is well.

    With no scratch place the page is written where it belongs. With one, the
    page is written there instead and compared with the page in the tree,
    which is left exactly as it was.
    """
    page = specification.replace(".architecture.json", ".html")
    relative = os.path.relpath(page, REPOSITORY)
    target = os.path.join(scratch, os.path.basename(page)) if scratch else page

    receipt = deliver(home, specification, target)

    if not receipt.get("ok"):
        return "%s was refused: %s" % (relative, str(receipt.get("error"))[:200])

    validation = receipt.get("validation", {})
    if (validation.get("checksPassed") != validation.get("checkCount")
            or validation.get("errors") or validation.get("warnings")):
        return "%s did not pass every check: %s" % (relative, validation)

    if scratch:
        if not os.path.isfile(page):
            return "%s is not there. Run scripts/build_diagrams.py." % relative
        with open(page, "rb") as kept, open(target, "rb") as fresh:
            if kept.read() != fresh.read():
                return ("%s does not agree with its specification. "
                        "Run scripts/build_diagrams.py." % relative)

    return None


def main(argv):
    check = "--check" in argv[1:]

    home = find_archify()
    if home is None:
        print("archify was not found. Put it beside this repository:\n")
        print(how_to_get_it())
        print("\nor say where it lies with ARCHIFY_HOME=/path/to/archify/archify.")
        return 1

    commit = installed_commit(home)
    if commit != ARCHIFY_COMMIT:
        print("Warning: this repository draws with archify at commit %s,"
              % ARCHIFY_COMMIT[:12])
        print("and the one here stands at %s, version %s."
              % ((commit or "an unknown commit")[:12],
                 installed_version(home) or "unknown"))
        print("A page made at another commit may differ for no reason of ours,")
        print("and --check then names every page. To draw as this repository does:\n")
        print(how_to_get_it())
        print()

    faults = []
    made = 0

    # A CHECK MUST NOT CHANGE WHAT IT CHECKS. It used to deliver each page onto
    # the page itself and then compare. That held only while a wrong archify
    # refused every page: one that accepted them and drew them differently
    # would have written over all 64 in the tree, ready to be committed. A
    # check therefore delivers into a place of its own and compares from there.
    # A page does not depend on where it is written, thus the bytes agree.
    scratch = tempfile.mkdtemp(prefix="ffitt-diagrams-") if check else None

    try:
        for specification in specifications():
            fault = make_one(home, specification, scratch)
            if fault:
                faults.append(fault)
            else:
                made += 1
    finally:
        if scratch:
            shutil.rmtree(scratch, ignore_errors=True)


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
