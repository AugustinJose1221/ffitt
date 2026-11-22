"""Properties of the filter with feedback.

The designs have their own file, which holds that each one meets what it was
asked. This one holds what the filter does with any coefficients it is given,
against a second road written out in Python:

    each section is the difference equation of the second order,
        y[n] = b0 x[n] + b1 x[n-1] + b2 x[n-2] - a1 y[n-1] - a2 y[n-2]
    and the sections follow one another;

    the gain and the turn of the phase are the size and the angle of the
    product of the sections' answers on the circle.

The library runs each section in the transposed second direct form, which is
not the form written above. The two are the same filter, thus they must agree
to the rounding of the width, and a coefficient that went to the wrong place
in either would not.

The sections are drawn with their poles inside the circle, so that every
filter drawn is stable and its output stays a number that can be compared.
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

SHARE = 1e-10 if ffitt.REAL_64 else 1e-4

samples = sp.elements(10.0)

# A coefficient is nothing, or of a size a filter really holds. One near the
# smallest number of the width squares to nothing inside the gain and the
# phase, and no design or measurement ever gives one.
coefficient_values = sp.elements(2.0).map(
    lambda value: 0.0 if abs(value) < 1e-6 else value)


@st.composite
def sections(draw):
    """Give the six coefficients of one stable section, as a caller writes them.

    The poles are a pair at a radius below one, and the coefficients are all
    multiplied by a0, which the library must divide out again.
    """
    radius = draw(st.floats(min_value=0.0, max_value=0.875, width=32))
    angle = draw(st.floats(min_value=0.0, max_value=3.125, width=32))
    a0 = draw(st.floats(min_value=0.5, max_value=2.0, width=32))
    b = [draw(coefficient_values) for _ in range(3)]
    a1 = -2.0 * radius * math.cos(angle)
    a2 = radius * radius
    return [value * a0 for value in b] + [a0, a1 * a0, a2 * a0]


@st.composite
def filters_and_signals(draw):
    count = draw(st.integers(min_value=1, max_value=3))
    chosen = [draw(sections()) for _ in range(count)]
    signal = draw(st.lists(samples, min_size=1, max_size=40))
    return chosen, signal


def made(lib, chosen):
    iir = lib.iir_alloc(len(chosen))
    for place, (b0, b1, b2, a0, a1, a2) in enumerate(chosen):
        lib.iir_set_section(REFERENCE(iir), place, b0, b1, b2, a0, a1, a2)
    return iir


def normalised(lib, iir):
    """The five coefficients of each section as the library holds them."""
    held = []
    for place in range(iir.sections):
        held.append([iir.coefficient[(place * 5) + index] for index in range(5)])
    return held


def by_the_difference_equation(held, signal):
    """Run the sections one after the other in the plain form, in Python."""
    values = list(signal)
    for b0, b1, b2, a1, a2 in held:
        x1 = x2 = y1 = y2 = 0.0
        answer = []
        for x in values:
            y = (b0 * x) + (b1 * x1) + (b2 * x2) - (a1 * y1) - (a2 * y2)
            answer.append(y)
            x2, x1 = x1, x
            y2, y1 = y1, y
        values = answer
    return values


def response(held, frequency):
    z = cmath.exp(-2j * math.pi * frequency)
    whole = 1.0
    for b0, b1, b2, a1, a2 in held:
        whole *= (b0 + (b1 * z) + (b2 * z * z)) / (1.0 + (a1 * z) + (a2 * z * z))
    return whole


def size_of(held, signal):
    """A bound on how large any value inside the filter can grow.

    The sum of the sizes of the impulse response of a stable section bounds
    how much it can make a signal larger. It is taken here over a long
    stretch of the response.
    """
    bound = max([abs(value) for value in signal] + [1.0])
    for section in held:
        impulse = by_the_difference_equation([section], [1.0] + [0.0] * 400)
        bound *= sum(abs(value) for value in impulse)
    return bound


@given(filters_and_signals())
def test_the_coefficients_are_held_divided_by_a0(lib, case):
    chosen, _ = case
    iir = made(lib, chosen)

    for given_section, held in zip(chosen, normalised(lib, iir)):
        b0, b1, b2, a0, a1, a2 = given_section
        want = [b0 / a0, b1 / a0, b2 / a0, a1 / a0, a2 / a0]
        for got, value in zip(held, want):
            assert abs(got - value) <= SHARE * max(1.0, abs(value))

    lib.iir_free(REFERENCE(iir))


@given(filters_and_signals())
def test_the_output_is_what_the_difference_equation_gives(lib, case):
    chosen, signal = case
    signal = [sp.to_float32(value) for value in signal]
    iir = made(lib, chosen)
    held = normalised(lib, iir)

    got = [lib.iir_process_sample(REFERENCE(iir), value) for value in signal]
    want = by_the_difference_equation(held, signal)

    bound = size_of(held, signal)
    for one, other in zip(got, want):
        assert abs(one - other) <= SHARE * bound

    lib.iir_free(REFERENCE(iir))


@given(filters_and_signals())
def test_a_block_is_the_samples_one_at_a_time(lib, case):
    chosen, signal = case
    one = made(lib, chosen)
    other = made(lib, chosen)

    each = [lib.iir_process_sample(REFERENCE(one), value) for value in signal]

    source = ffitt.float_array(signal)
    room = ffitt.real_buffer(len(signal))
    lib.iir_process_block(REFERENCE(other), source, room, len(signal))
    assert list(room) == each

    # And into itself, which the header allows.
    lib.iir_reset(REFERENCE(other))
    same = ffitt.float_array(signal)
    lib.iir_process_block(REFERENCE(other), same, same, len(signal))
    assert list(same) == each

    lib.iir_free(REFERENCE(one))
    lib.iir_free(REFERENCE(other))


@given(filters_and_signals(), st.lists(samples, min_size=1, max_size=20))
def test_after_a_reset_the_filter_answers_as_it_did_when_new(lib, case,
                                                             before):
    chosen, signal = case
    iir = made(lib, chosen)

    first = [lib.iir_process_sample(REFERENCE(iir), value) for value in signal]
    for value in before:
        lib.iir_process_sample(REFERENCE(iir), value)
    lib.iir_reset(REFERENCE(iir))
    again = [lib.iir_process_sample(REFERENCE(iir), value) for value in signal]

    assert again == first

    lib.iir_free(REFERENCE(iir))


@given(filters_and_signals(),
       st.floats(min_value=0.0, max_value=0.5, width=32))
def test_the_gain_and_the_phase_are_the_size_and_the_angle_of_the_answer(
        lib, case, frequency):
    chosen, _ = case
    iir = made(lib, chosen)
    held = normalised(lib, iir)

    want = response(held, frequency)
    bound = size_of(held, [1.0])

    gain = lib.iir_get_gain(REFERENCE(iir), frequency)
    assert abs(gain - abs(want)) <= SHARE * bound

    # Where the answer is nearly nothing its angle means nothing.
    if abs(want) > 0.01 * bound:
        phase = lib.iir_phase(REFERENCE(iir), frequency)
        turned = cmath.phase(cmath.exp(1j * (phase - cmath.phase(want))))
        assert abs(turned) <= (1e-8 if ffitt.REAL_64 else 1e-3)
        # Pi held at the width, which at 32 bits is a little more than pi.
        assert abs(phase) <= sp.to_float32(math.pi)

    lib.iir_free(REFERENCE(iir))


@given(filters_and_signals(),
       st.floats(min_value=0.03125, max_value=0.46875, width=32))
def test_the_delay_is_how_fast_the_phase_turns(lib, case, frequency):
    # The header calls the delay an estimate from the phase either side. It
    # is held here against the slope of the angle of the answer taken in
    # Python at double width, by a step small enough to be a slope.
    chosen, _ = case
    iir = made(lib, chosen)
    held = normalised(lib, iir)
    bound = size_of(held, [1.0])

    step = 1e-4
    for place in (frequency - 1e-3, frequency, frequency + 1e-3):
        # Near a zero of the answer the phase jumps and has no slope.
        assume(abs(response(held, place)) > 0.05 * bound)

    turned = cmath.phase(response(held, frequency + step)
                         / response(held, frequency - step))
    want = -turned / (2.0 * math.pi * 2.0 * step)

    got = lib.iir_group_delay(REFERENCE(iir), frequency)
    assert abs(got - want) <= 0.05 * max(1.0, abs(want))

    lib.iir_free(REFERENCE(iir))


@settings(max_examples=60)
@given(st.integers(min_value=1, max_value=3),
       st.floats(min_value=0.03125, max_value=0.4375, width=32),
       st.floats(min_value=1.0, max_value=20.0, width=32))
def test_a_notch_stops_its_centre_and_a_peak_passes_it_whole(lib, count,
                                                             centre, quality):
    notch = lib.iir_alloc(count)
    peak = lib.iir_alloc(count)
    assume(lib.iir_design_notch(REFERENCE(notch), centre, quality))
    assume(lib.iir_design_peak(REFERENCE(peak), centre, quality))

    assert lib.iir_get_gain(REFERENCE(notch), centre) <= 1e-3
    assert abs(lib.iir_get_gain(REFERENCE(peak), centre) - 1.0) <= 1e-3

    # Neither ever makes a frequency larger than it came in.
    for place in range(51):
        frequency = place / 100.0
        assert lib.iir_get_gain(REFERENCE(notch), frequency) <= 1.0 + 1e-3
        assert lib.iir_get_gain(REFERENCE(peak), frequency) <= 1.0 + 1e-3

    lib.iir_free(REFERENCE(notch))
    lib.iir_free(REFERENCE(peak))


@settings(max_examples=60)
@given(st.integers(min_value=1, max_value=4),
       st.floats(min_value=0.03125, max_value=0.4375, width=32))
def test_a_high_pass_stops_the_bottom_and_passes_the_top(lib, count, cutoff):
    # The low pass is held in the file of the designs. Its mirror is held
    # here, at the two ends of the band and at the cutoff itself, where a
    # Butterworth stands at one over the root of two.
    iir = lib.iir_alloc(count)
    assume(lib.iir_design_high_pass(REFERENCE(iir), cutoff))

    assert lib.iir_get_gain(REFERENCE(iir), 0.0) <= 1e-3
    assert abs(lib.iir_get_gain(REFERENCE(iir), 0.5) - 1.0) <= 1e-3
    assert abs(lib.iir_get_gain(REFERENCE(iir), cutoff)
               - (1.0 / math.sqrt(2.0))) <= 1e-2

    lib.iir_free(REFERENCE(iir))
