# bluestein

This file comes from the comments in the headers. Do not change it by hand.
To make it again, give:

```bash
python3 scripts/api_doc.py
```

A transform of any size. Declared in `ffitt/transform/bluestein.h`.

[Back to the index](../API.md) | [How the transform modules work](../../ffitt/transform/README.md) | [How it works](../diagrams/transform/bluestein.html) ([preview](https://htmlpreview.github.io/?https://github.com/AugustinJose1221/ffitt/blob/main/docs/diagrams/transform/bluestein.html))

## Overview

A transform of ANY size, built on the transform of a power of two.

The fft module takes a power of two and nothing else. That is the right
trade for most work, because a block of 1024 is a choice and not a fact. But
some sizes are facts:

  A MAINS PERIOD. At 3000 samples in a second, one period of 50 hertz is 60
  samples and one period of 60 hertz is 50. Neither is a power of two, and a
  block that does not hold a whole number of periods spreads the mains hum
  across every bin instead of putting it in one.
  A DAY, A REVOLUTION, A BATCH. 1440 minutes, 360 degrees, or however many
  readings the machine happens to give for each turn of the shaft.
  A SIZE THAT ANOTHER SYSTEM FIXED and that this one has to match.

Rounding such a size up to a power of two and filling with zeros is the
usual answer and it is often wrong: it moves every bin off the frequency
that was wanted, which is the whole reason the size was chosen.

HOW IT WORKS

The trick is that n times k, which is what a transform needs, can be written
as the squares of n, of k and of their difference. That turns the transform
into a CONVOLUTION, and a convolution of any length can be done by a
transform of any size at least as long, which may be a power of two. Thus a
transform of 60 points is done by a transform of 128 with some arithmetic
around it.

WHAT IT COSTS

Two transforms of the larger size at each call, one more at the allocation,
and the arithmetic between them. FOR A SIZE THAT IS A POWER OF TWO ALREADY,
USE THE FFT MODULE: measured on the same size, this one takes 5.1 times as
long and gives nothing extra.

    size                256      1024      4096
    fft                0.0055 ms 0.0244 ms 0.1151 ms
    this module        0.0284 ms 0.1243 ms 0.5882 ms

The ratio holds steady across the range, because both grow in the same way
and the larger size inside is what the constant is made of.

The tables it holds are larger too. Beside the tables of the transform
inside it, it keeps one turning factor for each point of the size asked for
and one for each point of the larger size.

WHAT IT COSTS IN PRECISION

Measured against a transform of the same size worked out the slow and direct
way, on a signal of random values. The worst error across all bins, as a part
of the largest bin:

    size                60         100         360        1000
    32 bits      0.0000004   0.0000005   0.0000005   0.0000006
    64 bits      below what these figures can show, at every size

That is the same order as the fft module itself, and for the same reason:
the arithmetic is a handful of transforms and nothing worse.

THE ONE PLACE IT WOULD FALL APART, AND WHERE THAT IS HELD OFF

The turning factors of this method follow the SQUARE of the index. For a
size of 200000 the last one asks for the sine of an angle of pi times four
times ten to the tenth, and a number of 32 bits holding an angle that large
has spent every digit it owns on how many turns and has none left for where
in the turn it lands.

The module therefore folds the square back into one turn before it forms any
angle. It costs one division for each factor, at the allocation only, and it
is what makes the method usable at 32 bits at all. Measured on a single tone,
where every bin but one should hold nothing, the worst false answer as a part
of the tone, at 32 bits:

    size              1 000      10 000      50 000     200 000
    with the fold   0.0000001   0.0000000   0.0000000   0.0000001
    without it      0.0000076   0.0001036   0.0003396   0.0014121

The fold holds the error flat across the whole range while the error without
it grows with the size, and by 200000 it is fourteen thousand times worse.
At 64 bits there are digits to spare at these sizes and the fold does not
show; it is kept because the module must hold at either width.

## Method

A bin of the transform is:

    X[k] = sum over n of x[n] * exp(-2*pi*i*k*n/size)

The trick of Bluestein rewrites the product k*n using

    k*n = (k^2 + n^2 - (k-n)^2) / 2

which turns the sum into a convolution:

    X[k] = conj(c[k]) * sum over n of (x[n] * conj(c[n])) * c[k-n]

where c[j] = exp(-i*pi*j^2/size) is the chirp. A convolution of any length
can be done with transforms of a power of two, and that is the whole point:
the size the caller asked for never has to be a power of two.

The convolution runs to 2*size-1 places. A transform works on a signal that
repeats for ever, thus anything past the end wraps round and adds itself to
the start. The library therefore takes the next power of two at or above
2*size-1, which is why a transform of size n costs the memory of one about
four times as large.

The square of the index is folded by 2*size before the angle is taken, so
that a large index does not lose its accuracy to a huge angle.

## Macros

### `BLUESTEIN_LARGEST_SIZE`

```c
#define BLUESTEIN_LARGEST_SIZE      ((uint32_t)1u << 20)
```

The largest size this module takes.

The transform inside must hold at least twice the size, thus a larger size
than this cannot be served by any power of two that fits in the count.

### `BLUESTEIN_CHIRP_COUNT`

```c
#define BLUESTEIN_CHIRP_COUNT(size)     (size)
```

The number of turning factors that a transform of the given size needs.

## Types

### `bluestein_t`

```c
typedef struct{
    uint32_t size;              // The number of points, any size
    fft_t fft;                  // The transform of a power of two inside
    cnum_t* chirp;              // One turning factor for each point
    cnum_t* kernel;             // The shape to convolve with, transformed
    cnum_t* first;              // Working room, the larger size
    cnum_t* second;             // Working room, the larger size
    bool dynamic_alloc;         // True if the memory comes from the heap
}bluestein_t;
```

## Functions

### `bluestein_is_valid_size`

```c
bool bluestein_is_valid_size(uint32_t size);
```

True if the module can transform this size. Any size from 2 up to
BLUESTEIN_LARGEST_SIZE will do, whether it is a power of two or not.

### `bluestein_transform_size`

```c
uint32_t bluestein_transform_size(uint32_t size);
```

Give the size of the transform that runs inside, which is the smallest power
of two that holds the convolution whole.

Use this to work out the memory before allocating: it is the size of the
transform inside and the length of both working buffers. Give 0 for a size
the module cannot serve.

### `bluestein_alloc`

```c
bluestein_t bluestein_alloc(uint32_t size);
```

Give a transform for the given number of points. The memory comes from the
heap. Give it to bluestein_free when it is no longer needed.

A transform whose size is 0 came back because the size is not one the module
takes. Examine the size with bluestein_is_valid_size first.

### `bluestein_static_alloc`

```c
bluestein_t bluestein_static_alloc(uint32_t size, cnum_t* twiddle, uint32_t* reverse, cnum_t* chirp, cnum_t* kernel, cnum_t* first, cnum_t* second);
```

Give a transform that uses the memory the caller holds, taking nothing from
the heap.

The table twiddle must hold FFT_TWIDDLE_COUNT(m) complex numbers and reverse
must hold FFT_REVERSE_COUNT(m) values, where m is bluestein_transform_size
of the size. The table chirp must hold BLUESTEIN_CHIRP_COUNT(size) complex
numbers, and kernel, first and second must each hold m of them.

### `bluestein_forward`

```c
void bluestein_forward(bluestein_t* bluestein, cnum_t* data);
```

Change the given data from the time domain into the frequency domain.

The data holds as many complex numbers as the size, and the result is
written over it. The result is the same as a transform of that size worked
out directly, to the precision the table above records.

### `bluestein_inverse`

```c
void bluestein_inverse(bluestein_t* bluestein, cnum_t* data);
```

Change the given data from the frequency domain into the time domain.

A forward transform and then an inverse transform give the first data again.

### `bluestein_bin_frequency`

```c
real_t bluestein_bin_frequency(uint32_t index, uint32_t size, real_t sample_rate);
```

Give the frequency in hertz that the bin with the given index holds.

This is the reason to use a size that is not a power of two. At 3000 samples
in a second and a size of 60, bin 1 holds exactly 50 hertz.

### `bluestein_free`

```c
void bluestein_free(bluestein_t* bluestein);
```

Release the memory of a transform that came from bluestein_alloc. This does
nothing for one that came from bluestein_static_alloc, thus a call for
either kind is safe. A second call does nothing.
