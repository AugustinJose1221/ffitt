"""Properties of the intrinsic mode functions.

The module holds no arithmetic. It holds a mode that emd has made, and it
writes modes out so that a person or a plot can read them. What can go wrong is
therefore what a reader sees: a point left out, two columns in the wrong order,
or a value that is not the one held. These rules write a mode out and read the
writing back.

The writing goes through printf, which writes to the descriptor of the process
and not to Python's own stream. The rules thus catch that descriptor for the
length of one call.
"""

import contextlib
import ctypes
import os
import sys
import tempfile

from hypothesis import given
from hypothesis import strategies as st

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import ffitt  # noqa: E402
import strategies as sp  # noqa: E402

LIBC = ctypes.CDLL(None)

# printf writes six places after the point, thus a value read back is out by at
# most half of the last of them.
WRITTEN = 0.5e-6 + 1e-12

values = sp.elements(1000.0)
sizes = st.integers(min_value=1, max_value=12)


@contextlib.contextmanager
def caught_output():
    """Catch what C writes to standard output, and give it as text after."""
    caught = {}
    LIBC.fflush(None)
    sys.stdout.flush()
    saved = os.dup(1)
    with tempfile.TemporaryFile(mode="w+b") as place:
        os.dup2(place.fileno(), 1)
        try:
            yield caught
        finally:
            LIBC.fflush(None)
            os.dup2(saved, 1)
            os.close(saved)
            place.seek(0)
            caught["text"] = place.read().decode()


@st.composite
def modes(draw, size=None):
    if size is None:
        size = draw(sizes)
    x = draw(st.lists(values, min_size=size, max_size=size))
    y = draw(st.lists(values, min_size=size, max_size=size))
    return x, y


def held(lib, x, y):
    """Give a mode that holds the given points, and the arrays behind it."""
    x_array = ffitt.float_array(x)
    y_array = ffitt.float_array(y)
    return lib.imf_static_alloc(len(x), x_array, y_array), x_array, y_array


@given(modes())
def test_a_mode_holds_the_memory_it_was_given(lib, mode):
    x, y = mode
    imf, x_array, y_array = held(lib, x, y)

    assert imf.size == len(x)
    assert not imf.dynamic_alloc
    assert ctypes.addressof(imf.x.contents) == ctypes.addressof(x_array)
    assert ctypes.addressof(imf.y.contents) == ctypes.addressof(y_array)

    # Freeing a mode that holds the caller's memory must leave that memory
    # alone, thus it is still readable and unchanged after.
    lib.imf_free(imf)
    assert list(x_array) == [sp.to_float32(value) for value in x]


@given(sizes)
def test_a_mode_from_the_heap_has_room_for_every_point(lib, size):
    imf = lib.imf_alloc(size)

    assert imf.size == size
    assert imf.dynamic_alloc
    for index in range(size):
        imf.x[index] = index
        imf.y[index] = -index
    assert [imf.y[index] for index in range(size)] == \
        [-float(index) for index in range(size)]

    lib.imf_free(imf)


@given(modes())
def test_a_mode_written_out_reads_back_as_its_points(lib, mode):
    x, y = mode
    # The two arrays are kept by name, because the mode points into them and
    # Python frees an array that nothing names.
    imf, x_array, y_array = held(lib, x, y)

    with caught_output() as caught:
        lib.imf_printf(ctypes.byref(imf), None)
    del x_array, y_array

    lines = caught["text"].splitlines()
    assert len(lines) == len(x)
    for line, want_x, want_y in zip(lines, x, y):
        read_x, read_y = (float(part) for part in line.split(", "))
        assert abs(read_x - sp.to_float32(want_x)) <= WRITTEN
        assert abs(read_y - sp.to_float32(want_y)) <= WRITTEN


@given(st.integers(min_value=1, max_value=4).flatmap(
    lambda count: st.tuples(st.just(count), sizes)).flatmap(
    lambda pair: st.tuples(st.just(pair[1]),
                           st.lists(modes(size=pair[1]), min_size=pair[0],
                                    max_size=pair[0]))))
def test_several_modes_written_out_stand_one_to_a_column(lib, case):
    size, mode_list = case

    keep = []
    imfs = (ffitt.Imf * len(mode_list))()
    for place, (x, y) in enumerate(mode_list):
        imf, x_array, y_array = held(lib, x, y)
        keep.append((x_array, y_array))
        imfs[place] = imf

    with caught_output() as caught:
        lib.imf_print_all(imfs, size, len(mode_list), None)

    # One line for each point, and one column for each mode, in the order the
    # modes were given. Only the values are written, not the places.
    lines = caught["text"].splitlines()
    assert len(lines) == size
    for index, line in enumerate(lines):
        columns = [float(part) for part in line.split(", ")]
        assert len(columns) == len(mode_list)
        for column, (_, y) in zip(columns, mode_list):
            assert abs(column - sp.to_float32(y[index])) <= WRITTEN
