# spectrogram

This file comes from the comments in the headers. Do not change it by hand.
To make it again, give:

```bash
python3 scripts/api_doc.py
```

What the short pieces mean. Declared in `ffitt/transform/spectrogram.h`.

[Back to the index](../API.md) | [How the transform modules work](../../ffitt/transform/README.md) | [How it works](../diagrams/transform/spectrogram.html) ([preview](https://htmlpreview.github.io/?https://github.com/AugustinJose1221/ffitt/blob/main/docs/diagrams/transform/spectrogram.html))

## Overview

What the frames of a short-time transform mean, in a unit that can be read.

stft_forward gives complex numbers, and a complex number is not something to
look at. This module turns those frames into one real number for each bin of
each frame, in whichever of four units the question asks for.

THE SCALING IS THE PART THAT IS USUALLY WRONG, and the wrong answer looks
perfectly reasonable. A transform of a longer block gives larger numbers for
the same signal; a window makes them smaller; and half of the power sits in
the mirrored half that is not there. Left uncorrected, the same tone reads
differently for every choice of block and window, and the number means
nothing outside the one program that made it.

This module corrects all three, thus:

  A WAVE OF AMPLITUDE A READS AS A, in SPECTROGRAM_AMPLITUDE, whatever the
  block, the window or the hop.

The four units:

  SPECTROGRAM_AMPLITUDE  how large the wave at that bin is, in the unit of
                         the signal. A wave of amplitude 2 reads 2.
  SPECTROGRAM_POWER      the mean power of that wave, which is A*A/2. This
                         is what adds up across bins.
  SPECTROGRAM_DENSITY    power for each hertz, which is what psd gives, and
                         the only one of the four that does not change when
                         the block gets longer.
  SPECTROGRAM_DECIBEL    the power in decibels against a reference of 1.

WHICH ONE TO ASK FOR. To read the size of a tone off a picture, amplitude.
To add the power of a band together, density. To draw the picture at all,
decibels, because a spectrogram of anything real covers so many factors of
ten that a linear scale shows one bright line and black everywhere else.

THE FLOOR UNDER THE DECIBELS IS NOT A DETAIL. The logarithm of nothing has
no value, and a bin that holds nothing is a thing that happens: a silent
stretch of recording, or a bin above the cutoff of a filter. Without a floor
the answer holds values that no arithmetic and no picture can use.
SPECTROGRAM_FLOOR_DECIBEL is where this module stops.

## Method

One frame of the short-time transform gives a complex number for each bin.
The size of that number is turned into a unit a reader can use:

    amplitude = 2 * |X[k]| / (block * coherent_gain)
    power     = amplitude^2 / 2
    density   = |X[k]|^2 / (rate * block * noise_gain)
    decibel   = 10 * log10(power), held above a floor

Three corrections stand in those lines, and leaving any one out gives an
answer that looks reasonable and means nothing:

  divide by the block, because a longer block gives larger numbers for the
  same signal;
  divide by the gain of the window, because a window makes the signal
  smaller;
  double it, because half of the power sits in the mirrored half that a
  real signal does not keep.

The logarithm of nothing has no value, and a bin that holds nothing is a
thing that happens. The decibel answer therefore stops at a floor rather
than falling for ever.

## Macros

### `SPECTROGRAM_FLOOR_DECIBEL`

```c
#define SPECTROGRAM_FLOOR_DECIBEL   (-REAL_C(200.0))
```

The lowest value the decibel unit gives.

A bin holding nothing has no logarithm. 200 decibels below a reference of 1
is far below anything a measurement can reach at either width, thus the
floor cannot hide a real reading, and it keeps the answer to numbers that
arithmetic and pictures can use.

## Functions

### `spectrogram_is_valid_kind`

```c
bool spectrogram_is_valid_kind(spectrogram_kind_t kind);
```

True if the unit is one this module knows.

### `spectrogram_value_count`

```c
uint32_t spectrogram_value_count(const stft_t* stft, uint32_t frame_count);
```

How many values a spectrogram of this many frames holds.

### `spectrogram_build`

```c
bool spectrogram_build(const stft_t* stft, const cnum_t* frames, uint32_t frame_count, spectrogram_kind_t kind, real_t sample_rate, real_t* output, uint32_t room);
```

Turn the frames of a short-time transform into one real number for each bin.

The frames are what stft_forward gave, and the output holds
spectrogram_value_count values laid out the same way: the bin b of the frame
f sits at (f * STFT_BIN_COUNT(block)) + b.

The sample rate is used by SPECTROGRAM_DENSITY only, and it is ignored by
the other three.

Give false if the transform has not been designed, if the unit is unknown,
if there are no frames, or if the room is too small.

### `spectrogram_largest`

```c
real_t spectrogram_largest(const real_t* values, uint32_t count);
```

Give the largest value in a spectrogram, which is what a picture is usually
drawn against.

### `spectrogram_against_the_largest`

```c
bool spectrogram_against_the_largest(const real_t* values, uint32_t count, real_t* output);
```

Turn a spectrogram of decibels into one measured from its own largest value,
so that the largest reads 0 and everything else is below it.

This is how a spectrogram is nearly always drawn, because the reading that
matters is which parts are loud AGAINST THE REST and not against a reference
that the recording never knew about. The output may be the input.

Give false if the values are not decibels, which the caller must know, or if
there are none.
