# What each operation costs

The benchmark measures how long each operation takes, for several sizes of
input. It needs no external library:

```bash
cmake -S . -B build -DBUILD_BENCHMARK=ON && cmake --build build && ./build/benchmark
```

Each line gives the time of the fastest repeat, the mean time of all the
repeats, and the number of times the operation runs in one second. The fastest
repeat gives the best picture, because the other work of the system only makes
a repeat slower. The seed of the random numbers is the same at each run, thus
two runs compare with each other.

## The table

Every module of the library is here, with the operation a caller reaches for
most. The times were measured on one machine with GCC 13.3 and NO OPTIMISATION
ASKED FOR, which is what the build above gives. They are for comparing one
operation against another and not for promising a speed on another machine.

`scripts/benchmark_table.py` builds the benchmark at both widths, runs it, and
writes this table. Thus what the table says and what the benchmark measures
cannot drift apart. `--check` gives 1 when the table is out of date.

The 64 bit column is not always the slower one. A double is twice the memory of
a float, which costs, but a float must be widened before some arithmetic and
narrowed after it, which costs as well.

<!-- BENCHMARK TABLE BEGINS. scripts/benchmark_table.py writes it. -->

| Module | What it does | 32 bit | 64 bit |
|---|---|---:|---:|
| `ringbuf` | put one sample into a buffer of 256 | 0.03 us | 0.03 us |
| `ringbuf` | read a sample from a hundred steps ago | 0.03 us | 0.03 us |
| `ringbuf` | write the whole buffer of 256 out in order | 1.69 us | 1.69 us |
| `real` | one sine, at the width the library was built for | 0.03 us | 0.03 us |
| `real` | one square root | 0.02 us | 0.02 us |
| `real` | one exponential | 0.03 us | 0.03 us |
| `matrix` | add two 8 by 8 matrices | 0.96 us | 0.98 us |
| `matrix` | subtract two 8 by 8 matrices | 0.94 us | 0.96 us |
| `matrix` | multiply two 8 by 8 matrices | 5.25 us | 5.23 us |
| `matrix` | transpose an 8 by 8 matrix | 0.62 us | 0.62 us |
| `matrix` | multiply two 8 by 8 matrices into the caller's memory | 5.15 us | 5.23 us |
| `matrix` | invert an 8 by 8 matrix | 15.95 us | 15.81 us |
| `matrix` | the determinant of an 8 by 8 matrix | 4.01 us | 4.08 us |
| `vector` | the dot product of two vectors of 1024 | 2.53 us | 2.53 us |
| `vector` | the length of a vector of 1024 | 2.53 us | 2.54 us |
| `cmatrix` | multiply two 10 by 10 complex matrices | 26.06 us | 63.51 us |
| `cmatrix` | the determinant of a 10 by 10 complex matrix | 12.70 us | 30.25 us |
| `cmatrix` | invert a 10 by 10 complex matrix | 56.66 us | 138.25 us |
| `cnum` | multiply two complex numbers | 0.03 us | 0.04 us |
| `cnum` | divide one complex number by another | 0.04 us | 0.05 us |
| `cnum` | the size of a complex number | 0.03 us | 0.04 us |
| `eigen` | the eigenvalues and vectors of a 10 by 10 matrix | 4.04 us | 3.85 us |
| `eigen` | how badly conditioned that matrix is | 0.05 us | 0.05 us |
| `lstsq` | fit a curve of order 8 through 256 readings | 218.62 us | 219.10 us |
| `lstsq` | how well that curve holds the readings | 8.49 us | 8.75 us |
| `poly` | read a curve of order 8 at one place | 0.05 us | 0.05 us |
| `poly` | multiply two curves of order 8 | 0.27 us | 0.27 us |
| `poly` | every root of a curve of order 4 | 3.44 us | 10.02 us |
| `quaternion` | join two turns into one | 0.04 us | 0.03 us |
| `quaternion` | turn one point by a quaternion | 0.03 us | 0.03 us |
| `quaternion` | the same turn written as a 3 by 3 matrix | 0.09 us | 0.09 us |
| `quaternion` | the turn part way between two others | 0.16 us | 0.17 us |
| `quaternion` | carry a turn forward by a rate over a step | 0.11 us | 0.11 us |
| `pmatrix` | read a 10 by 10 matrix of functions at one place | 1.26 us | 1.26 us |
| `matrix` | the factor of Cholesky of a 10 by 10 matrix | 3.64 us | 3.69 us |
| `vector2d` | the dot product of two vectors of two | 0.03 us | 0.03 us |
| `vector2d` | the length of a vector of two | 0.03 us | 0.03 us |
| `cspline` | build a cubic spline through 512 points | 17.78 us | 21.41 us |
| `cspline` | read one point from a spline of 512 | 0.08 us | 0.11 us |
| `interp` | read one place from a table of 256, straight lines | 0.03 us | 0.03 us |
| `interp` | the same, smooth and never above the neighbours | 0.03 us | 0.03 us |
| `interp` | read 4096 places from that table at one call | 0.03 us | 0.03 us |
| `fft` | a 1024 point transform of a real signal | 70.40 us | 71.04 us |
| `fft` | the same 1024 points, only the bins that hold new information | 37.27 us | 38.15 us |
| `fft` | a half spectrum of 1024 points back into a real signal | 99.06 us | 125.38 us |
| `fft` | the same half spectrum back by the faster method | 39.56 us | 42.91 us |
| `fft` | a 1024 point transform of a complex signal | 63.07 us | 63.48 us |
| `fft` | a 1024 point inverse transform | 91.73 us | 113.43 us |
| `fft` | the size of every bin of a 1024 point spectrum | 4.94 us | 5.21 us |
| `bluestein` | a 1000 point transform, a size no power of two | 381.61 us | 459.79 us |
| `dct` | a 1024 point cosine transform | 11948.58 us | 18519.21 us |
| `dct` | a 1024 point inverse cosine transform | 18341.00 us | 25027.28 us |
| `dwt` | one level of a wavelet over 1024 samples | 11.97 us | 12.12 us |
| `dwt` | rebuild 1024 samples from one wavelet level | 7.46 us | 7.18 us |
| `dwt` | four levels of a wavelet over 1024 samples | 25.89 us | 26.23 us |
| `dwt` | take the small wavelet values out of 1024 | 1.90 us | 1.95 us |
| `window` | build a window of Blackman and Harris over 1024 | 33.28 us | 58.12 us |
| `window` | put a window over 1024 samples | 2.55 us | 2.66 us |
| `window` | the noise bandwidth of a window of 1024 | 2.60 us | 2.61 us |
| `hilbert` | the analytic signal of 1024 samples | 137.71 us | 165.95 us |
| `hilbert` | the envelope of 1024 samples | 6.64 us | 16.03 us |
| `hilbert` | the frequency at each of 1024 samples | 49.47 us | 53.47 us |
| `cepstrum` | the cepstrum of 1024 samples | 92.88 us | 107.88 us |
| `cepstrum` | find the pitch in a cepstrum of 1024 | 0.88 us | 0.88 us |
| `goertzel` | watch one frequency over a block of 1024 | 6.47 us | 6.47 us |
| `goertzel` | read how much of that frequency was there | 0.03 us | 0.03 us |
| `correlate` | 4096 samples against themselves at every lag | 21065.30 us | 21172.60 us |
| `correlate` | the same by the transform | 1705.18 us | 1936.69 us |
| `correlate` | 4096 samples against another signal at 512 lags | 4946.59 us | 4992.04 us |
| `correlate` | find the period of 4096 samples | 14028.62 us | 13669.78 us |
| `convolve` | slide a shape of 512 along 4096 samples | 6406.51 us | 6445.19 us |
| `convolve` | the same by the transform | 2457.11 us | 2747.70 us |
| `psd` | the spectrum of 4096 samples by the way of Welch | 280.60 us | 288.95 us |
| `psd` | the power between two frequencies of that spectrum | 1.16 us | 1.13 us |
| `csd` | the cross spectrum of two signals of 4096 | 675.67 us | 799.56 us |
| `csd` | how much two signals of 4096 agree, bin by bin | 675.11 us | 797.95 us |
| `csd` | the transfer between two signals of 4096 | 676.15 us | 799.60 us |
| `stft` | 4096 samples into frames of 256, hopping 64 | 521.85 us | 542.38 us |
| `stft` | rebuild the 4096 samples from those frames | 620.87 us | 676.43 us |
| `spectrogram` | a picture in decibel from those frames | 124.64 us | 228.23 us |
| `spectrogram` | hold that picture against its own loudest point | 34.97 us | 35.31 us |
| `hht` | amplitude and frequency of one mode of 1024 | 227.31 us | 274.22 us |
| `hht` | the mean frequency of that mode | 3.31 us | 3.31 us |
| `fir` | design a low pass of 33 coefficients | 0.86 us | 1.30 us |
| `fir` | 4096 samples through a filter of 33 with no feedback | 416.56 us | 415.19 us |
| `iir` | design a low pass of two sections | 0.10 us | 0.13 us |
| `iir` | 4096 samples through a filter of two sections | 78.18 us | 75.64 us |
| `filtfilt` | 4096 samples both ways, thus with no delay at all | 153.34 us | 154.06 us |
| `filtfilt` | the same with a filter of 33 and no feedback | 863.29 us | 857.36 us |
| `adaptive` | 4096 samples through a filter of 32 that learns | 2153.99 us | 2141.68 us |
| `rls` | 4096 samples through a filter of 32 that learns fast | 68240.50 us | 69558.97 us |
| `lattice` | 4096 samples through eight stages that learn | 1146.14 us | 1228.86 us |
| `savgol` | design a smoother of 33 that keeps a cubic | 11.02 us | 11.19 us |
| `savgol` | smooth 4096 samples and keep the shape of the peaks | 486.85 us | 488.21 us |
| `medfilt` | the middle value of a window of 33 over 4096 samples | 838.85 us | 844.54 us |
| `hampel` | take the wild readings out of 4096 samples | 5101.22 us | 5130.98 us |
| `dcblock` | take the standing level out of 4096 samples | 23.74 us | 23.75 us |
| `detrend` | find the drift under 4096 samples | 32.26 us | 31.71 us |
| `detrend` | find that drift and take it away | 62.69 us | 63.24 us |
| `detrend` | take a drift already known away from 4096 samples | 30.39 us | 29.86 us |
| `farrow` | delay 4096 samples by half a sample | 395.76 us | 395.21 us |
| `resample` | 4096 samples down to a quarter of the rate | 669.64 us | 698.36 us |
| `resample` | 4096 samples up to four times the rate | 2911.26 us | 2908.37 us |
| `movavg` | one sample through a moving mean of 64 | 0.05 us | 0.05 us |
| `fir` | one sample through an equal fir of 64, the mean the slow way | 0.21 us | 0.21 us |
| `kalman` | one prediction of a Kalman filter over four states | 2.22 us | 2.22 us |
| `kalman` | one full step of a Kalman filter over four states | 4.67 us | 4.61 us |
| `ekf` | one step of a bending filter over four states | 7.36 us | 5.49 us |
| `ukf` | one step of a filter that places points, four states | 10.40 us | 10.46 us |
| `pll` | hold a loop on a tone through 4096 samples | 0.03 us | 0.03 us |
| `propagate` | carry four states one step by the way of Runge | 0.11 us | 0.10 us |
| `propagate` | carry four states across a hundred such steps | 8.97 us | 9.09 us |
| `changepoint` | watch 4096 readings for the moment a level moves | 43.80 us | 43.67 us |
| `matched` | look for a shape of 64 all through 4096 samples | 878.48 us | 661.46 us |
| `matched` | find where that shape fits best | 884.67 us | 661.41 us |
| `delay` | how far two signals of 1024 stand apart, by lag | 3225.79 us | 3196.55 us |
| `delay` | the same to a fraction of a sample, by phase | 145.47 us | 147.42 us |
| `emd` | sift 256 samples into three modes | 3.06 us | 3.06 us |
| `imf` | take the memory for a mode of 1024 points | 0.10 us | 0.08 us |
| `stats` | the mean of 4096 readings | 24.52 us | 24.25 us |
| `stats` | how far 4096 readings spread | 53.70 us | 52.95 us |
| `stats` | the root mean square of 4096 readings | 26.71 us | 26.80 us |
| `stats` | the middle of 4096 readings | 58.02 us | 59.27 us |
| `stats` | the spread of 4096 readings, wild ones and all | 179.78 us | 179.84 us |
| `peakdetect` | every peak in 4096 samples | 16.93 us | 17.11 us |
| `peakdetect` | the peaks in 4096 samples that pass the rules | 1632.10 us | 1637.02 us |
| `peakdetect` | how far one peak stands above its neighbours | 0.03 us | 0.03 us |
| `valleydetect` | every valley in 4096 samples | 13.94 us | 23.02 us |
| `generate` | make 4096 samples of a sine | 60.88 us | 81.42 us |
| `generate` | make 4096 samples of a square wave with no aliases | 90.88 us | 90.81 us |
| `generate` | make 4096 samples of noise | 51.49 us | 51.40 us |
| `quantise` | round 4096 samples to 12 bits | 54.37 us | 54.88 us |
| `quantise` | the same with a little noise added first | 140.74 us | 139.66 us |
| `curve` | draw a bell curve over 4096 places | 73.56 us | 87.98 us |
| `curve` | read a bell curve at one place | 0.04 us | 0.04 us |
| `binarysearch` | find a value in a sorted list of 256 | 0.05 us | 0.05 us |

<!-- BENCHMARK TABLE ENDS. -->
