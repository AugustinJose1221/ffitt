"""Properties of the functions of real.h.

Each function is one of the REAL_ macros given a name and an address, so that a
caller can hand it to something that takes a function. The danger the header
names is a function that takes a float where real_t is a double: it builds, it
runs, and its answer is nonsense. Thus the rules here hold each function
against Python's own at the width of the build. A function at the wrong width
is out by far more than these tolerances, at the first point drawn.

The rules run against the system's mathematics and, with FFITT_NO_LIBM, against
the library's own, which is why the tolerances follow the width and not the
last bit.
"""

import ctypes
import math
import os
import sys

from hypothesis import given
from hypothesis import strategies as st

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import ffitt  # noqa: E402
import strategies as sp  # noqa: E402

# A few steps of the last digit the width holds. The library's own sine is
# held at 4.2e-9 by its table, which is below a float's step and above a
# double's, thus the 64 bit share is set by that table.
SHARE = 4.2e-9 if ffitt.REAL_64 else 4.0 * (2.0 ** -23)


def between(low, high):
    # The bounds are brought to a float first, because Hypothesis takes only a
    # bound that a float can hold when it draws floats.
    narrow = ctypes.c_float
    return st.floats(min_value=narrow(low).value, max_value=narrow(high).value,
                     width=32)


def near(got, want, scale):
    return abs(got - want) <= SHARE * max(1.0, scale)


# Each function, what Python gives for it, and the range drawn from.
FUNCTIONS = [
    ("real_sin", math.sin, -100.0, 100.0),
    ("real_cos", math.cos, -100.0, 100.0),
    ("real_tan", math.tan, -1.5, 1.5),
    ("real_sqrt", math.sqrt, 0.0, 1e6),
    ("real_exp", math.exp, -20.0, 20.0),
    ("real_log", math.log, 1e-6, 1e6),
    ("real_abs", abs, -1e6, 1e6),
]


@st.composite
def a_function_and_a_point(draw):
    name, theirs, low, high = draw(st.sampled_from(FUNCTIONS))
    return name, theirs, draw(between(low, high))


@given(a_function_and_a_point())
def test_every_function_gives_what_python_gives_at_the_width(lib, case):
    name, theirs, at = case
    at = sp.to_float32(at)

    got = getattr(lib, name)(at)
    want = theirs(at)

    # An angle is only as right as the turn it is part of, and a large answer
    # carries its error as a share of itself, thus the scale is the larger of
    # the two.
    scale = max(abs(want), abs(at)) if name in ("real_sin", "real_cos") \
        else abs(want)
    assert near(got, want, scale), (name, at, got, want)


@given(between(-100.0, 100.0))
def test_the_sine_and_the_cosine_lie_on_the_circle(lib, at):
    sine = lib.real_sin(at)
    cosine = lib.real_cos(at)

    assert near((sine * sine) + (cosine * cosine), 1.0, 1.0)


@given(between(-1.5, 1.5))
def test_the_tangent_is_the_sine_over_the_cosine(lib, at):
    tangent = lib.real_tan(at)
    quotient = lib.real_sin(at) / lib.real_cos(at)

    # The cosine is small near the edge of the range, and the quotient there
    # carries the error of the cosine over its size.
    assert near(tangent, quotient, abs(tangent) / abs(lib.real_cos(at)))


@given(between(-20.0, 20.0))
def test_the_logarithm_undoes_the_exponential(lib, at):
    at = sp.to_float32(at)

    assert near(lib.real_log(lib.real_exp(at)), at, abs(at))


@given(between(0.0, 1e6))
def test_the_square_of_a_root_is_the_number(lib, at):
    at = sp.to_float32(at)
    root = lib.real_sqrt(at)

    assert root >= 0.0
    assert near(root * root, at, at)


@given(between(-1e6, 1e6))
def test_the_size_has_no_sign_and_is_exact(lib, at):
    at = sp.to_float32(at)

    assert lib.real_abs(at) == abs(at)
    assert lib.real_abs(-at) == abs(at)
