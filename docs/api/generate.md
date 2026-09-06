# generate

This file comes from the comments in the headers. Do not change it by hand.
To make it again, give:

```bash
python3 scripts/api_doc.py
```

Making the signals to test with. Declared in `ffitt/util/generate.h`.

[Back to the index](../API.md) | [How the util modules work](../../ffitt/util/README.md)

## Overview

Making the signals to test with, without making the faults that come free
with them.

Every test and every example in this library used to write its own sine
wave. That is fine for a sine, and it is a trap for anything else.

WHY A SQUARE WAVE IS NOT A ROW OF ONES AND MINUS ONES

Write a square wave the obvious way, by taking the sign of a sine, and it
holds every odd harmonic of its frequency, out to infinity. A sampled signal
cannot hold anything above half the sample rate, so every harmonic above
that FOLDS BACK and lands somewhere below it. Where it lands has nothing to
do with the note being played.

Measured, a square wave at 8000 samples in a second: the loudest thing in
the answer that is NOT a harmonic of the tone, against the tone itself.

    tone Hz        100     300     700    1300    1900    3100
    samples a turn  80      27      11     6.2     4.2     2.6
    naive        -39.3   -23.9   -17.3   -13.9    -9.2    -9.2  dB
    this module  -49.3   -33.7   -29.6   -39.6   -25.7   -39.6  dB

READ THE NAIVE ROW ACROSS. The fewer samples there are to a turn, the worse
it gets, until at 1900 Hz the loudest false tone is only 9 dB below the one
that was asked for. A filter tested with that wave is being tested against a
signal nobody meant to make.

This module holds the folding between 26 and 50 dB down across the whole
range, which is 10 to 26 dB better than the naive one at every frequency.

HOW IT IS HELD DOWN

The fold comes from the corner. A square wave steps from one value to the
other between two samples, and a step between samples is a thing a sampled
signal cannot hold. The module works out WHERE BETWEEN THE TWO SAMPLES the
step really falls and smooths the corner across them by that much, which is
the method of the polynomial band-limited step.

It costs a handful of operations at each corner and nothing anywhere else,
thus a square wave costs about what the naive one costs.

IT DOES NOT REMOVE THE FOLDING ALTOGETHER, and the table above is honest
about that: the best it reaches is about 50 dB down and the worst about 26.
Nothing that runs in constant time does better. A TEST THAT NEEDS BETTER
THAN THAT WANTS A SINE, which folds nothing because it holds one frequency
and no other.

THE PHASE IS CARRIED AND NOT WORKED OUT FROM THE SAMPLE NUMBER

Working out sin(2*pi*f*n/rate) from the sample number n looks simpler and
goes wrong in two ways. The angle grows without bound, so a long run loses
its digits exactly as the bluestein module records. And a frequency that
changes cannot be written that way at all: the phase would jump every time
the frequency did.

This module carries the phase from one sample to the next and folds it into
one turn each time, thus it runs for ever without losing digits and its
frequency may be changed at any sample without a jump.

Which shape to make.

## Macros

### `GENERATE_BROWN_KEEP`

```c
#define GENERATE_BROWN_KEEP     REAL_C(0.999)
```

### `GENERATE_DEFAULT_PART`

```c
#define GENERATE_DEFAULT_PART   REAL_C(0.5)
```

The part of a turn a pulse fills, where none is given.

### `GENERATE_PINK_PARTS`

```c
#define GENERATE_PINK_PARTS     7u
```

How many running parts the pink noise is made from.

Each part changes half as often as the one before it, and together they give
a slope of about 3 dB for each doubling of frequency. Seven parts hold that
slope across about seven octaves, which covers any sample rate this library
is used at.

## Types

### `generate_t`

```c
typedef struct{
    generate_kind_t kind;       // Which shape
    real_t phase;               // Where in the turn, from 0 to 1
    real_t step;                // How far the phase moves each sample
    real_t sweep;               // How far the step moves each sample
    real_t last_step;           // What the step was, for the sweep to end on
    uint32_t seed;              // Where the random values stand
    real_t pink[GENERATE_PINK_PARTS];   // The running parts of the pink noise
    real_t part;                // The part of a turn a pulse fills
    real_t running;             // The running sum of the brown noise
    real_t last_pink;           // The pink value before this one, for the blue
    real_t spare;               // The second of a pair of normal draws
    uint32_t counted;           // How many samples have been made
    bool has_spare;             // True while spare holds a draw not yet given
    bool designed;              // True once generate_design has been called
}generate_t;
```

## Functions

### `generate_is_valid_kind`

```c
bool generate_is_valid_kind(generate_kind_t kind);
```

True if the kind is one this module knows.

### `generate_is_valid_frequency`

```c
bool generate_is_valid_frequency(real_t frequency, real_t sample_rate);
```

True if this frequency can be made at this sample rate, which means above
nothing and below half the rate.

A frequency at or above half the sample rate cannot be told from a lower
one, and asking for it gives an answer about a frequency nobody wanted.

### `generate_make`

```c
generate_t generate_make(generate_kind_t kind);
```

Give a maker of the given shape, standing at the start of its turn.

This takes no memory at all: everything it holds is in the type. Thus there
is no free, and one may be made on the stack.

### `generate_design`

```c
bool generate_design(generate_t* generate, real_t frequency, real_t sample_rate);
```

Choose the frequency and the sample rate.

The phase is left where it stands, thus the frequency of a running maker may
be changed at any sample and the wave carries on from where it was. That is
what makes it possible to follow something.

The two noises ignore the frequency. Give false if the kind is unknown, or
if the frequency cannot be made at this rate and the kind is not a noise.

### `generate_design_sweep`

```c
bool generate_design_sweep(generate_t* generate, real_t from, real_t to, real_t sample_rate, uint32_t samples);
```

Set the frequency to move steadily from one to another across a number of
samples, which makes a chirp.

A CHIRP IS THE MOST USEFUL TEST SIGNAL THERE IS, because it visits every
frequency in one run. One chirp through a filter shows the whole of what the
filter does, where a set of tones shows only the frequencies that were
chosen.

Give false if either frequency cannot be made at this rate, or the number of
samples is nothing.

### `generate_set_seed`

```c
void generate_set_seed(generate_t* generate, uint32_t seed);
```

Set where the random values start, so that a run can be repeated exactly.

A TEST THAT CANNOT BE REPEATED IS NOT A TEST. The same seed gives the same
values on every machine and at either width, thus a fault found once can be
found again.

### `generate_is_valid_part`

```c
bool generate_is_valid_part(real_t part);
```

True if this is a part of a turn a pulse can fill, which means above nothing
and below one. A pulse that filled none of the turn or all of it would have
no corners and would not be a pulse.

### `generate_set_part`

```c
bool generate_set_part(generate_t* generate, real_t part);
```

Choose how much of each turn a pulse fills.

GENERATE_PULSE is high for this part of the turn and low for the rest, thus
a part of a half gives the square wave and a part of a tenth gives a narrow
pulse standing once each turn.

GENERATE_GAUSSIAN_PULSE reads it as the WIDTH of its bump, as a part of the
turn: the bump falls away by the same amount at this distance either side of
the middle of the turn as a normal spread falls away at one standard
deviation. A part of about an eighth gives a bump that has died away by the
ends of its turn; anything much wider runs into the turn beside it.

Every other kind ignores it. Give false and leave the maker as it was if the
part is not one generate_is_valid_part accepts.

### `generate_get_part`

```c
real_t generate_get_part(const generate_t* generate);
```

Give the part of a turn a pulse fills.

### `generate_sample`

```c
real_t generate_sample(generate_t* generate);
```

Make the next sample.

### `generate_block`

```c
bool generate_block(generate_t* generate, real_t* output, uint32_t count);
```

Fill a list with the next samples.

Give false if the maker has not been designed.

### `generate_reset`

```c
void generate_reset(generate_t* generate);
```

Put the maker back to the start of its turn, without changing the frequency.

### `generate_get_phase`

```c
real_t generate_get_phase(const generate_t* generate);
```

Give where in the turn the maker stands, from 0 to 1.

Use it to make two shapes that keep step with each other: set one from the
other after each sample.

### `generate_set_phase`

```c
void generate_set_phase(generate_t* generate, real_t phase);
```

Set where in the turn the maker stands, from 0 to 1.
