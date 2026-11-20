# The cost tests

The headers of this library say what things cost.

- `movavg` says its work does not follow the window, and holds a table of
  measured times to show it.
- `resample` says the filtering costs the OUTPUT rate and not the input rate.
- `correlate` says the plain method wins below about 300 samples and the
  transform wins far above it.
- `convolve` says the same about a shape of about 60.
- `goertzel` says the transform costs less above about log2(n) frequencies.
- `ringbuf` says putting a sample in costs the same at any size of buffer.
- `fft` says the half road for a real signal costs about half the work of the
  plain road, forward and inverse.

Those sentences are the reason a caller picks one function over another.
Nothing held them. The benchmark beside this one MEASURES and PRINTS, thus a
claim could stop being true and the table would still be printed and the build
would still be green.

These tests measure the same things and then say whether the claim still
stands. The exit code says it too: 0 when every claim held, 1 when one did not.

## How to run them

    cmake -S . -B build -DBUILD_COST_TESTS=ON
    cmake --build build
    ./build/cost

They need no external library. They take about seven seconds.

The build type is set to Release when the caller names none. A build with no
optimisation measures the compiler and not the module.

## How a claim is held

A time measured on one machine is not the time on another. Thus a claim of two
hundred times is held at fifty, and a claim of sixty-four times is held at
five. What is tested is the SHAPE of the cost, which is what the header
promises a caller: that one way is far cheaper than the other, or that the cost
does not follow a size. A margin that wide cannot be met by accident and cannot
be missed by a busy machine.

Where the header names a crossover, the claim is held from BOTH sides. A claim
held on one side only would pass just as well for a module that was always
faster one way, which is not what the header says.

Each measurement is the FASTEST of seven runs, because the other work of the
machine can only make a run slower and never faster.

THE TWO SIDES OF A CLAIM ARE MEASURED IN TURN. Each module makes one run of
each of its measurements per round, for seven rounds, and keeps the fastest of
each. The seven runs of one side were once all made before the seven runs of
the other. The fastest of seven cannot remove a disturbance that lasts through
all seven runs of one side and not of the other, and on the build machine one
did: the plain filter ran twice as slowly for all seven of its runs, and a
ratio that measures 2.24 was reported as 1.05. Measured in turn, a lasting
disturbance falls on every side alike. Issue #95 holds the record.

Measured here over five runs at each width, the order changed the WORST spread
of any claim from 7.7 to 3.6 percent at 32 bits, and from 32.8 to 3.1 percent
at 64 bits. The typical spread did not change: it was near one or two percent
both ways. What went is the rare large disturbance, which is the one that
breaks a claim. Running every side between the runs of another leaves each
run a cache a little colder, and some ratios moved by up to seven percent;
every one stands several times clear of what it asks.

Every claim was made to fail on purpose before it was kept. The ratios were
turned round, the ring buffer was made to move its samples, and the moving mean
was replaced by the filter it exists to avoid. All twelve reported BROKEN and
the program gave 1, thus none of them is a test that cannot fail.

## What these tests found

TWO CLAIMS BROKE AT 64 BITS AND HELD AT 32, AND THE CAUSE WAS NOT THE LIBRARY'S
ARITHMETIC.

    correlate  at 4096 the transform wins by a wide margin   1.52 >= 4.00
    convolve   at a shape of 512 the transform costs far less 0.27 >= 1.50

The butterfly of the transform was written on `cnum_t`, handing a complex
number to a function and taking one back. At 32 bits that pair fits where the
compiler wants it. At 64 bits it is sixteen bytes, and what GCC 13.3 built from
it at `-O2` was more than six times SLOWER than the same code at `-O1`, with
the answers unchanged to every bit.

The butterfly is now written on the real and the imaginary parts. Measured for
one transform of 8192 points, in microseconds:

    width           on cnum_t     on the parts
    32 bit             220.9            103.5
    64 bit            2078.3            143.0

The two claims now measure 15.95 and 2.62, and all twelve hold at both widths.
The build runs this suite at 32 and at 64 bits.

NOTHING WAS WEAKENED TO GET THERE. The claims stand exactly as they were
written; it was the transform that was mended.
