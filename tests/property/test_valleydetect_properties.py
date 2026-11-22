"""Properties of the valley detection.

The header says a valley is the mirror of a peak. These rules hold it to that:
turning the signal upside down must turn every valley into a peak at the same
place, as the peak detection finds it, and nothing else. A second rule holds it
against the line of the definition, written out in Python.
"""

import os
import sys

from hypothesis import given
from hypothesis import strategies as st

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import ffitt  # noqa: E402
import strategies as sp  # noqa: E402

signals = st.lists(sp.elements(), min_size=1, max_size=24)

# Signals drawn from a few whole numbers, so that equal neighbours, which is
# where a "smaller than" written as "not larger than" goes wrong, are common.
stepped = st.lists(st.integers(min_value=-3, max_value=3).map(float),
                   min_size=1, max_size=24)


def valleys(lib, data):
    array = ffitt.float_array(data)
    index_buffer = ffitt.real_buffer(len(data) + 2)
    valley_buffer = ffitt.real_buffer(len(data) + 2)
    count = lib.valleydetect_get_valley(array, index_buffer, valley_buffer,
                                        len(data))
    return ([int(index_buffer[place]) for place in range(count)],
            [valley_buffer[place] for place in range(count)])


def peaks(lib, data):
    array = ffitt.float_array(data)
    index_buffer = ffitt.real_buffer(len(data) + 2)
    peak_buffer = ffitt.real_buffer(len(data) + 2)
    count = lib.peakdetect_get_peaks(array, index_buffer, peak_buffer,
                                     len(data))
    return ([int(index_buffer[place]) for place in range(count)],
            [peak_buffer[place] for place in range(count)])


@given(data=signals)
def test_every_valley_is_smaller_than_the_value_on_each_side(lib, data):
    indices, values = valleys(lib, data)

    for index, value in zip(indices, values):
        assert 0 < index < len(data) - 1
        assert data[index] < data[index - 1]
        assert data[index] < data[index + 1]
        assert value == data[index]


@given(data=st.one_of(signals, stepped))
def test_the_valleys_are_exactly_the_places_the_definition_names(lib, data):
    data = [sp.to_float32(value) for value in data]
    indices, _ = valleys(lib, data)

    want = [index for index in range(1, len(data) - 1)
            if data[index] < data[index - 1] and data[index] < data[index + 1]]
    assert indices == want


@given(data=st.one_of(signals, stepped))
def test_a_valley_is_a_peak_of_the_signal_turned_upside_down(lib, data):
    data = [sp.to_float32(value) for value in data]
    valley_indices, valley_values = valleys(lib, data)
    peak_indices, peak_values = peaks(lib, [-value for value in data])

    assert valley_indices == peak_indices
    assert valley_values == [-value for value in peak_values]


@given(data=signals)
def test_a_point_is_never_a_peak_and_a_valley_at_the_same_time(lib, data):
    valley_set = set(valleys(lib, data)[0])
    peak_set = set(peaks(lib, data)[0])

    assert peak_set.isdisjoint(valley_set)


@given(data=st.lists(sp.elements(), min_size=1, max_size=2))
def test_a_short_signal_has_no_valley(lib, data):
    # A valley needs a value on each side, thus a signal with one or two
    # values can hold none.
    assert valleys(lib, data) == ([], [])
