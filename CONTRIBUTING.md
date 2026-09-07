# Contributing

This repository uses [Conventional Commits](https://www.conventionalcommits.org)
and semantic versioning.

Work goes into a branch with the name `feature/<name>` or `fix/<name>`. Such a
branch merges into `development`. When `development` is stable, a branch with
the name `release/vX.Y.Z` comes from it. Only fixes go into a release branch,
and that branch then merges into `main`.

## Naming

The names follow the scheme of the Linux kernel:

- A name is in lower case, with an underscore between the words.
- The name of a function starts with the name of its module, thus `matrix_add`
  and not `add_matrix`. The name of the file is the name of the module, thus
  every function of `ffitt/linalg/matrix.c` starts with `matrix_`.
- The name of a type is in lower case and ends with `_t`.
- The name of a macro is in upper case.
- A function that only its own file uses is static.

To examine the names:

```bash
python3 scripts/check_naming.py
```

## Keeping the documentation with the code

The files under [docs/api](docs/api) come from the comments in the headers,
thus the documentation and the code cannot say two different things. After a
change to a header, make the files again:

```bash
python3 scripts/api_doc.py
```

To examine that every function has a comment, that the files are current, that
no file belongs to a module that went away, that every area holds a guide, and
that no link of any Markdown file points at something that is not there:

```bash
python3 scripts/api_doc.py --check
```

## What a module says about its method

Each header carries a block that opens with `Method:`. It holds a simplified
equation of what the module works out, and the few lines that say how the
library reaches it. `scripts/api_doc.py` carries that block into
`docs/api/<module>.md` as a Method section, and the comment above it as an
Overview.

THREE RULES DECIDE WHETHER THE BLOCK IS READ AT ALL, and each was learned by
getting it wrong:

- An EMPTY LINE must stand above the block. Without one it joins the comment
  before it and is read as part of the overview.
- The block must stand ABOVE THE FIRST DECLARATION. Below it, nothing reads
  it.
- It must not be written INSIDE A MACRO THAT RUNS OVER SEVERAL LINES. A
  `#define` whose line ends in a backslash continues on the next one, and a
  block dropped between the two breaks the macro.

An equation is written indented by four spaces. One space after the two
slashes is taken away and the rest of the indent stays, thus the equation
arrives as a block of code and keeps its shape.

## Diagrams

Each module has a drawing that says how it does its work, under
`docs/diagrams/<area>/<module>.html`, beside the specification
`docs/diagrams/<area>/<module>.architecture.json`.

THE SPECIFICATION IS THE SOURCE AND THE PAGE IS THE RESULT. Neither is edited
by hand: the specification is written, and the page is delivered from it.

The pages are delivered by [archify](https://github.com/tt-a1i/archify),
which is a separate project. This repository draws with version 2.17.0-dev.1,
as `scripts/build_diagrams.py` records. Another version may draw the same
specification differently, and the script says so.

To make every page again, or to examine that each one agrees with its
specification:

```bash
ARCHIFY_HOME=/path/to/archify/archify python3 scripts/build_diagrams.py
ARCHIFY_HOME=/path/to/archify/archify python3 scripts/build_diagrams.py --check
```

A PAGE IS ACCEPTED ONLY ON A DELIVERY THAT PASSES ALL NINE ARTIFACT CHECKS
with no errors and no warnings. Anything less is not a diagram of this
library.

What a specification holds:

- A title of the shape `Inside <module>`, so that the whole set reads as one.
- `animation: trace` and about four `views`, which give the reader the
  chapters and the Play story control. Both are off unless they are asked
  for, and a diagram without them is a still picture.
- Three cards: what the module works out, how the library gets there, and
  what it costs or what will catch you.

A label may be left off a relationship when both of its nodes already say
what the wording would say. That is a choice about meaning, and not a way to
settle a complaint about geometry: never drop a label that names a direction,
an order, or a mechanism.

The validator gives an exact position for a label that overlaps something.
Those positions are ABSOLUTE, thus applying one as a relative `labelDy` moves
the label somewhere else and the complaint returns.

A DELIVERY THAT PASSES IS NOT A DIAGRAM THAT READS WELL. Open the page and
look at it. One diagram passed all nine checks with two labels sitting on top
of each other, because the validator measures a label against a route and not
against another label.

To examine that every module has a method block and a diagram, that no file
was left behind by a module that went away, and that every preview link names
a file this repository holds:

```bash
python3 scripts/check_diagrams.py
```

That check needs no archify, thus it runs on every build. Whether each page
still agrees with its specification is asked separately, with
`scripts/build_diagrams.py --check`, because answering it means delivering
the page again.

## The freeze, and what it became at 1.0.0

**From 0.17.0 to 0.19.0 this library was in a feature freeze.** It took fixes,
tests and documentation, and no new modules or public functions. That freeze
was a rehearsal, and 1.0.0 is what it was rehearsing for.

**From 1.0.0 the freeze is the CONTRACT and not a project rule.** A public
function cannot be removed, and its shape cannot change, without a major
version. That is what semantic versioning means and it is now what this
repository means by it: `major_version_zero` is false in `cz.yaml`, thus a
breaking change counts as major rather than folding into a minor.

Adding a function is a MINOR version and is welcome. Taking one away, or
changing what one does, is a MAJOR version and needs a reason a caller would
accept.

The freeze is not a note in a file. `scripts/check_freeze.py` counts the public
functions in every header and compares them against the counts recorded, and it
runs as its own job in the workflow. Adding a function fails the build, and so
does taking one away: the check does not know which of the two is happening,
thus it stops both and asks a person to say which.

To lift it on purpose for a release, run

```bash
python3 scripts/check_freeze.py --show
```

and paste the answer into `FROZEN` in that file, so that the change is one a
reviewer can see in the diff. **Lifting it for a function that is REMOVED is a
major version**, and the diff is where that must be noticed: the counts falling
looks exactly like the counts rising until someone reads which module moved.

**What the freeze is for.** An audit before it found 96.5 percent of lines
covered and no function between nothing and sixty percent, but 21 modules that
no generated test has ever exercised. Every catch-up round on that has found
real faults. The freeze is the time to close it.

**What the freeze has closed.** Every module that is not a handful of lines now
has a file of rules that hold it to what it IS and not to what its interface
looks like. Those rules found three faults in the library: a filter that gave a
different shape for the same reading measured in volts and in millivolts, a
step for a derivative that was five thousand times worse than the width could
do, and a decomposition whose envelope stood still while it took the same
amount away again and again, so that a signal of size 3 gave a residue of a
million and a half.

**How much is covered, and why the number is 98 and not 99.** The build fails
below 98 percent of lines and below 90 percent of branches. What is left is not untested behaviour: it is the
guards against the heap giving nothing and against numbers the width cannot
hold. Reaching those needs an allocator that fails on purpose, or calls that
break what the headers say a caller may do. Covering every line a caller CAN
reach still leaves the whole below 99, thus 99 is a number the code cannot meet
while those guards stand, and taking them out to meet it would be the wrong
trade. Two of them were found to be unreachable because the caller's own check
is stricter than the guard, and those are named where they stand.

The guards against the heap giving nothing ARE now reached. `Test_heap_refusal`
asks the linker to send `malloc` and `calloc` through a pair of functions that
refuse on command, which is the only way to ask for a heap that fails. Every
allocator of the library is held to what `ffitt/core/README.md` says it must
then do.

**The branch number leaves the assertions out, and it must.** An `ASSERT`
states what the CALLER must have got right, and its failing side calls abort. A
suite that passes has by construction never taken that side. There are 964 of
them, and counted in they hold the whole at 74 percent and hide every real gap
behind a wall of branches no test could ever turn green. Left out, the number
is 91.2 and it means something: what is still uncovered is mostly the operand
combinations inside the validators, where a refusal is tested and which half of
an `&&` caused it is not.

**Rules are run over and over, not once.** A rule that passes one run has been
given a few hundred cases. The suite is run 25 times at each width before a
release, and that has found five rules whose bound was too tight to be true.
None of them was a fault in the library, and two of them corrected what the
headers claimed: how far a resampler really stops a tone at the very edge of
the band, and what a coefficient of correlation needs of a signal before it
means anything.

## Making a release

The bump command of commitizen is not in use, thus a release is made by hand.
When `development` is stable:

1. Make the release branch from `development`:

   ```bash
   git checkout development && git checkout -b release/vX.Y.Z
   ```

2. Write the entry for the new version at the top of `CHANGELOG.md`. Take the
   text of each entry from the subject of each commit since the last tag:

   ```bash
   git log --reverse --format='%s' <last tag>..HEAD
   ```

3. Change the version in the `project` command of `CMakeLists.txt` to the new
   version.

4. Commit the two files, and give the commit the message
   `docs(changelog): Add the entry for the version X.Y.Z`.

5. Only fixes go into the release branch after this point. Run the tests, the
   naming check and the documentation check again after each fix.

6. Merge the branch into `main` and into `development`, and make the tag:

   ```bash
   git checkout main && git merge --no-ff release/vX.Y.Z -m "Merge branch 'release/vX.Y.Z'"
   ```

   ```bash
   git checkout development && git merge --no-ff release/vX.Y.Z -m "Merge branch 'release/vX.Y.Z' into development"
   ```

   ```bash
   git tag -a X.Y.Z -m "X.Y.Z" main
   ```

   ```bash
   git push origin main development X.Y.Z
   ```

**Both of those are merges and neither can be a fast forward.** The release
branch is merged into two branches, thus each of them gets a merge commit of its
own and from that moment neither branch holds the other. The tags up to 0.8.0
name a plain commit and a fast forward worked then; 0.9.0 is the first that
names a merge commit, and no fast forward onto `main` has been possible since.
These steps said `--ff-only` until 0.14.0, which aborts.

**The tag names `main`.** Both branches hold the same tree at this point but they
are different commits, and every tag from 0.1.0 onwards names the commit on
`main`. Leaving the branch off tags whichever branch happens to be checked out,
which is `development` if the steps are followed in the order above.

The name of the tag holds no letter v, but the name of the branch does. The
tag 0.1.0 set that rule.

Each push runs the workflow in
[.github/workflows/tests.yml](.github/workflows/tests.yml). It runs the
documentation check, the naming check, the example check, the freeze check, the
diagram check, the unit tests, the property based tests, the build, and a build
with the warnings of the compiler switched on. Everything but the first five
runs at both widths, which makes thirteen jobs. A warning stops the workflow.