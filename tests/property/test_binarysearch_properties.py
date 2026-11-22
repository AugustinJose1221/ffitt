"""Properties of the binary search.

The search halves the list until one place is left, and a halving written one
off is the oldest fault there is: it finds the value most of the time and
misses it at an end or among equal values. These rules hold the search against
Python's own bisect, which answers the same question by another road, on lists
that hold equal values and on values outside the list.
"""

import bisect
import os
import sys

from hypothesis import given
from hypothesis import strategies as st

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import ffitt  # noqa: E402
import strategies as sp  # noqa: E402


@st.composite
def rising_data_and_value(draw):
    """Give a rising list of values and a value inside its range."""
    size = draw(st.integers(min_value=2, max_value=12))
    start = draw(st.floats(min_value=-50.0, max_value=50.0, width=32))
    steps = draw(st.lists(st.floats(min_value=0.25, max_value=8.0, width=32),
                          min_size=size - 1, max_size=size - 1))
    data = [start]
    for step in steps:
        data.append(sp.to_float32(data[-1] + step))

    position = draw(st.floats(min_value=0.0, max_value=1.0, width=32))
    value = sp.to_float32(data[0] + ((data[-1] - data[0]) * position))
    return data, value


@st.composite
def list_that_never_falls_and_value(draw):
    """Give a list that may hold the same value several times, and a value.

    The values are drawn from a few whole numbers, so that equal values are
    common and the value asked for often stands in the list, below it, or
    above it.
    """
    data = sorted(draw(st.lists(st.integers(min_value=-5, max_value=5),
                                min_size=1, max_size=16)))
    value = draw(st.integers(min_value=-7, max_value=7))
    halves = draw(st.booleans())
    value = value + 0.5 if halves else float(value)
    return [float(item) for item in data], value


@given(pair=rising_data_and_value())
def test_the_binary_search_gives_the_first_value_that_is_not_less(lib, pair):
    data, value = pair
    array = ffitt.float_array(data)

    index = lib.binarysearch_get_index(array, value, len(data))

    assert index < len(data)
    assert data[index] >= value
    if index > 0:
        assert data[index - 1] < value


@given(pair=rising_data_and_value())
def test_the_binary_search_finds_a_value_that_is_in_the_list(lib, pair):
    data, _ = pair
    array = ffitt.float_array(data)

    for position, value in enumerate(data):
        index = lib.binarysearch_get_index(array, value, len(data))
        # The values rise, thus each value comes one time only.
        assert index == position


@given(pair=list_that_never_falls_and_value())
def test_the_search_gives_what_bisect_gives_among_equal_values(lib, pair):
    data, value = pair
    array = ffitt.float_array(data)

    index = lib.binarysearch_get_index(array, value, len(data))

    # bisect gives one past the end where every value is less. The search
    # gives the last index there instead, so that it is always one that can
    # be read, and the header says so.
    want = min(bisect.bisect_left(data, value), len(data) - 1)
    assert index == want


@given(pair=list_that_never_falls_and_value())
def test_among_equal_values_the_first_of_them_is_found(lib, pair):
    data, value = pair
    array = ffitt.float_array(data)

    for position, item in enumerate(data):
        index = lib.binarysearch_get_index(array, item, len(data))
        assert data[index] == item
        assert index == data.index(item)
        assert index <= position


@given(pair=rising_data_and_value(),
       distance=st.floats(min_value=1.0, max_value=100.0, width=32))
def test_the_binary_search_gives_an_index_inside_the_list_for_any_value(lib, pair,
                                                                        distance):
    # The caller reads the list at the index that the search gives. Thus the
    # index must stay inside the list, even for a value that lies outside the
    # range of the list.
    data, _ = pair
    array = ffitt.float_array(data)

    for value in (data[0] - distance, data[-1] + distance, data[0], data[-1]):
        index = lib.binarysearch_get_index(array, sp.to_float32(value), len(data))
        assert 0 <= index < len(data)
