# hht

This file comes from the comments in the headers. Do not change it by hand.
To make it again, give:

```bash
python3 scripts/api_doc.py
```

The Hilbert-Huang transform. Declared in `ffitt/transform/hht.h`.

[Back to the index](../API.md) | [How the transform modules work](../../ffitt/transform/README.md) | [How it works](../diagrams/transform/hht.html) ([preview](https://htmlpreview.github.io/?https://github.com/AugustinJose1221/ffitt/blob/development/docs/diagrams/transform/hht.html))

## Overview

The Hilbert-Huang transform.

The transform joins the two parts that this library already holds:

1. The empirical mode decomposition takes a signal apart into intrinsic mode
   functions. Each function holds one frequency at a time.
2. The Hilbert transform gives the amplitude and the frequency at each point
   of time of such a function.

The result says which frequency the signal holds at which time, and how
strong it is. A Fourier transform gives the frequencies of the whole signal
and says nothing about the time. Thus the Hilbert-Huang transform suits a
signal whose frequency changes, where a Fourier transform gives a wide band
and no clear answer.

The Hilbert transform needs the size to be a power of two, because it uses
the fast Fourier transform. Give the decomposition a signal of such a size.

## Method

A Fourier transform asks how much of each frequency the WHOLE signal holds.
This asks which one frequency the signal holds AT EACH MOMENT, and that
question needs the signal taken apart first.

The road is two modules already here, one after the other:

    emd      splits x[n] into imf_1 .. imf_m, each of one frequency at a time
    hilbert  gives z[n] = imf[n] + i*H{imf}[n] for each of them

From each analytic signal come two readings at every sample:

    amplitude[n] = the distance of z[n] from zero
    frequency[n] = the change of the angle of z[n], times rate / (2*pi)

Thus the answer is not a spectrum but a list of curves: for each mode, how
strong it is and what frequency it holds, at every moment.

The whole thing rests on each mode holding one frequency at a time. Where
emd fails to separate them, the frequency of that mode is a mean of several
and describes nothing. That failure moves here unchanged.

## Functions

### `hht_transform_imf`

```c
void hht_transform_imf(fft_t* fft, imf_t* imf, cnum_t* work, real_t* amplitude, real_t* frequency, real_t sample_rate);
```

Give the amplitude and the frequency at each point of time, for one
intrinsic mode function.

The function writes size values into the amplitude list, and size-1 values
into the frequency list, because a frequency needs two points of the phase.
The work buffer must hold size complex numbers. The function gets no memory.

The size must be the same as the size of the transform, and it must be a
power of two.

### `hht_transform`

```c
void hht_transform(fft_t* fft, imf_t* imf, uint32_t count, cnum_t* work, real_t* amplitude, real_t* frequency, real_t sample_rate);
```

Give the amplitude and the frequency for a list of intrinsic mode
functions, one after the other.

The lists amplitude and frequency hold the result of each function one after
the other. Thus the amplitude list must hold count*size values, and the
frequency list must hold count*(size-1) values. The work buffer must hold
size complex numbers.

### `hht_mean_frequency`

```c
real_t hht_mean_frequency(const real_t* amplitude, const real_t* frequency, uint32_t size);
```

Give the mean frequency of one intrinsic mode function, where each point
counts as much as the square of its amplitude.

A point with a small amplitude holds a phase that noise moves easily. This
mean gives such a point little weight, thus it describes the function better
than a plain mean does.
