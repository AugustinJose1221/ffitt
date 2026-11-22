"""Properties of the peak detection.

The rules of peakdetect_find have their own file, and the refining of a peak
against the shapes of the curve module has its own too. This one holds the
parts those two lean on: that a peak is what its definition says, that the
prominence is the one the header defines, and that the width and the refining
behave as a measurement must however the signal is drawn.
"""

import os
import sys

from hypothesis import given
from hypothesis import strategies as st

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import ffitt  # noqa: E402
import strategies as sp  # noqa: E402

signals = st.lists(sp.elements(), min_size=1, max_size=24)

# Signals drawn from a few whole numbers. Equal neighbours and flat tops are
# common in them, and the arithmetic on them is exact at both widths.
stepped = st.lists(st.integers(min_value=-4, max_value=4).map(float),
                   min_size=3, max_size=24)

parts = st.floats(min_value=0.0, max_value=1.0, width=32)


def get_peaks(lib, data):
    array = ffitt.float_array(data)
    index_buffer = ffitt.real_buffer(len(data) + 2)
    peak_buffer = ffitt.real_buffer(len(data) + 2)
    count = lib.peakdetect_get_peaks(array, index_buffer, peak_buffer,
                                     len(data))
    return ([int(index_buffer[place]) for place in range(count)],
            [peak_buffer[place] for place in range(count)])


def prominence_by_the_definition(data, peak):
    """The prominence as the header defines it, written out plainly.

    Walk out from the peak on each side until the signal rises above it or
    ends, keeping the lowest point reached. The prominence is the height of the
    peak above the higher of the two.
    """
    top = data[peak]
    bases = []
    for walk in (range(peak - 1, -1, -1), range(peak + 1, len(data))):
        lowest = top
        for index in walk:
            if data[index] > top:
                break
            lowest = min(lowest, data[index])
        bases.append(lowest)
    return top - max(bases)


@given(data=signals)
def test_every_peak_is_larger_than_the_value_on_each_side(lib, data):
    indices, values = get_peaks(lib, data)

    for index, value in zip(indices, values):
        assert 0 < index < len(data) - 1
        assert data[index] > data[index - 1]
        assert data[index] > data[index + 1]
        assert value == data[index]


@given(data=st.one_of(signals, stepped))
def test_the_peaks_are_exactly_the_places_the_definition_names(lib, data):
    data = [sp.to_float32(value) for value in data]
    indices, _ = get_peaks(lib, data)

    want = [index for index in range(1, len(data) - 1)
            if data[index] > data[index - 1] and data[index] > data[index + 1]]
    assert indices == want


@given(data=signals)
def test_the_peaks_come_in_the_order_of_the_signal(lib, data):
    indices, _ = get_peaks(lib, data)

    assert indices == sorted(indices)
    assert len(set(indices)) == len(indices)


@given(data=st.lists(sp.elements(), min_size=1, max_size=2))
def test_a_short_signal_has_no_peak(lib, data):
    # A peak needs a value on each side, thus a signal with one or two values
    # can hold no peak.
    assert get_peaks(lib, data) == ([], [])


@given(data=st.one_of(signals, stepped))
def test_the_prominence_is_the_one_the_header_defines(lib, data):
    data = [sp.to_float32(value) for value in data]
    array = ffitt.float_array(data)

    for peak in get_peaks(lib, data)[0]:
        got = lib.peakdetect_prominence(array, len(data), peak)

        # One subtraction of two values the width holds, rounded once, thus
        # the two roads agree to the last bit.
        assert got == sp.to_float32(prominence_by_the_definition(data, peak))


@given(data=st.one_of(signals, stepped), first=parts, second=parts)
def test_a_peak_is_never_narrower_further_down(lib, data, first, second):
    # Further down the level is lower, thus each edge can only move outwards
    # before the signal falls below it.
    #
    # The part is the share of the way down from the top, thus the larger part
    # is the lower level. The edges are placed between samples by a division,
    # which may round, hence the small allowance.
    data = [sp.to_float32(value) for value in data]
    array = ffitt.float_array(data)
    nearer_the_top, further_down = sorted((first, second))

    for peak in get_peaks(lib, data)[0]:
        narrow = lib.peakdetect_width(array, len(data), peak, nearer_the_top)
        wide = lib.peakdetect_width(array, len(data), peak, further_down)
        assert wide >= narrow - 1e-4


@st.composite
def hills_with_equal_feet(draw):
    """Give a hill that rises to one top and falls to the height it began at.

    The values are whole numbers, thus the level at the base, which is the top
    less the whole prominence, is exactly the height of the two feet.
    """
    rise = draw(st.lists(st.integers(min_value=1, max_value=5), min_size=1,
                         max_size=8))
    fall_steps = draw(st.lists(st.integers(min_value=1, max_value=5),
                               min_size=1, max_size=8))
    foot = draw(st.integers(min_value=-10, max_value=10))

    up = [foot]
    for step in rise:
        up.append(up[-1] + step)
    top = up[-1]

    # The way down must end at the foot, thus its steps are scaled to fit.
    total = sum(fall_steps)
    height = top - foot
    down = []
    gone = 0
    for place, step in enumerate(fall_steps):
        gone += step
        down.append(top - (height * gone) // total)
    down[-1] = foot
    # A step of nothing on the way down would make a flat stretch; take those
    # out so that the hill falls at every sample.
    falling = []
    for value in down:
        if (not falling and value < top) or (falling and value < falling[-1]):
            falling.append(value)
    if not falling or falling[-1] != foot:
        falling.append(foot)

    return [float(value) for value in up + falling], len(up) - 1


@given(hills_with_equal_feet())
def test_at_its_base_a_peak_whose_feet_never_go_lower_is_the_whole_signal(
        lib, hill):
    # The level at a part of one is the height of the higher foot. Here both
    # feet stand at it and nothing falls below it, thus neither edge is ever
    # crossed, and the width is measured from the first sample to the last.
    data, peak = hill
    array = ffitt.float_array(data)

    width = lib.peakdetect_width(array, len(data), peak, 1.0)

    assert width == float(len(data) - 1)


@st.composite
def sampled_parabolas(draw):
    """Give a parabola sampled at whole places, and where its top really is."""
    size = draw(st.integers(min_value=3, max_value=16))
    peak = draw(st.integers(min_value=1, max_value=size - 2))
    off = draw(st.floats(min_value=-0.4375, max_value=0.4375, width=32))
    height = draw(st.floats(min_value=1.0, max_value=100.0, width=32))
    bend = draw(st.floats(min_value=0.125, max_value=4.0, width=32))
    middle = peak + off
    data = [sp.to_float32(height - (bend * (index - middle) ** 2))
            for index in range(size)]
    return data, peak, middle, height


@given(sampled_parabolas())
def test_refining_a_sampled_parabola_finds_its_top(lib, case):
    # A parabola is what the refining fits, thus on a parabola it must be
    # right and not only better than rounding.
    data, peak, middle, height = case
    array = ffitt.float_array(data)

    # The answer is an offset from the sample the peak was found at.
    offset = lib.peakdetect_refine(array, len(data), peak)
    top = lib.peakdetect_refine_height(array, len(data), peak)

    share = 1e-9 if ffitt.REAL_64 else 2e-3
    assert abs((peak + offset) - middle) <= share * max(1.0, height)
    assert abs(top - height) <= share * height


@given(data=st.one_of(signals, stepped))
def test_a_refined_peak_stays_within_half_a_sample_of_where_it_was_found(
        lib, data):
    # The answer is an offset from the sample the peak was found at. The
    # fitted top of three points whose middle one is the highest lies between
    # the two halfway places either side of it, as the header says.
    data = [sp.to_float32(value) for value in data]
    array = ffitt.float_array(data)

    for peak in get_peaks(lib, data)[0]:
        offset = lib.peakdetect_refine(array, len(data), peak)
        assert -0.5 <= offset <= 0.5
