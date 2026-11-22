"""Properties of the complex numbers.

Every operation here is two or four lines of arithmetic, and a sign written the
wrong way round in one of them is still a number that looks right. These rules
hold each operation against Python's own complex numbers, which are a second
road to the same answer, and against the rules that tie the operations to each
other: a division undoes a multiplication, and a number times its conjugate is
its size squared.
"""

import os
import sys

from hypothesis import assume, given
from hypothesis import strategies as st

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import ffitt  # noqa: E402
import strategies as sp  # noqa: E402

parts = sp.elements(100.0)
factors = sp.elements(10.0)


@st.composite
def numbers(draw):
    return (draw(parts), draw(parts))


def make(lib, pair):
    return lib.cnum_make(pair[0], pair[1])


def as_python(value):
    return complex(value.re, value.im)


def near(got, want, size):
    """Give True if two complex answers agree inside what the width keeps.

    The error of a product or a quotient follows the size of what went into
    it and not the size of the answer, thus the tolerance is scaled by that.
    """
    share = 1e-12 if ffitt.REAL_64 else 1e-5
    return abs(got - want) <= share * max(1.0, size)


@given(numbers(), numbers())
def test_a_sum_and_a_difference_are_what_python_gives(lib, a, b):
    first = complex(*a)
    second = complex(*b)

    total = as_python(lib.cnum_add(make(lib, a), make(lib, b)))
    apart = as_python(lib.cnum_subtract(make(lib, a), make(lib, b)))

    size = abs(first) + abs(second)
    assert near(total, first + second, size)
    assert near(apart, first - second, size)


@given(numbers(), numbers())
def test_a_product_is_what_python_gives(lib, a, b):
    first = complex(*a)
    second = complex(*b)

    product = as_python(lib.cnum_multiply(make(lib, a), make(lib, b)))

    assert near(product, first * second, abs(first) * abs(second))


@given(numbers(), numbers())
def test_a_product_does_not_care_which_number_comes_first(lib, a, b):
    one_way = lib.cnum_multiply(make(lib, a), make(lib, b))
    other_way = lib.cnum_multiply(make(lib, b), make(lib, a))

    # The two lines of arithmetic are the same products added in another
    # order, thus they agree to the last bit.
    assert lib.cnum_is_equal(one_way, other_way)


@given(numbers(), numbers())
def test_a_division_undoes_a_multiplication(lib, a, b):
    second = complex(*b)
    assume(abs(second) > 0.01)

    product = lib.cnum_multiply(make(lib, a), make(lib, b))
    back = as_python(lib.cnum_divide(product, make(lib, b)))

    # What goes in is a product, thus the error the division can carry follows
    # the size of that product over the divisor, which is the size of a, plus
    # what the product itself lost, times how far the divisor is from one.
    size = abs(complex(*a)) * max(1.0, abs(second), 1.0 / abs(second))
    assert near(back, complex(*a), size)


@given(numbers(), numbers())
def test_a_quotient_is_what_python_gives(lib, a, b):
    second = complex(*b)
    assume(abs(second) > 0.01)

    quotient = as_python(lib.cnum_divide(make(lib, a), make(lib, b)))
    want = complex(*a) / second

    assert near(quotient, want, abs(complex(*a)) / abs(second))


@given(numbers())
def test_a_division_by_nothing_gives_nothing(lib, a):
    # The header promises zero, not a number that is not a number, so that one
    # empty bin cannot spread through a whole calculation.
    answer = lib.cnum_divide(make(lib, a), lib.cnum_zero())

    assert lib.cnum_is_zero(answer)


@given(numbers())
def test_a_number_times_its_conjugate_is_its_size_squared(lib, a):
    value = make(lib, a)
    product = lib.cnum_multiply(value, lib.cnum_conjugate(value))
    squared = lib.cnum_magnitude_squared(value)

    # The imaginary part is a product less the same product, which is exactly
    # nothing in any width.
    assert product.im == 0.0
    assert sp.close(product.re, squared, relative=1e-6, absolute=0.0)


@given(numbers())
def test_the_size_is_the_root_of_the_size_squared(lib, a):
    value = make(lib, a)
    size = lib.cnum_magnitude(value)
    squared = lib.cnum_magnitude_squared(value)

    assert size >= 0.0
    assert sp.close(size * size, squared, relative=1e-5, absolute=1e-30)
    assert sp.close(size, abs(complex(*a)), relative=1e-6, absolute=1e-30)


@given(numbers(), numbers())
def test_the_size_of_a_product_is_the_product_of_the_sizes(lib, a, b):
    product = lib.cnum_multiply(make(lib, a), make(lib, b))
    whole = lib.cnum_magnitude(make(lib, a)) * lib.cnum_magnitude(make(lib, b))

    assert sp.close(lib.cnum_magnitude(product), whole, relative=1e-5,
                    absolute=1e-30)


@given(numbers())
def test_turning_a_sign_round_twice_gives_the_number_back(lib, a):
    value = make(lib, a)

    assert lib.cnum_is_equal(lib.cnum_conjugate(lib.cnum_conjugate(value)),
                             value)
    assert lib.cnum_is_equal(lib.cnum_negate(lib.cnum_negate(value)), value)
    assert lib.cnum_is_zero(lib.cnum_add(value, lib.cnum_negate(value)))


@given(numbers())
def test_the_parts_read_back_are_the_parts_written(lib, a):
    value = make(lib, a)

    assert lib.cnum_real(value) == sp.to_float32(a[0])
    assert lib.cnum_imaginary(value) == sp.to_float32(a[1])
    assert lib.cnum_is_equal(lib.cnum_from_real(a[0]),
                             lib.cnum_make(a[0], 0.0))


@given(numbers(), factors)
def test_scaling_is_multiplying_by_a_real_number(lib, a, factor):
    scaled = lib.cnum_scale(make(lib, a), factor)
    multiplied = lib.cnum_multiply(make(lib, a), lib.cnum_from_real(factor))

    # The multiplication adds a product of nothing to each part, which changes
    # nothing, thus the two agree exactly.
    assert scaled.re == multiplied.re
    assert scaled.im == multiplied.im


@given(numbers())
def test_one_and_nothing_do_what_one_and_nothing_do(lib, a):
    value = make(lib, a)

    assert lib.cnum_is_equal(lib.cnum_multiply(value, lib.cnum_one()), value)
    assert lib.cnum_is_equal(lib.cnum_add(value, lib.cnum_zero()), value)
    assert lib.cnum_is_zero(lib.cnum_multiply(value, lib.cnum_zero()))


@given(numbers(), st.floats(min_value=-2.0, max_value=2.0, width=32),
       st.floats(min_value=-2.0, max_value=2.0, width=32),
       st.floats(min_value=0.0, max_value=1.0, width=32))
def test_near_means_each_part_lies_within_the_tolerance(lib, a, apart_re,
                                                        apart_im, tolerance):
    # The second number is drawn close to the first, so that both answers come
    # up and the edge of the tolerance is crossed often.
    first = make(lib, a)
    second = lib.cnum_make(sp.to_float32(a[0] + apart_re),
                           sp.to_float32(a[1] + apart_im))

    # The parts are subtracted at the width of the build, thus Python must
    # round each difference the same way before it compares.
    want = ((abs(sp.to_float32(first.re - second.re))
             <= sp.to_float32(tolerance))
            and (abs(sp.to_float32(first.im - second.im))
                 <= sp.to_float32(tolerance)))

    assert lib.cnum_is_near(first, second, tolerance) == want


@given(numbers())
def test_a_number_is_near_itself_at_no_tolerance_and_equal_to_itself(lib, a):
    value = make(lib, a)

    assert lib.cnum_is_equal(value, value)
    assert lib.cnum_is_near(value, value, 0.0)
    assert lib.cnum_is_zero(value) == ((value.re == 0.0) and (value.im == 0.0))
