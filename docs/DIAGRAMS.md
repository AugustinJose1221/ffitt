# Diagrams

This file comes from the diagrams under docs/diagrams. Do not change it by hand.
To make it again, give:

```bash
python3 scripts/api_doc.py
```

One page for each module, showing how that module does its work. Each page holds
a few chapters that walk through it a step at a time.

**Preview** opens the page in a browser. **File** is the page itself, which a
reader with a clone can open with no service at all.

20 of the 64 modules have a diagram.

## Transforms

| Module | Diagram | File |
|---|---|---|
| [`fft`](api/fft.md) | [preview](https://htmlpreview.github.io/?https://github.com/AugustinJose1221/ffitt/blob/development/docs/diagrams/transform/fft.html) | [fft.html](diagrams/transform/fft.html) |
| [`bluestein`](api/bluestein.md) | [preview](https://htmlpreview.github.io/?https://github.com/AugustinJose1221/ffitt/blob/development/docs/diagrams/transform/bluestein.html) | [bluestein.html](diagrams/transform/bluestein.html) |
| [`window`](api/window.md) | [preview](https://htmlpreview.github.io/?https://github.com/AugustinJose1221/ffitt/blob/development/docs/diagrams/transform/window.html) | [window.html](diagrams/transform/window.html) |
| [`psd`](api/psd.md) | [preview](https://htmlpreview.github.io/?https://github.com/AugustinJose1221/ffitt/blob/development/docs/diagrams/transform/psd.html) | [psd.html](diagrams/transform/psd.html) |
| [`csd`](api/csd.md) | [preview](https://htmlpreview.github.io/?https://github.com/AugustinJose1221/ffitt/blob/development/docs/diagrams/transform/csd.html) | [csd.html](diagrams/transform/csd.html) |
| [`stft`](api/stft.md) | [preview](https://htmlpreview.github.io/?https://github.com/AugustinJose1221/ffitt/blob/development/docs/diagrams/transform/stft.html) | [stft.html](diagrams/transform/stft.html) |
| [`spectrogram`](api/spectrogram.md) | [preview](https://htmlpreview.github.io/?https://github.com/AugustinJose1221/ffitt/blob/development/docs/diagrams/transform/spectrogram.html) | [spectrogram.html](diagrams/transform/spectrogram.html) |
| [`correlate`](api/correlate.md) | [preview](https://htmlpreview.github.io/?https://github.com/AugustinJose1221/ffitt/blob/development/docs/diagrams/transform/correlate.html) | [correlate.html](diagrams/transform/correlate.html) |
| [`convolve`](api/convolve.md) | [preview](https://htmlpreview.github.io/?https://github.com/AugustinJose1221/ffitt/blob/development/docs/diagrams/transform/convolve.html) | [convolve.html](diagrams/transform/convolve.html) |
| [`goertzel`](api/goertzel.md) | [preview](https://htmlpreview.github.io/?https://github.com/AugustinJose1221/ffitt/blob/development/docs/diagrams/transform/goertzel.html) | [goertzel.html](diagrams/transform/goertzel.html) |
| [`slide`](api/slide.md) | [preview](https://htmlpreview.github.io/?https://github.com/AugustinJose1221/ffitt/blob/development/docs/diagrams/transform/slide.html) | [slide.html](diagrams/transform/slide.html) |
| [`hilbert`](api/hilbert.md) | [preview](https://htmlpreview.github.io/?https://github.com/AugustinJose1221/ffitt/blob/development/docs/diagrams/transform/hilbert.html) | [hilbert.html](diagrams/transform/hilbert.html) |
| [`hht`](api/hht.md) | [preview](https://htmlpreview.github.io/?https://github.com/AugustinJose1221/ffitt/blob/development/docs/diagrams/transform/hht.html) | [hht.html](diagrams/transform/hht.html) |
| [`dwt`](api/dwt.md) | [preview](https://htmlpreview.github.io/?https://github.com/AugustinJose1221/ffitt/blob/development/docs/diagrams/transform/dwt.html) | [dwt.html](diagrams/transform/dwt.html) |
| [`dct`](api/dct.md) | [preview](https://htmlpreview.github.io/?https://github.com/AugustinJose1221/ffitt/blob/development/docs/diagrams/transform/dct.html) | [dct.html](diagrams/transform/dct.html) |
| [`cepstrum`](api/cepstrum.md) | [preview](https://htmlpreview.github.io/?https://github.com/AugustinJose1221/ffitt/blob/development/docs/diagrams/transform/cepstrum.html) | [cepstrum.html](diagrams/transform/cepstrum.html) |

## Filters

| Module | Diagram | File |
|---|---|---|
| [`fir`](api/fir.md) | [preview](https://htmlpreview.github.io/?https://github.com/AugustinJose1221/ffitt/blob/development/docs/diagrams/filter/fir.html) | [fir.html](diagrams/filter/fir.html) |
| [`iir`](api/iir.md) | [preview](https://htmlpreview.github.io/?https://github.com/AugustinJose1221/ffitt/blob/development/docs/diagrams/filter/iir.html) | [iir.html](diagrams/filter/iir.html) |
| [`savgol`](api/savgol.md) | not yet drawn | |
| [`movavg`](api/movavg.md) | [preview](https://htmlpreview.github.io/?https://github.com/AugustinJose1221/ffitt/blob/development/docs/diagrams/filter/movavg.html) | [movavg.html](diagrams/filter/movavg.html) |
| [`medfilt`](api/medfilt.md) | [preview](https://htmlpreview.github.io/?https://github.com/AugustinJose1221/ffitt/blob/development/docs/diagrams/filter/medfilt.html) | [medfilt.html](diagrams/filter/medfilt.html) |
| [`dcblock`](api/dcblock.md) | not yet drawn | |
| [`detrend`](api/detrend.md) | not yet drawn | |
| [`hampel`](api/hampel.md) | not yet drawn | |
| [`adaptive`](api/adaptive.md) | not yet drawn | |
| [`rls`](api/rls.md) | not yet drawn | |
| [`lattice`](api/lattice.md) | not yet drawn | |
| [`resample`](api/resample.md) | not yet drawn | |
| [`filtfilt`](api/filtfilt.md) | not yet drawn | |
| [`farrow`](api/farrow.md) | not yet drawn | |

## Estimation

| Module | Diagram | File |
|---|---|---|
| [`kalman`](api/kalman.md) | not yet drawn | |
| [`ekf`](api/ekf.md) | not yet drawn | |
| [`ukf`](api/ukf.md) | not yet drawn | |
| [`propagate`](api/propagate.md) | not yet drawn | |
| [`pll`](api/pll.md) | not yet drawn | |

## Decomposition

| Module | Diagram | File |
|---|---|---|
| [`emd`](api/emd.md) | not yet drawn | |
| [`imf`](api/imf.md) | not yet drawn | |

## Interpolation

| Module | Diagram | File |
|---|---|---|
| [`cspline`](api/cspline.md) | not yet drawn | |
| [`interp`](api/interp.md) | not yet drawn | |

## Linear algebra

| Module | Diagram | File |
|---|---|---|
| [`matrix`](api/matrix.md) | not yet drawn | |
| [`cmatrix`](api/cmatrix.md) | not yet drawn | |
| [`pmatrix`](api/pmatrix.md) | not yet drawn | |
| [`cnum`](api/cnum.md) | not yet drawn | |
| [`quaternion`](api/quaternion.md) | not yet drawn | |
| [`eigen`](api/eigen.md) | not yet drawn | |
| [`poly`](api/poly.md) | not yet drawn | |
| [`lstsq`](api/lstsq.md) | not yet drawn | |
| [`vector`](api/vector.md) | not yet drawn | |
| [`vector2d`](api/vector2d.md) | not yet drawn | |

## Detection

| Module | Diagram | File |
|---|---|---|
| [`matched`](api/matched.md) | not yet drawn | |
| [`delay`](api/delay.md) | not yet drawn | |
| [`changepoint`](api/changepoint.md) | not yet drawn | |

## Utilities

| Module | Diagram | File |
|---|---|---|
| [`generate`](api/generate.md) | not yet drawn | |
| [`curve`](api/curve.md) | not yet drawn | |
| [`quantise`](api/quantise.md) | not yet drawn | |
| [`stats`](api/stats.md) | not yet drawn | |
| [`binarysearch`](api/binarysearch.md) | not yet drawn | |
| [`peakdetect`](api/peakdetect.md) | not yet drawn | |
| [`valleydetect`](api/valleydetect.md) | not yet drawn | |

## Core

| Module | Diagram | File |
|---|---|---|
| [`real`](api/real.md) | not yet drawn | |
| [`nolibm`](api/nolibm.md) | not yet drawn | |
| [`ringbuf`](api/ringbuf.md) | not yet drawn | |
| [`point2d`](api/point2d.md) | not yet drawn | |
| [`callback`](api/callback.md) | not yet drawn | |
