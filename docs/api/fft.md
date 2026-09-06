# fft

This file comes from the comments in the headers. Do not change it by hand.
To make it again, give:

```bash
python3 scripts/api_doc.py
```

The fast Fourier transform. Declared in `ffitt/transform/fft.h`.

[Back to the index](../API.md) | [How the transform modules work](../../ffitt/transform/README.md) | [How it works](../diagrams/transform/fft.html) ([preview](https://htmlpreview.github.io/?https://github.com/AugustinJose1221/ffitt/blob/main/docs/diagrams/transform/fft.html))

## Overview

The fast Fourier transform.

The transform changes a signal in the time domain into a signal in the
frequency domain. Element k of the result says how much of the signal turns
at the frequency of the bin k. Use fft_bin_frequency to get that frequency
in hertz.

The module takes a size that is a power of two, such as 64, 256 or 1024.
This is the radix-2 method of Cooley and Tukey. A size that is not a power
of two needs another method with much more code, and that method holds less
accuracy in a float. Use fft_is_valid_size to examine a size.

The transform needs two tables that depend on the size only: the turning
factors and the order of the bit reversal. The module calculates them one
time at the allocation, thus a transform itself gets no memory. A program
that transforms the same size again and again makes the fft_t one time.

A float holds about 7 digits. The error of the transform grows with the
logarithm of the size. Up to about 4096 points the result keeps at least 4
digits. Above that, examine whether the accuracy is still enough for your
work.

## Method

Bin k of the result is the whole signal weighed against one turning rate:

    X[k] = sum over n of x[n] * exp(-2*pi*i*k*n/size)

Worked out as it stands, that is size steps for each of size bins, thus
size*size steps in all.

The library does not work it out as it stands. The sum splits into the
samples at even places and the samples at odd places, and each half is a
transform of half the size. Splitting again and again leaves log2(size)
passes over the array, which is why the size must be a power of two.

The splitting leaves the samples wanted in the order of the bits of the
index, read backwards. The module therefore exchanges the pairs first, and
then works the passes over the array in place. The turning factors and that
order depend on the size alone, thus both are worked out at the allocation
and never again.

## Macros

### `FFT_TWIDDLE_COUNT`

```c
#define FFT_TWIDDLE_COUNT(size)     ((size)/2)
```

The number of turning factors that a transform of the given size needs.

### `FFT_REVERSE_COUNT`

```c
#define FFT_REVERSE_COUNT(size)     (size)
```

The number of indices of the bit reversal that a transform of the given size
needs.

### `FFT_REAL_BIN_COUNT`

```c
#define FFT_REAL_BIN_COUNT(size)    (((size)/2) + 1)
```

The number of bins that hold new information in the transform of a real
signal, which is half the size and one more.

A real signal gives a spectrum where the second half is the mirror of the
first, thus the bins above this many say nothing that the bins below them
have not already said. Bin 0 holds the level of the signal and bin size/2
holds the highest frequency the sample rate can carry.

## Types

### `fft_t`

```c
typedef struct{
    uint32_t size;              // The number of points, a power of two
    cnum_t* twiddle;            // The turning factors, size/2 of them
    uint32_t* reverse;          // The order of the bit reversal, size of them
    bool dynamic_alloc;         // True if the memory comes from the heap
}fft_t;
```

## Functions

### `fft_is_valid_size`

```c
bool fft_is_valid_size(uint32_t size);
```

True if the size is a power of two and larger than one. Only such a size
works with this module.

### `fft_alloc`

```c
fft_t fft_alloc(uint32_t size);
```

Give a transform for the given number of points. The memory comes from the
heap. Give the transform to fft_free when you no longer need it.

### `fft_static_alloc`

```c
fft_t fft_static_alloc(uint32_t size, cnum_t* twiddle, uint32_t* reverse);
```

Give a transform that uses the memory that the caller holds. The table
twiddle must hold FFT_TWIDDLE_COUNT(size) complex numbers, and the table
reverse must hold FFT_REVERSE_COUNT(size) values. This function takes no
memory from the heap.

### `fft_forward`

```c
void fft_forward(fft_t* fft, cnum_t* data);
```

Change the given data from the time domain into the frequency domain. The
data must hold as many complex numbers as the size of the transform. The
function writes the result over the data, and it gets no memory.

### `fft_inverse`

```c
void fft_inverse(fft_t* fft, cnum_t* data);
```

Change the given data from the frequency domain into the time domain. This
operation is the opposite of fft_forward: a forward transform and then an
inverse transform give the first data again. The function writes the result
over the data, and it gets no memory.

### `fft_forward_real`

```c
void fft_forward_real(fft_t* fft, const real_t* input, cnum_t* output);
```

Change a signal of float values into the frequency domain.

The function writes each value of the input into the real part of the
output, sets each imaginary part to zero, and then does a forward transform.
The output must hold as many complex numbers as the size of the transform.

A signal of real values gives a result where the second half mirrors the
first half. Thus only the bins from 0 to size/2 hold new information. This
function is not the faster method that uses that mirror. It gives the same
result with less code.

### `fft_inverse_real`

```c
void fft_inverse_real(fft_t* fft, const cnum_t* input, real_t* output, cnum_t* work);
```

Change a half spectrum back into a signal of real values.

This is the opposite of fft_forward_real. The input holds
FFT_REAL_BIN_COUNT(size) complex numbers, which is what the first half of a
forward transform of a real signal gives, and the output holds as many real
values as the size of the transform. The work buffer holds as many complex
numbers as the size of the transform and loses its content.

The mirrored half is rebuilt from the half that is given, thus the caller
need not hold it and cannot get it wrong.

TWO BINS ARE NOT FREE TO BE ANYTHING. Bin 0 and bin size/2 are their own
mirror, thus for a signal of real values they must be real themselves. This
function TAKES THE REAL PART of those two and drops whatever imaginary part
they carry. That is not a rounding matter: a filter written in the frequency
domain that turns the phase of every bin will turn those two into something
that no real signal can give, and the answer would otherwise hold a wave at
half the sample rate that was never asked for.

### `fft_magnitude`

```c
void fft_magnitude(const cnum_t* data, real_t* magnitude, uint32_t size);
```

Write the size of each element of the data into the magnitude list. The size
of an element says how strong that frequency is in the signal. Both lists
must hold as many values as the given size.

### `fft_power`

```c
void fft_power(const cnum_t* data, real_t* power, uint32_t size);
```

Write the square of the size of each element into the power list. This
function takes no square root, thus it is faster than fft_magnitude. Both
lists must hold as many values as the given size.

### `fft_bin_frequency`

```c
real_t fft_bin_frequency(uint32_t index, uint32_t size, real_t sample_rate);
```

Give the frequency in hertz that the bin with the given index holds. The
sample rate is the number of samples in one second.

A bin above size/2 holds a frequency above half the sample rate. Such a bin
mirrors a lower bin, and this function gives the negative frequency for it,
which is the frequency that the mirror holds.

### `fft_free`

```c
void fft_free(fft_t* fft);
```

Release the memory of a transform that came from fft_alloc. This function
does nothing for a transform that came from fft_static_alloc, thus a call
for either kind is safe. A second call does nothing.
