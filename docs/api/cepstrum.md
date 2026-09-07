# cepstrum

This file comes from the comments in the headers. Do not change it by hand.
To make it again, give:

```bash
python3 scripts/api_doc.py
```

Finding what repeats in a spectrum. Declared in `ffitt/transform/cepstrum.h`.

[Back to the index](../API.md) | [How the transform modules work](../../ffitt/transform/README.md) | [How it works](../diagrams/transform/cepstrum.html) ([preview](https://htmlpreview.github.io/?https://github.com/AugustinJose1221/ffitt/blob/development/docs/diagrams/transform/cepstrum.html))

## Overview

Find a thing that repeats in the SPECTRUM rather than in the signal.

A voice, a violin string and an engine all make a tone with harmonics: a
frequency and then the same frequency doubled, trebled and so on. In the
spectrum those harmonics are a row of peaks EVENLY SPACED, and how far apart
they stand is the frequency of the note.

A row of evenly spaced peaks is itself a thing that repeats, and the way to
find a thing that repeats is a transform. TAKING A TRANSFORM OF A SPECTRUM IS
WHAT THIS DOES, and the row of harmonics comes out as one peak.

The word for the place of that peak is quefrency, and it is a time: a peak at
quefrency 80 means the harmonics stand a beat of 1/80 of the sample rate
apart, which means the note repeats every 80 samples.

WHY NOT JUST CORRELATE THE SIGNAL. correlate_best_lag also finds a period and
is cheaper, and for a plain repeating signal it is the right answer. Measured
on a note whose true period is 64 samples, built from harmonics of it:

  harmonics present            cepstrum      correlate
  -------------------------   ---------     ----------
  1 to 12                        64  ok       192 wrong
  2 to 12, no fundamental        64  ok       128 wrong
  3 to 12                        64  ok        64  ok

READ THE ROW WITH NO FUNDAMENTAL. A small loudspeaker cannot make 100 Hz, thus
a note at 100 Hz comes out as 200, 300, 400 and nothing at 100. The ear still
hears 100. Correlation sees a signal that repeats at a shorter period and says
so, with a strength of 1.000 while it does; this sees harmonics 100 apart and
answers 100.

THE OTHER THING IT FINDS IS AN ECHO. A sound and the same sound again a little
later multiply the spectrum by a ripple, and a ripple in the spectrum is a
peak here. Measured on a burst of noise with a copy of itself at 100 samples
and seven tenths the loudness, this answered 100.

THE LOGARITHM IS WHAT MAKES THE ECHO SEPARABLE, and it is not a detail. An
echo MULTIPLIES the spectrum. Taking the logarithm turns multiplying into
adding, thus what the room did and what the source did become two things
standing side by side rather than one wrapped around the other. Without it
this would be the plain autocorrelation and would find nothing new.

THE BLOCK IS WINDOWED, AND THAT IS NOT A DETAIL EITHER. It was written once
without a window, on the reasoning that a note whose period divides the block
needs none. The NOISE on that note does not divide the block: it leaks across
every bin, its leakage has strong structure in the logarithm, and that
structure drowns the row of harmonics. Measured on a note with no fundamental
and a twentieth of noise, the answer without a window came back at 255 where
64 was right, and moved about with the floor and with the width of the build.
With a window every one of those cases gives 64, at both widths.

WHAT IT CANNOT DO.

  THE ANSWER IS A WHOLE NUMBER OF SAMPLES and the true period rarely is.
  Measured, a period of 100 came back as 99 and one of 128 as 129. That is
  the quefrency axis being sampled and not an error of the method: give the
  cepstrum to peakdetect_refine to get the place of the peak between samples.

  IT NEEDS SEVERAL HARMONICS. With five it answered 62 where 64 was right,
  because a short row of peaks has a broad transform. Below about eight, treat
  the answer as a hint.

  THE STRENGTH TELLS STRUCTURE FROM NOISE AND NOT A TONE FROM A NOTE. A block
  of noise gives about 0.06 and a real note about 0.2 to 0.7, thus the two are
  easily told apart. A SINGLE PURE TONE ALSO GIVES ABOUT 0.25, because one
  peak in a spectrum is structure too. A caller who must tell a note from a
  tone has to look at the spectrum for more than one peak; this will not do it.

  It says nothing about WHEN, only about what repeats across the whole block.
  And it is fooled by anything else evenly spaced in the spectrum, a comb
  filter above all.

## Method

The cepstrum is a transform of a spectrum:

    c[q] = inverse transform of log(|X[k]|)

The logarithm is what makes it work. A signal made by a source passing
through a shape is a MULTIPLICATION of the two in the spectrum, and a
logarithm turns a multiplication into a SUM. The source and the shape can
then be added apart, which no other road here offers.

A row of harmonics standing evenly apart in the spectrum is itself a thing
that repeats, thus it comes out of this transform as one peak.

The place of that peak is called quefrency and it is a time, not a
frequency. A peak at quefrency 80 says the harmonics stand a beat of
rate/80 apart, thus the note repeats every 80 samples:

    period in samples = quefrency
    note in hertz     = rate / quefrency

The slow part of the log spectrum is the shape of the thing that the sound
passed through, and the fast part is the source. Cutting the cepstrum at a
quefrency and transforming back keeps one and drops the other.

## Macros

### `CEPSTRUM_FLOOR`

```c
#define CEPSTRUM_FLOOR      REAL_C(1.0e-6)
```

## Types

### `cepstrum_t`

```c
typedef struct{
    fft_t fft;                  // The transform, taken twice
    cnum_t* work;               // Room for one spectrum
    real_t* window;             // The window laid on the block
    real_t* windowed;           // The block after the window
    uint32_t size;              // The block, a power of two
    bool dynamic_alloc;         // True if the memory comes from the heap
}cepstrum_t;
```

## Functions

### `cepstrum_is_valid_size`

```c
bool cepstrum_is_valid_size(uint32_t size);
```

True if this is a block the cepstrum can be taken of, which is whatever the
transform can take.

### `cepstrum_alloc`

```c
cepstrum_t cepstrum_alloc(uint32_t size);
```

Give a cepstrum of the given block size. The memory comes from the heap. Give
it to cepstrum_free when you no longer need it.

### `cepstrum_static_alloc`

```c
cepstrum_t cepstrum_static_alloc(uint32_t size, cnum_t* work, real_t* window, real_t* windowed, fft_t fft);
```

Give one that uses the memory the caller holds. The work must hold as many
complex numbers as the size, and the window and the windowed block as many
real values. This takes nothing from the heap.

### `cepstrum_real`

```c
bool cepstrum_real(cepstrum_t* cepstrum, const real_t* input, real_t* output);
```

Work out the real cepstrum of a block.

The output holds as many values as the block. The value at place k says how
much the spectrum ripples with a beat that fits k times into the block, thus k
is a number of samples and is called a quefrency.

The first few places hold the SHAPE of the spectrum rather than anything
repeating in it -- how the loudness falls away with frequency, which for a
voice is the shape of the mouth. Reading a period from them finds the shape
and not the note, thus cepstrum_best_quefrency starts past them.

Give false if the size is not one cepstrum_is_valid_size accepts.

### `cepstrum_best_quefrency`

```c
uint32_t cepstrum_best_quefrency(const real_t* cepstrum, uint32_t size, uint32_t low, uint32_t high, real_t* strength);
```

Give the quefrency between low and high where the cepstrum stands highest,
which is the period of whatever repeats in the spectrum.

THE LOW BOUND MUST BE SET AND IT MATTERS. Below about a twentieth of the block
the cepstrum holds the shape of the spectrum, which is always large and always
there. A search that started at nothing would find that shape every time and
call it a note.

The strength says how far the peak stands above the ordinary run of the range.
IT MUST BE READ, and the header above says what it can and cannot tell apart.
Give NULL if it is not wanted.

Give 0 and a strength of 0 if the range does not fit inside the block.

### `cepstrum_free`

```c
void cepstrum_free(cepstrum_t* cepstrum);
```

Give back the memory that cepstrum_alloc took.
