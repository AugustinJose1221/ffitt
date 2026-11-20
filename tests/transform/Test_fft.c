#include "unity.h"
#include "real_assert.h"
#include "fft.h"
#include "cnum.h"
#include <stdlib.h>
#include <math.h>

#define TOLERANCE   REAL_C(0.001)
#define PI          REAL_C(3.14159265358979323846)

void setUp(void)
{

}

void tearDown(void)
{

}

static void fill_sine(real_t* signal, uint32_t size, real_t cycles, real_t amplitude)
{
    for(uint32_t index = 0; index < size; index++)
    {
        signal[index] = amplitude * REAL_SIN((REAL_C(2.0)*PI*cycles*(real_t)index) / (real_t)size);
    }
}

void test_fft_is_valid_size(void)
{
    TEST_ASSERT_EQUAL(true, fft_is_valid_size(2));
    TEST_ASSERT_EQUAL(true, fft_is_valid_size(8));
    TEST_ASSERT_EQUAL(true, fft_is_valid_size(1024));
    TEST_ASSERT_EQUAL(false, fft_is_valid_size(0));
    TEST_ASSERT_EQUAL(false, fft_is_valid_size(1));
    TEST_ASSERT_EQUAL(false, fft_is_valid_size(3));
    TEST_ASSERT_EQUAL(false, fft_is_valid_size(100));
}

void test_fft_alloc(void)
{
    fft_t fft = fft_alloc(16);

    TEST_ASSERT_EQUAL(16, fft.size);
    TEST_ASSERT_EQUAL(true, fft.dynamic_alloc);
    TEST_ASSERT_NOT_NULL(fft.twiddle);
    TEST_ASSERT_NOT_NULL(fft.reverse);

    fft_free(&fft);
}

void test_fft_static_alloc(void)
{
    cnum_t twiddle[FFT_TWIDDLE_COUNT(8)];
    uint32_t reverse[FFT_REVERSE_COUNT(8)];

    fft_t fft = fft_static_alloc(8, twiddle, reverse);

    TEST_ASSERT_EQUAL(8, fft.size);
    TEST_ASSERT_EQUAL(false, fft.dynamic_alloc);
    TEST_ASSERT_EQUAL_PTR(twiddle, fft.twiddle);
    TEST_ASSERT_EQUAL_PTR(reverse, fft.reverse);

    fft_free(&fft);

    // The memory belongs to the caller, thus the pointers do not change.
    TEST_ASSERT_EQUAL_PTR(twiddle, fft.twiddle);
}

void test_fft_the_bit_reversal_table_of_size_eight(void)
{
    // With 3 bits: 0,1,2,3,4,5,6,7 becomes 0,4,2,6,1,5,3,7.
    fft_t fft = fft_alloc(8);
    uint32_t expected[8] = {0, 4, 2, 6, 1, 5, 3, 7};

    for(uint32_t index = 0; index < 8; index++)
    {
        TEST_ASSERT_EQUAL(expected[index], fft.reverse[index]);
    }

    fft_free(&fft);
}

void test_fft_of_a_constant_signal_holds_only_the_first_bin(void)
{
    // A signal that does not change holds one frequency only, which is zero.
    // The first bin then holds the sum of every sample.
    fft_t fft = fft_alloc(16);
    cnum_t data[16];

    for(uint32_t index = 0; index < 16; index++)
    {
        data[index] = cnum_make(REAL_C(2.0), REAL_C(0.0));
    }

    fft_forward(&fft, data);

    TEST_ASSERT_REAL_WITHIN(TOLERANCE, REAL_C(32.0), data[0].re);
    TEST_ASSERT_REAL_WITHIN(TOLERANCE, REAL_C(0.0), data[0].im);
    for(uint32_t index = 1; index < 16; index++)
    {
        TEST_ASSERT_REAL_WITHIN(TOLERANCE, REAL_C(0.0), cnum_magnitude(data[index]));
    }

    fft_free(&fft);
}

void test_fft_of_a_single_sine_holds_two_bins(void)
{
    // A sine of 3 cycles over the window gives a peak at the bin 3 and its
    // mirror at the bin size-3. Each peak holds half of the amplitude, times
    // the size, thus 32*1/2 = 16 for an amplitude of 1.
    const uint32_t size = 64;
    fft_t fft = fft_alloc(size);
    real_t signal[64];
    cnum_t spectrum[64];
    real_t magnitude[64];

    fill_sine(signal, size, REAL_C(3.0), REAL_C(1.0));
    fft_forward_real(&fft, signal, spectrum);
    fft_magnitude(spectrum, magnitude, size);

    TEST_ASSERT_REAL_WITHIN(REAL_C(0.01), REAL_C(32.0), magnitude[3]);
    TEST_ASSERT_REAL_WITHIN(REAL_C(0.01), REAL_C(32.0), magnitude[size-3]);

    for(uint32_t index = 0; index < size; index++)
    {
        if(index != 3 && index != (size-3))
        {
            TEST_ASSERT_REAL_WITHIN(REAL_C(0.01), REAL_C(0.0), magnitude[index]);
        }
    }

    fft_free(&fft);
}

void test_fft_finds_the_frequency_of_the_strongest_bin(void)
{
    const uint32_t size = 128;
    fft_t fft = fft_alloc(size);
    real_t signal[128];
    cnum_t spectrum[128];
    real_t magnitude[128];

    fill_sine(signal, size, REAL_C(10.0), REAL_C(1.0));
    fft_forward_real(&fft, signal, spectrum);
    fft_magnitude(spectrum, magnitude, size);

    uint32_t strongest = 0;
    for(uint32_t index = 1; index <= (size/2); index++)
    {
        if(magnitude[index] > magnitude[strongest])
        {
            strongest = index;
        }
    }

    TEST_ASSERT_EQUAL(10, strongest);
    // With a sample rate of 128 hertz the window holds one second, thus the
    // bin 10 is 10 hertz.
    TEST_ASSERT_REAL_WITHIN(TOLERANCE, REAL_C(10.0),
                             fft_bin_frequency(strongest, size, REAL_C(128.0)));

    fft_free(&fft);
}

void test_fft_the_inverse_gives_the_first_signal_again(void)
{
    const uint32_t size = 64;
    fft_t fft = fft_alloc(size);
    real_t signal[64];
    cnum_t data[64];

    for(uint32_t index = 0; index < size; index++)
    {
        signal[index] = REAL_SIN((real_t)index) + (REAL_C(0.5)*REAL_COS(REAL_C(3.0)*(real_t)index));
        data[index] = cnum_make(signal[index], REAL_C(0.0));
    }

    fft_forward(&fft, data);
    fft_inverse(&fft, data);

    for(uint32_t index = 0; index < size; index++)
    {
        TEST_ASSERT_REAL_WITHIN(TOLERANCE, signal[index], data[index].re);
        TEST_ASSERT_REAL_WITHIN(TOLERANCE, REAL_C(0.0), data[index].im);
    }

    fft_free(&fft);
}

void test_fft_of_two_sines_holds_both_frequencies(void)
{
    const uint32_t size = 128;
    fft_t fft = fft_alloc(size);
    real_t signal[128];
    cnum_t spectrum[128];
    real_t magnitude[128];

    for(uint32_t index = 0; index < size; index++)
    {
        signal[index] = REAL_SIN((REAL_C(2.0)*PI*REAL_C(5.0)*(real_t)index)/(real_t)size)
                        + (REAL_C(0.5)*REAL_SIN((REAL_C(2.0)*PI*REAL_C(20.0)*(real_t)index)/(real_t)size));
    }

    fft_forward_real(&fft, signal, spectrum);
    fft_magnitude(spectrum, magnitude, size);

    // The first sine has two times the amplitude of the second one, thus its
    // bin is two times as large.
    TEST_ASSERT_REAL_WITHIN(REAL_C(0.05), REAL_C(64.0), magnitude[5]);
    TEST_ASSERT_REAL_WITHIN(REAL_C(0.05), REAL_C(32.0), magnitude[20]);
    TEST_ASSERT_REAL_WITHIN(REAL_C(0.05), REAL_C(0.0), magnitude[12]);

    fft_free(&fft);
}

void test_fft_power_is_the_square_of_the_magnitude(void)
{
    cnum_t data[4];
    real_t magnitude[4];
    real_t power[4];

    data[0] = cnum_make(REAL_C(3.0), REAL_C(4.0));
    data[1] = cnum_make(REAL_C(0.0), REAL_C(0.0));
    data[2] = cnum_make(-REAL_C(1.0), REAL_C(0.0));
    data[3] = cnum_make(REAL_C(0.0), REAL_C(2.0));

    fft_magnitude(data, magnitude, 4);
    fft_power(data, power, 4);

    for(uint32_t index = 0; index < 4; index++)
    {
        TEST_ASSERT_REAL_WITHIN(TOLERANCE, magnitude[index]*magnitude[index],
                                 power[index]);
    }
    TEST_ASSERT_REAL_WITHIN(TOLERANCE, REAL_C(5.0), magnitude[0]);
    TEST_ASSERT_REAL_WITHIN(TOLERANCE, REAL_C(25.0), power[0]);
}

void test_fft_bin_frequency(void)
{
    // A window of 8 points at 8 hertz holds one second.
    TEST_ASSERT_REAL_WITHIN(TOLERANCE, REAL_C(0.0), fft_bin_frequency(0, 8, REAL_C(8.0)));
    TEST_ASSERT_REAL_WITHIN(TOLERANCE, REAL_C(1.0), fft_bin_frequency(1, 8, REAL_C(8.0)));
    TEST_ASSERT_REAL_WITHIN(TOLERANCE, REAL_C(4.0), fft_bin_frequency(4, 8, REAL_C(8.0)));
    // The bin above the middle mirrors a lower bin.
    TEST_ASSERT_REAL_WITHIN(TOLERANCE, -REAL_C(3.0), fft_bin_frequency(5, 8, REAL_C(8.0)));
    TEST_ASSERT_REAL_WITHIN(TOLERANCE, -REAL_C(1.0), fft_bin_frequency(7, 8, REAL_C(8.0)));
}

void test_fft_the_smallest_size_works(void)
{
    fft_t fft = fft_alloc(2);
    cnum_t data[2];

    data[0] = cnum_make(REAL_C(1.0), REAL_C(0.0));
    data[1] = cnum_make(REAL_C(3.0), REAL_C(0.0));

    fft_forward(&fft, data);

    // For two points the result is the sum and the difference.
    TEST_ASSERT_REAL_WITHIN(TOLERANCE, REAL_C(4.0), data[0].re);
    TEST_ASSERT_REAL_WITHIN(TOLERANCE, -REAL_C(2.0), data[1].re);

    fft_free(&fft);
}

void test_fft_a_static_transform_gives_the_same_result_as_a_dynamic_one(void)
{
    const uint32_t size = 32;
    cnum_t twiddle[FFT_TWIDDLE_COUNT(32)];
    uint32_t reverse[FFT_REVERSE_COUNT(32)];

    fft_t dynamic_fft = fft_alloc(size);
    fft_t static_fft = fft_static_alloc(size, twiddle, reverse);

    cnum_t first[32];
    cnum_t second[32];

    for(uint32_t index = 0; index < size; index++)
    {
        real_t value = REAL_SIN(REAL_C(0.3)*(real_t)index) + (real_t)index;
        first[index] = cnum_make(value, REAL_C(0.0));
        second[index] = cnum_make(value, REAL_C(0.0));
    }

    fft_forward(&dynamic_fft, first);
    fft_forward(&static_fft, second);

    for(uint32_t index = 0; index < size; index++)
    {
        TEST_ASSERT_EQUAL(true, cnum_is_near(first[index], second[index], TOLERANCE));
    }

    fft_free(&dynamic_fft);
    fft_free(&static_fft);
}

void test_fft_free_releases_a_dynamic_transform(void)
{
    fft_t fft = fft_alloc(8);

    fft_free(&fft);

    TEST_ASSERT_NULL(fft.twiddle);
    TEST_ASSERT_EQUAL(false, fft.dynamic_alloc);

    // A second call must do nothing.
    fft_free(&fft);
    TEST_ASSERT_NULL(fft.twiddle);
}

void test_fft_inverse_real_gives_the_signal_back(void)
{
    // The round trip. A real signal, transformed and brought back from the
    // half spectrum alone, must be the signal it started as.
    fft_t fft = fft_alloc(64);
    real_t input[64];
    real_t output[64];
    cnum_t spectrum[64];
    cnum_t work[64];

    for(uint32_t index = 0; index < 64u; index++)
    {
        input[index] = REAL_SIN(REAL_C(2.0) * REAL_PI * REAL_C(5.0)
                                * (real_t)index / REAL_C(64.0))
                       + (REAL_C(0.5) * REAL_COS(REAL_C(2.0) * REAL_PI
                          * REAL_C(11.0) * (real_t)index / REAL_C(64.0)));
    }

    fft_forward_real(&fft, input, spectrum);

    // Only the first half and one more is handed back, and that is enough.
    fft_inverse_real(&fft, spectrum, output, work);

    for(uint32_t index = 0; index < 64u; index++)
    {
        TEST_ASSERT_REAL_WITHIN(REAL_C(0.001), input[index], output[index]);
    }

    fft_free(&fft);
}

void test_fft_real_bin_count(void)
{
    // Half the size and one more: bin 0 and the bin at half the sample rate
    // are both counted.
    TEST_ASSERT_EQUAL(33, FFT_REAL_BIN_COUNT(64));
    TEST_ASSERT_EQUAL(9, FFT_REAL_BIN_COUNT(16));
}

void test_fft_inverse_real_drops_what_no_real_signal_could_have(void)
{
    // Bin 0 and the bin at half the sample rate sit on their own mirror, thus
    // no real signal can give either one an imaginary part. A spectrum built
    // by hand, or turned in phase by a filter, can. This holds that such a
    // part is dropped and not carried into the answer.
    fft_t fft = fft_alloc(16);
    real_t clean[16];
    real_t dirty[16];
    cnum_t spectrum[9];
    cnum_t work[16];

    for(uint32_t index = 0; index < 9u; index++)
    {
        spectrum[index] = cnum_zero();
    }

    // A level of 16, which gives a flat signal of 1.
    spectrum[0] = cnum_make(REAL_C(16.0), REAL_C(0.0));
    fft_inverse_real(&fft, spectrum, clean, work);

    // The same, with an imaginary part on bin 0 and on the top bin that no
    // real signal could have put there.
    spectrum[0] = cnum_make(REAL_C(16.0), REAL_C(9.0));
    spectrum[8] = cnum_make(REAL_C(0.0), REAL_C(4.0));
    fft_inverse_real(&fft, spectrum, dirty, work);

    for(uint32_t index = 0; index < 16u; index++)
    {
        TEST_ASSERT_REAL_WITHIN(REAL_C(0.001), REAL_C(1.0), clean[index]);
        TEST_ASSERT_REAL_WITHIN(REAL_C(0.001), clean[index], dirty[index]);
    }

    fft_free(&fft);
}

// THE FASTER ROAD FOR A REAL SIGNAL.
//
// fft_forward_half and fft_inverse_half must give what fft_forward_real and
// fft_inverse_real give, to the rounding of the width.
//
// THE TOLERANCE IS A SHARE OF THE LARGEST VALUE, AND NOT A FIXED AMOUNT. The
// rounding of a transform grows with the size of the values and with the
// logarithm of the size. A fixed amount small enough to mean something at a
// size of 2 is broken by honest rounding at 1024: it was written that way
// first, and a bin of 4.13 at 32 bits differed by 6.7e-6, which is a share of
// 1.6e-6. Measured over every size from 2 to 4096, the worst share is 5.4e-7
// at 32 bits and 9.4e-16 at 64, and the shares below stand clear of both.
//
// A value that is small and known exactly, as in the transform by hand, is
// held to a fixed amount instead.

#ifdef FFITT_REAL_64
#define HALF_SHARE      REAL_C(1e-13)
#define HALF_TOLERANCE  REAL_C(1e-12)
#else
#define HALF_SHARE      REAL_C(4e-6)
#define HALF_TOLERANCE  REAL_C(5e-6)
#endif

// The largest size of any value in a list, which the share is a share of.
static real_t largest_of(const real_t* values, uint32_t count)
{
    real_t largest = REAL_C(0.0);
    for(uint32_t index = 0; index < count; index++)
    {
        real_t size = REAL_ABS(values[index]);
        largest = (size > largest) ? size : largest;
    }
    return largest;
}

static real_t largest_bin_of(const cnum_t* bins, uint32_t count)
{
    real_t largest = REAL_C(0.0);
    for(uint32_t index = 0; index < count; index++)
    {
        real_t size = cnum_magnitude(bins[index]);
        largest = (size > largest) ? size : largest;
    }
    return largest;
}

// A signal with something at every frequency, so that no bin is nothing by luck.
static void fill_with_noise(real_t* signal, uint32_t size, uint32_t seed)
{
    srand(seed);
    for(uint32_t index = 0; index < size; index++)
    {
        signal[index] = ((real_t)rand() / (real_t)RAND_MAX) - REAL_C(0.5);
    }
}

void test_fft_forward_half_gives_the_bins_of_fft_forward_real_at_every_size(void)
{
    // Every size the module takes, from the smallest. The smallest sizes are
    // where an untwist goes wrong: at 2 there is no pair at all, and at 4 the
    // only bin besides the two ends is its own mirror.
    for(uint32_t size = 2u; size <= 1024u; size *= 2u)
    {
        fft_t fft = fft_alloc(size);
        real_t* signal = (real_t*)malloc(sizeof(real_t) * size);
        cnum_t* full = (cnum_t*)malloc(sizeof(cnum_t) * size);
        cnum_t* half = (cnum_t*)malloc(sizeof(cnum_t) * FFT_REAL_BIN_COUNT(size));

        fill_with_noise(signal, size, size);
        fft_forward_real(&fft, signal, full);
        fft_forward_half(&fft, signal, half);

        real_t allowed = HALF_SHARE * largest_bin_of(full, FFT_REAL_BIN_COUNT(size));

        for(uint32_t bin = 0; bin < FFT_REAL_BIN_COUNT(size); bin++)
        {
            TEST_ASSERT_REAL_WITHIN(allowed, full[bin].re, half[bin].re);
            TEST_ASSERT_REAL_WITHIN(allowed, full[bin].im, half[bin].im);
        }

        free(signal);
        free(full);
        free(half);
        fft_free(&fft);
    }
}

void test_fft_forward_half_of_four_samples_is_the_transform_by_hand(void)
{
    // Worked by hand from the definition, for the size where the middle bin is
    // its own mirror and is written exactly rather than through the table.
    fft_t fft = fft_alloc(4);
    real_t signal[4] = {REAL_C(1.0), REAL_C(2.0), REAL_C(3.0), REAL_C(4.0)};
    cnum_t bins[FFT_REAL_BIN_COUNT(4)];

    fft_forward_half(&fft, signal, bins);

    TEST_ASSERT_REAL_WITHIN(HALF_TOLERANCE, REAL_C(10.0), bins[0].re);   // the sum
    TEST_ASSERT_REAL_WITHIN(HALF_TOLERANCE, REAL_C(0.0), bins[0].im);
    TEST_ASSERT_REAL_WITHIN(HALF_TOLERANCE, REAL_C(-2.0), bins[1].re);   // (1-3) - i(2-4)
    TEST_ASSERT_REAL_WITHIN(HALF_TOLERANCE, REAL_C(2.0), bins[1].im);
    TEST_ASSERT_REAL_WITHIN(HALF_TOLERANCE, REAL_C(-2.0), bins[2].re);   // 1-2+3-4
    TEST_ASSERT_REAL_WITHIN(HALF_TOLERANCE, REAL_C(0.0), bins[2].im);

    fft_free(&fft);
}

void test_fft_forward_half_puts_the_highest_frequency_in_the_last_bin(void)
{
    // A signal that turns once for every two samples is the highest the sample
    // rate can carry. All of it must land in bin size/2, and none elsewhere.
    fft_t fft = fft_alloc(16);
    real_t signal[16];
    cnum_t bins[FFT_REAL_BIN_COUNT(16)];

    for(uint32_t index = 0; index < 16u; index++)
    {
        signal[index] = ((index % 2u) == 0u) ? REAL_C(1.0) : REAL_C(-1.0);
    }

    fft_forward_half(&fft, signal, bins);

    TEST_ASSERT_REAL_WITHIN(HALF_TOLERANCE, REAL_C(16.0), bins[8].re);
    for(uint32_t bin = 0; bin < 8u; bin++)
    {
        TEST_ASSERT_REAL_WITHIN(HALF_TOLERANCE, REAL_C(0.0), cnum_magnitude(bins[bin]));
    }

    fft_free(&fft);
}

void test_fft_inverse_half_gives_what_fft_inverse_real_gives(void)
{
    // A half spectrum of noise, with imaginary parts at bin 0 and bin size/2
    // that no real signal can give. Both functions must drop them alike.
    for(uint32_t size = 2u; size <= 1024u; size *= 2u)
    {
        uint32_t bins = FFT_REAL_BIN_COUNT(size);
        fft_t fft = fft_alloc(size);
        cnum_t* spectrum = (cnum_t*)malloc(sizeof(cnum_t) * bins);
        real_t* plain = (real_t*)malloc(sizeof(real_t) * size);
        real_t* fast = (real_t*)malloc(sizeof(real_t) * size);
        cnum_t* plain_work = (cnum_t*)malloc(sizeof(cnum_t) * size);
        cnum_t* fast_work = (cnum_t*)malloc(sizeof(cnum_t) * (size / 2u));

        srand(size + 7u);
        for(uint32_t bin = 0; bin < bins; bin++)
        {
            spectrum[bin] = cnum_make(((real_t)rand() / (real_t)RAND_MAX) - REAL_C(0.5),
                                      ((real_t)rand() / (real_t)RAND_MAX) - REAL_C(0.5));
        }

        fft_inverse_real(&fft, spectrum, plain, plain_work);
        fft_inverse_half(&fft, spectrum, fast, fast_work);

        real_t allowed = HALF_SHARE * largest_of(plain, size);

        for(uint32_t index = 0; index < size; index++)
        {
            TEST_ASSERT_REAL_WITHIN(allowed, plain[index], fast[index]);
        }

        free(spectrum);
        free(plain);
        free(fast);
        free(plain_work);
        free(fast_work);
        fft_free(&fft);
    }
}

void test_fft_half_gives_the_signal_back(void)
{
    fft_t fft = fft_alloc(256);
    real_t signal[256];
    real_t back[256];
    cnum_t bins[FFT_REAL_BIN_COUNT(256)];
    cnum_t work[128];

    fill_with_noise(signal, 256u, 99u);
    fft_forward_half(&fft, signal, bins);
    fft_inverse_half(&fft, bins, back, work);

    real_t allowed = HALF_SHARE * largest_of(signal, 256u);

    for(uint32_t index = 0; index < 256u; index++)
    {
        TEST_ASSERT_REAL_WITHIN(allowed, signal[index], back[index]);
    }

    fft_free(&fft);
}

void test_fft_half_needs_no_heap_with_the_tables_of_a_static_transform(void)
{
    // The faster road reads the tables of the fft_t it is given and takes no
    // memory of its own, thus a transform built on memory the caller holds
    // serves it as well as one built on the heap.
    cnum_t twiddle[FFT_TWIDDLE_COUNT(64)];
    uint32_t reverse[FFT_REVERSE_COUNT(64)];
    fft_t fixed = fft_static_alloc(64, twiddle, reverse);
    fft_t heap = fft_alloc(64);
    real_t signal[64];
    cnum_t from_fixed[FFT_REAL_BIN_COUNT(64)];
    cnum_t from_heap[FFT_REAL_BIN_COUNT(64)];

    fill_with_noise(signal, 64u, 5u);
    fft_forward_half(&fixed, signal, from_fixed);
    fft_forward_half(&heap, signal, from_heap);

    for(uint32_t bin = 0; bin < FFT_REAL_BIN_COUNT(64); bin++)
    {
        TEST_ASSERT_EQUAL_MEMORY(&from_heap[bin], &from_fixed[bin], sizeof(cnum_t));
    }

    fft_free(&fixed);
    fft_free(&heap);
}
