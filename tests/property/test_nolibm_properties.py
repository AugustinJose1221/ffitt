"""Properties of the library's own arithmetic.

nolibm.h gives a table: for each function, the worst relative error measured
against the system's own function, over 200000 points. The unit test walks a
fixed grid of 20000 points and asks for the same numbers. A grid finds the
worst case only where the worst case happens to lie on it.

These rules let Hypothesis LOOK for the worst case instead. It draws a point,
and where the error is larger than the table says it moves towards the point
that is worse still. If a rule here fails, the table in the header is wrong
for that function, and that is the thing to fix.

They found four such faults when they were first written: the logarithm was
out by fifteen times its claim at the edge of its range, the inverse
hyperbolic functions lost their digits near their zero, and the table had the
square root and the length of two sides a little better than they are. The
table was measured again after the fixes, and the numbers below are its
numbers.

The functions take and give a double at both widths of the build, thus these
rules are the same at 32 bits and at 64.
"""

import math
import os
import sys

import pytest

from hypothesis import assume, given
from hypothesis import strategies as st

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import ffitt  # noqa: E402


def between(low, high):
    return st.floats(min_value=low, max_value=high, allow_nan=False,
                     allow_infinity=False)


def how_far(got, want):
    """The error measured against how large the answer is, as the header does.

    Where the answer is nothing, the error is measured as it stands.
    """
    apart = abs(got - want)
    return apart / abs(want) if abs(want) > 1e-300 else apart


# Each function, the range the table was measured over, and the worst relative
# error the table gives for it. The ranges are the ones of the unit test.
TABLE = [
    ("nolibm_sqrt", math.sqrt, 1e-6, 1e6, 2.3e-16),
    ("nolibm_log", math.log, 1e-6, 1e6, 1.0e-15),
    ("nolibm_log10", math.log10, 1e-6, 1e6, 1.0e-15),
    ("nolibm_tan", math.tan, -1.5, 1.5, 2.3e-15),
    ("nolibm_acosh", math.acosh, 1.0, 100.0, 1.0e-15),
    ("nolibm_asinh", math.asinh, -100.0, 100.0, 1.0e-15),
    ("nolibm_atan", math.atan, -100.0, 100.0, 3.8e-12),
    ("nolibm_asin", math.asin, -0.999, 0.999, 3.8e-12),
    ("nolibm_exp", math.exp, -20.0, 20.0, 1.2e-11),
    ("nolibm_cosh", math.cosh, -10.0, 10.0, 1.2e-11),
    ("nolibm_sinh", math.sinh, -10.0, 10.0, 1.2e-11),
    ("nolibm_cos", math.cos, -100.0, 100.0, 4.2e-10),
    ("nolibm_sin", math.sin, -100.0, 100.0, 4.2e-9),
    ("nolibm_erf", math.erf, -4.0, 4.0, 1.5e-7),
]


# Each function is a test of its own, so that each is searched with the whole
# count of examples and not a share of it. Drawn as one, the fourteen shared
# two hundred examples between them, and two faults near zero went unseen.
@pytest.mark.parametrize("name, theirs, low, high, claim", TABLE,
                         ids=[row[0] for row in TABLE])
def test_every_function_holds_the_error_its_table_gives(lib, name, theirs,
                                                        low, high, claim):
    @given(between(low, high))
    def holds(at):
        got = getattr(lib, name)(at)
        assert how_far(got, theirs(at)) <= claim, (name, at)

    holds()


# Each function, Python's own, where its zero stands, and what its table claims.
NEAR_ZERO = [
    ("nolibm_asinh", math.asinh, 0.0, 1.0e-15),
    ("nolibm_acosh", math.acosh, 1.0, 1.0e-15),
]


@pytest.mark.parametrize("name, theirs, zero, claim", NEAR_ZERO,
                         ids=[row[0] for row in NEAR_ZERO])
def test_the_inverse_hyperbolic_functions_keep_their_digits_near_zero(
        lib, name, theirs, zero, claim):
    # Both are a logarithm of a number close to one there, and forming that
    # number plainly once lost every digit of an asinh below 1e-16. The
    # points are drawn by their exponent, because a range drawn evenly almost
    # never comes near nothing.
    @given(st.integers(min_value=-300, max_value=0),
           st.floats(min_value=1.0, max_value=9.99))
    def holds(power, digits):
        at = zero + (digits * (10.0 ** power))
        assert how_far(getattr(lib, name)(at), theirs(at)) <= claim, (name, at)

    holds()


@given(between(-100.0, 100.0))
def test_the_sine_and_the_cosine_lie_on_the_circle(lib, at):
    sine = lib.nolibm_sin(at)
    cosine = lib.nolibm_cos(at)

    # Each is right to the claim of the cosine or better, measured against
    # an answer of size one, thus the sum of the squares is right to twice it.
    assert abs((sine * sine) + (cosine * cosine) - 1.0) <= 2.0 * 4.2e-9


@given(between(-20.0, 20.0))
def test_the_logarithm_undoes_the_exponential(lib, at):
    back = lib.nolibm_log(lib.nolibm_exp(at))

    # The exponential is out by its claim, and the logarithm turns a share of
    # error in its argument into the same amount of error in its answer.
    assert abs(back - at) <= 1.2e-11 + (1.0e-15 * abs(at))


@given(between(1e-6, 1e6))
def test_the_square_of_a_root_is_the_number(lib, at):
    root = lib.nolibm_sqrt(at)

    assert how_far(root * root, at) <= 4.0 * 2.3e-16


@given(between(-1000.0, 1000.0), between(-1000.0, 1000.0))
def test_the_angle_of_a_point_is_the_angle_python_gives(lib, y, x):
    # The origin has no angle, and the header says what is given there. The
    # rule below that holds it is the next one.
    assume((y != 0.0) or (x != 0.0))

    got = lib.nolibm_atan2(y, x)
    want = math.atan2(y, x)

    # Measured against the size of a turn and not of the answer, because the
    # answer is nothing along an axis and an angle cannot be more right than
    # the turn it is part of allows.
    assert abs(got - want) <= 3.8e-12 * max(1.0, abs(want))
    assert -math.pi <= got <= math.pi


@given(between(0.001, 1000.0), st.booleans())
def test_a_zero_below_the_axis_is_below_it(lib, x, negative):
    # Minus nothing and nothing are equal, but the system reads the sign, and
    # a conjugate of a real number carries a minus nothing. Left of the origin
    # that sign decides between a half turn up and a half turn down.
    x = -x if negative else x
    assert lib.nolibm_atan2(-0.0, x) == math.atan2(-0.0, x)
    assert lib.nolibm_atan2(0.0, x) == math.atan2(0.0, x)


@given(st.sampled_from([0.0, -0.0]), st.sampled_from([0.0, -0.0]))
def test_the_origin_gives_an_angle_of_nothing(lib, y, x):
    # Here the library and the system part on purpose. The system reads the
    # sign of a zero and can answer pi; the header promises nothing at a point
    # that has no direction, so that a caller never meets half a turn there.
    assert lib.nolibm_atan2(y, x) == 0.0


@given(between(-1000.0, 1000.0), between(-1000.0, 1000.0))
def test_the_length_of_two_sides_is_the_length_python_gives(lib, x, y):
    assert how_far(lib.nolibm_hypot(x, y), math.hypot(x, y)) <= 1.0e-15


@given(between(0.01, 100.0), between(-4.0, 4.0))
def test_a_power_is_the_power_python_gives(lib, base, power):
    assert how_far(lib.nolibm_pow(base, power), base ** power) <= 1.2e-11


@given(between(-1e6, 1e6))
def test_the_whole_number_functions_are_exact(lib, at):
    assert lib.nolibm_floor(at) == math.floor(at)
    assert lib.nolibm_ceil(at) == math.ceil(at)
    assert lib.nolibm_fabs(at) == abs(at)
    assert lib.nolibm_fabs(-at) == abs(at)


@given(between(-1e4, 1e4), between(0.001, 1000.0), st.booleans())
def test_the_remainder_is_exact(lib, at, divisor, negative):
    # The remainder is worked out by doubling and halving, which is exact, and
    # the remainder of two doubles is a double that can be held exactly. Thus
    # the answer must be the system's to the last bit.
    divisor = -divisor if negative else divisor

    assert lib.nolibm_fmod(at, divisor) == math.fmod(at, divisor)
