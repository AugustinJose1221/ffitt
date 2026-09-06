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

52 of the 64 modules have a diagram.

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
| [`savgol`](api/savgol.md) | [preview](https://htmlpreview.github.io/?https://github.com/AugustinJose1221/ffitt/blob/development/docs/diagrams/filter/savgol.html) | [savgol.html](diagrams/filter/savgol.html) |
| [`movavg`](api/movavg.md) | [preview](https://htmlpreview.github.io/?https://github.com/AugustinJose1221/ffitt/blob/development/docs/diagrams/filter/movavg.html) | [movavg.html](diagrams/filter/movavg.html) |
| [`medfilt`](api/medfilt.md) | [preview](https://htmlpreview.github.io/?https://github.com/AugustinJose1221/ffitt/blob/development/docs/diagrams/filter/medfilt.html) | [medfilt.html](diagrams/filter/medfilt.html) |
| [`dcblock`](api/dcblock.md) | [preview](https://htmlpreview.github.io/?https://github.com/AugustinJose1221/ffitt/blob/development/docs/diagrams/filter/dcblock.html) | [dcblock.html](diagrams/filter/dcblock.html) |
| [`detrend`](api/detrend.md) | [preview](https://htmlpreview.github.io/?https://github.com/AugustinJose1221/ffitt/blob/development/docs/diagrams/filter/detrend.html) | [detrend.html](diagrams/filter/detrend.html) |
| [`hampel`](api/hampel.md) | [preview](https://htmlpreview.github.io/?https://github.com/AugustinJose1221/ffitt/blob/development/docs/diagrams/filter/hampel.html) | [hampel.html](diagrams/filter/hampel.html) |
| [`adaptive`](api/adaptive.md) | [preview](https://htmlpreview.github.io/?https://github.com/AugustinJose1221/ffitt/blob/development/docs/diagrams/filter/adaptive.html) | [adaptive.html](diagrams/filter/adaptive.html) |
| [`rls`](api/rls.md) | [preview](https://htmlpreview.github.io/?https://github.com/AugustinJose1221/ffitt/blob/development/docs/diagrams/filter/rls.html) | [rls.html](diagrams/filter/rls.html) |
| [`lattice`](api/lattice.md) | [preview](https://htmlpreview.github.io/?https://github.com/AugustinJose1221/ffitt/blob/development/docs/diagrams/filter/lattice.html) | [lattice.html](diagrams/filter/lattice.html) |
| [`resample`](api/resample.md) | [preview](https://htmlpreview.github.io/?https://github.com/AugustinJose1221/ffitt/blob/development/docs/diagrams/filter/resample.html) | [resample.html](diagrams/filter/resample.html) |
| [`filtfilt`](api/filtfilt.md) | [preview](https://htmlpreview.github.io/?https://github.com/AugustinJose1221/ffitt/blob/development/docs/diagrams/filter/filtfilt.html) | [filtfilt.html](diagrams/filter/filtfilt.html) |
| [`farrow`](api/farrow.md) | [preview](https://htmlpreview.github.io/?https://github.com/AugustinJose1221/ffitt/blob/development/docs/diagrams/filter/farrow.html) | [farrow.html](diagrams/filter/farrow.html) |

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
| [`matrix`](api/matrix.md) | [preview](https://htmlpreview.github.io/?https://github.com/AugustinJose1221/ffitt/blob/development/docs/diagrams/linalg/matrix.html) | [matrix.html](diagrams/linalg/matrix.html) |
| [`cmatrix`](api/cmatrix.md) | [preview](https://htmlpreview.github.io/?https://github.com/AugustinJose1221/ffitt/blob/development/docs/diagrams/linalg/cmatrix.html) | [cmatrix.html](diagrams/linalg/cmatrix.html) |
| [`pmatrix`](api/pmatrix.md) | [preview](https://htmlpreview.github.io/?https://github.com/AugustinJose1221/ffitt/blob/development/docs/diagrams/linalg/pmatrix.html) | [pmatrix.html](diagrams/linalg/pmatrix.html) |
| [`cnum`](api/cnum.md) | [preview](https://htmlpreview.github.io/?https://github.com/AugustinJose1221/ffitt/blob/development/docs/diagrams/linalg/cnum.html) | [cnum.html](diagrams/linalg/cnum.html) |
| [`quaternion`](api/quaternion.md) | [preview](https://htmlpreview.github.io/?https://github.com/AugustinJose1221/ffitt/blob/development/docs/diagrams/linalg/quaternion.html) | [quaternion.html](diagrams/linalg/quaternion.html) |
| [`eigen`](api/eigen.md) | [preview](https://htmlpreview.github.io/?https://github.com/AugustinJose1221/ffitt/blob/development/docs/diagrams/linalg/eigen.html) | [eigen.html](diagrams/linalg/eigen.html) |
| [`poly`](api/poly.md) | [preview](https://htmlpreview.github.io/?https://github.com/AugustinJose1221/ffitt/blob/development/docs/diagrams/linalg/poly.html) | [poly.html](diagrams/linalg/poly.html) |
| [`lstsq`](api/lstsq.md) | [preview](https://htmlpreview.github.io/?https://github.com/AugustinJose1221/ffitt/blob/development/docs/diagrams/linalg/lstsq.html) | [lstsq.html](diagrams/linalg/lstsq.html) |
| [`vector`](api/vector.md) | [preview](https://htmlpreview.github.io/?https://github.com/AugustinJose1221/ffitt/blob/development/docs/diagrams/linalg/vector.html) | [vector.html](diagrams/linalg/vector.html) |
| [`vector2d`](api/vector2d.md) | [preview](https://htmlpreview.github.io/?https://github.com/AugustinJose1221/ffitt/blob/development/docs/diagrams/linalg/vector2d.html) | [vector2d.html](diagrams/linalg/vector2d.html) |

## Detection

| Module | Diagram | File |
|---|---|---|
| [`matched`](api/matched.md) | not yet drawn | |
| [`delay`](api/delay.md) | not yet drawn | |
| [`changepoint`](api/changepoint.md) | not yet drawn | |

## Utilities

| Module | Diagram | File |
|---|---|---|
| [`generate`](api/generate.md) | [preview](https://htmlpreview.github.io/?https://github.com/AugustinJose1221/ffitt/blob/development/docs/diagrams/util/generate.html) | [generate.html](diagrams/util/generate.html) |
| [`curve`](api/curve.md) | [preview](https://htmlpreview.github.io/?https://github.com/AugustinJose1221/ffitt/blob/development/docs/diagrams/util/curve.html) | [curve.html](diagrams/util/curve.html) |
| [`quantise`](api/quantise.md) | [preview](https://htmlpreview.github.io/?https://github.com/AugustinJose1221/ffitt/blob/development/docs/diagrams/util/quantise.html) | [quantise.html](diagrams/util/quantise.html) |
| [`stats`](api/stats.md) | [preview](https://htmlpreview.github.io/?https://github.com/AugustinJose1221/ffitt/blob/development/docs/diagrams/util/stats.html) | [stats.html](diagrams/util/stats.html) |
| [`binarysearch`](api/binarysearch.md) | [preview](https://htmlpreview.github.io/?https://github.com/AugustinJose1221/ffitt/blob/development/docs/diagrams/util/binarysearch.html) | [binarysearch.html](diagrams/util/binarysearch.html) |
| [`peakdetect`](api/peakdetect.md) | [preview](https://htmlpreview.github.io/?https://github.com/AugustinJose1221/ffitt/blob/development/docs/diagrams/util/peakdetect.html) | [peakdetect.html](diagrams/util/peakdetect.html) |
| [`valleydetect`](api/valleydetect.md) | [preview](https://htmlpreview.github.io/?https://github.com/AugustinJose1221/ffitt/blob/development/docs/diagrams/util/valleydetect.html) | [valleydetect.html](diagrams/util/valleydetect.html) |

## Core

| Module | Diagram | File |
|---|---|---|
| [`real`](api/real.md) | [preview](https://htmlpreview.github.io/?https://github.com/AugustinJose1221/ffitt/blob/development/docs/diagrams/core/real.html) | [real.html](diagrams/core/real.html) |
| [`nolibm`](api/nolibm.md) | [preview](https://htmlpreview.github.io/?https://github.com/AugustinJose1221/ffitt/blob/development/docs/diagrams/core/nolibm.html) | [nolibm.html](diagrams/core/nolibm.html) |
| [`ringbuf`](api/ringbuf.md) | [preview](https://htmlpreview.github.io/?https://github.com/AugustinJose1221/ffitt/blob/development/docs/diagrams/core/ringbuf.html) | [ringbuf.html](diagrams/core/ringbuf.html) |
| [`point2d`](api/point2d.md) | [preview](https://htmlpreview.github.io/?https://github.com/AugustinJose1221/ffitt/blob/development/docs/diagrams/core/point2d.html) | [point2d.html](diagrams/core/point2d.html) |
| [`callback`](api/callback.md) | [preview](https://htmlpreview.github.io/?https://github.com/AugustinJose1221/ffitt/blob/development/docs/diagrams/core/callback.html) | [callback.html](diagrams/core/callback.html) |
