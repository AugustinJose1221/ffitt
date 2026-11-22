"""Properties of the filter without feedback.

The design of a filter has its own file. This one holds what the filter does
with what it was given, for coefficients of any kind, against a second road
written out in Python:

    the output is the sum of the coefficients times the newest samples, which
    is a convolution;

    the gain and the turn of the phase are the size and the angle of the sum
    of the coefficients turned round the circle, which is a transform.

And it holds the promises that tie the parts together: a block is the samples
one at a time, a reset forgets everything, every design is symmetric, and a
symmetric filter holds every frequency back by the same time.
"""

import cmath
import ctypes
import math
import os
import sys

from hypothesis import assume, given, settings
from hypothesis import strategies as st

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import ffitt  # noqa: E402
import strategies as sp  # noqa: E402

REFERENCE = ctypes.byref

lengths = st.integers(min_value=1, max_value=16)
coefficient_values = sp.elements(2.0)
samples = sp.elements(10.0)
frequencies = st.floats(min_value=0.0, max_value=0.5, width=32)

# A share of the size of the sum, which is what the rounding of a sum follows.
SHARE = 1e-12 if ffitt.REAL_64 else 2e-6


@st.composite
def filters_and_signals(draw):
    length = draw(lengths)
    coefficients = draw(st.lists(coefficient_values, min_size=length,
                                 max_size=length))
    signal = draw(st.lists(samples, min_size=1, max_size=40))
    return coefficients, signal


def made(lib, coefficients):
    fir = lib.fir_alloc(len(coefficients))
    for index, value in enumerate(coefficients):
        lib.fir_set_coefficient(REFERENCE(fir), index, value)
    return fir


def response(coefficients, frequency):
    """The sum of the coefficients turned round the circle at one frequency."""
    return sum(value * cmath.exp(-2j * math.pi * frequency * index)
               for index, value in enumerate(coefficients))


@given(filters_and_signals())
def test_the_output_is_the_convolution_of_the_signal_with_the_coefficients(
        lib, case):
    coefficients, signal = case
    coefficients = [sp.to_float32(value) for value in coefficients]
    signal = [sp.to_float32(value) for value in signal]
    fir = made(lib, coefficients)

    for now in range(len(signal)):
        got = lib.fir_process_sample(REFERENCE(fir), signal[now])
        terms = [coefficients[step] * signal[now - step]
                 for step in range(len(coefficients)) if now - step >= 0]
        want = sum(terms)
        size = sum(abs(term) for term in terms)
        assert abs(got - want) <= SHARE * max(1.0, size)

    lib.fir_free(REFERENCE(fir))


@given(filters_and_signals())
def test_a_block_is_the_samples_one_at_a_time(lib, case):
    coefficients, signal = case
    one = made(lib, coefficients)
    other = made(lib, coefficients)

    each = [lib.fir_process_sample(REFERENCE(one), value) for value in signal]

    source = ffitt.float_array(signal)
    room = ffitt.real_buffer(len(signal))
    lib.fir_process_block(REFERENCE(other), source, room, len(signal))

    # The block calls the same arithmetic in the same order, thus the two
    # agree to the last bit.
    assert list(room) == each

    lib.fir_free(REFERENCE(one))
    lib.fir_free(REFERENCE(other))


@given(filters_and_signals())
def test_a_block_filtered_into_itself_is_the_same_as_into_another(lib, case):
    coefficients, signal = case
    one = made(lib, coefficients)
    other = made(lib, coefficients)

    source = ffitt.float_array(signal)
    room = ffitt.real_buffer(len(signal))
    lib.fir_process_block(REFERENCE(one), source, room, len(signal))

    same = ffitt.float_array(signal)
    lib.fir_process_block(REFERENCE(other), same, same, len(signal))

    assert list(same) == list(room)

    lib.fir_free(REFERENCE(one))
    lib.fir_free(REFERENCE(other))


@given(filters_and_signals(), st.lists(samples, min_size=1, max_size=20))
def test_after_a_reset_the_filter_answers_as_it_did_when_new(lib, case,
                                                             before):
    coefficients, signal = case
    fir = made(lib, coefficients)

    first = [lib.fir_process_sample(REFERENCE(fir), value) for value in signal]
    for value in before:
        lib.fir_process_sample(REFERENCE(fir), value)
    lib.fir_reset(REFERENCE(fir))
    again = [lib.fir_process_sample(REFERENCE(fir), value) for value in signal]

    assert again == first

    lib.fir_free(REFERENCE(fir))


@given(filters_and_signals(), frequencies)
def test_the_gain_and_the_phase_are_the_size_and_the_angle_of_the_transform(
        lib, case, frequency):
    coefficients, _ = case
    coefficients = [sp.to_float32(value) for value in coefficients]
    frequency = sp.to_float32(frequency)
    fir = made(lib, coefficients)

    want = response(coefficients, frequency)
    size = sum(abs(value) for value in coefficients)

    gain = lib.fir_get_gain(REFERENCE(fir), frequency)
    assert abs(gain - abs(want)) <= 4.0 * SHARE * max(1.0, size) \
        + (1e-5 if not ffitt.REAL_64 else 1e-11) * size

    # Where the answer is nearly nothing its angle means nothing, and a small
    # error in either part turns it a long way.
    if abs(want) > 0.01 * max(1.0, size):
        phase = lib.fir_phase(REFERENCE(fir), frequency)
        turned = cmath.phase(cmath.exp(1j * (phase - cmath.phase(want))))
        assert abs(turned) <= 1e-3 if not ffitt.REAL_64 else abs(turned) <= 1e-8

    lib.fir_free(REFERENCE(fir))


@given(filters_and_signals())
def test_a_filter_is_symmetric_when_its_coefficients_read_the_same_backwards(
        lib, case):
    coefficients, _ = case
    coefficients = [sp.to_float32(value) for value in coefficients]

    # Half the time the list is made to read the same both ways, so that both
    # answers come up.
    mirrored = coefficients[:(len(coefficients) + 1) // 2]
    mirrored = mirrored + mirrored[:len(coefficients) // 2][::-1]

    # Two coefficients count as the same within a hundred steps of the last
    # digit of the largest of them, because the designs work the two ends out
    # by different roads. A difference close to that border could fall either
    # way by rounding, thus those lists are left out.
    step = (2.0 ** -52) if ffitt.REAL_64 else (2.0 ** -23)
    for kind in (coefficients, mirrored):
        room = 100.0 * step * max(abs(value) for value in kind)
        apart = [abs(kind[index] - kind[-1 - index])
                 for index in range(len(kind) // 2)]
        assume(all(not (0.5 * room < gap <= 2.0 * room + 1e-30)
                   for gap in apart))
        fir = made(lib, kind)
        want = all(gap <= room + 1e-30 for gap in apart)
        assert lib.fir_is_symmetric(REFERENCE(fir)) == want
        lib.fir_free(REFERENCE(fir))


@settings(max_examples=60)
@given(st.sampled_from(ffitt.WINDOWS_WITHOUT_A_PARAMETER),
       st.integers(min_value=5, max_value=31).map(lambda n: n | 1),
       st.floats(min_value=0.0625, max_value=0.1875, width=32),
       st.floats(min_value=0.0625, max_value=0.1875, width=32),
       st.sampled_from(["low", "high", "band pass", "band stop"]))
def test_every_design_is_symmetric_and_holds_every_frequency_back_alike(
        lib, kind, length, low, width, shape):
    high = sp.to_float32(min(0.45, low + width))
    fir = lib.fir_alloc(length)
    if shape == "low":
        made_one = lib.fir_design_low_pass_with(REFERENCE(fir), low, kind, 0.0)
    elif shape == "high":
        made_one = lib.fir_design_high_pass_with(REFERENCE(fir), low, kind,
                                                 0.0)
    elif shape == "band pass":
        made_one = lib.fir_design_band_pass_with(REFERENCE(fir), low, high,
                                                 kind, 0.0)
    else:
        made_one = lib.fir_design_band_stop_with(REFERENCE(fir), low, high,
                                                 kind, 0.0)
    assume(made_one)

    assert lib.fir_is_symmetric(REFERENCE(fir))

    # Half the length less one, at every frequency, which is what a symmetric
    # filter is for.
    for frequency in (0.01, 0.1, 0.2, 0.3, 0.45):
        delay = lib.fir_group_delay(REFERENCE(fir), frequency)
        assert abs(delay - ((length - 1) / 2.0)) <= 1e-3

    lib.fir_free(REFERENCE(fir))


@given(st.lists(coefficient_values, min_size=2, max_size=8),
       st.floats(min_value=0.03125, max_value=0.46875, width=32))
def test_the_delay_of_any_filter_is_how_fast_its_phase_turns(lib, coefficients,
                                                             frequency):
    # A filter written by hand need not be symmetric. The delay of it is then
    # worked out from the phase either side, and that must agree with the
    # slope of the angle of the transform, taken here in Python by the same
    # small step and at double width.
    coefficients = [sp.to_float32(value) for value in coefficients]
    frequency = sp.to_float32(frequency)
    fir = made(lib, coefficients)

    # A filter the library counts as symmetric takes the straight answer of
    # the rule above, thus only the others are measured here.
    if lib.fir_is_symmetric(REFERENCE(fir)):
        lib.fir_free(REFERENCE(fir))
        assume(False)

    step = 1e-3
    for place in (frequency - step, frequency, frequency + step):
        # Near a zero of the transform the phase jumps and has no slope.
        assume(abs(response(coefficients, place))
               > 0.05 * sum(abs(value) for value in coefficients))

    turned = cmath.phase(response(coefficients, frequency + step)
                         / response(coefficients, frequency - step))
    want = -turned / (2.0 * math.pi * 2.0 * step)

    got = lib.fir_group_delay(REFERENCE(fir), frequency)
    assert abs(got - want) <= 0.05 * max(1.0, abs(want))

    lib.fir_free(REFERENCE(fir))
