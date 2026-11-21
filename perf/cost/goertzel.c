// WHAT THE HEADER OF goertzel CLAIMS.
//
//   "MEASURED ON A BLOCK OF 1024, built with optimisation, one frequency
//    costs less than half of fft_forward_real_bins, and two or three cost as much
//    as that transform. Thus for a block that is in memory, use this algorithm
//    for one or two frequencies and the transform for more."
//
// This is a crossover and it is held from both sides: one frequency below it,
// and 16 above it.
//
// WHAT IS SET AGAINST WHAT. One transform of the block gives EVERY frequency
// at one time, thus it is one measurement whatever the caller wanted. This
// algorithm gives one frequency, thus asking for k of them means running it k
// times over the same block. The transform is given the same block through
// fft_forward_real_bins, which is the cheapest call for a caller who holds a real
// signal.
//
// THE HEADER ONCE SAID "about log2(n)", which is 10 here, and these tests were
// held at 2 and at 128 frequencies against fft_forward_real. Both held, and
// the words were still wrong: the crossover was at about four frequencies
// against that transform, and is at two or three against the faster one.
// A claim held only far from the place it names says nothing about that
// place. Thus 16 is chosen to stand near the crossover and still clear of it.

#include <perf/cost/cost.h>

#include <ffitt/transform/goertzel.h>
#include <ffitt/transform/fft.h>

#include <stdlib.h>

#define GOERTZEL_BLOCK          1024u
#define GOERTZEL_SAMPLE_RATE    REAL_C(8000.0)
#define GOERTZEL_FEW            1u
#define GOERTZEL_MANY           16u
#define GOERTZEL_BLOCKS         200u
#define GOERTZEL_REPEATS        7u

static real_t goertzel_input[GOERTZEL_BLOCK];
static cnum_t goertzel_spectrum[FFT_REAL_BIN_COUNT(GOERTZEL_BLOCK)];

// The frequencies are spread over the band that the sample rate can carry, so
// that no two of them are the same and none falls above half the rate.
static real_t goertzel_frequency(uint32_t index, uint32_t count)
{
    return (GOERTZEL_SAMPLE_RATE * REAL_C(0.4) * (real_t)(index + 1u))
           / (real_t)count;
}

static double goertzel_time_of_watching(uint32_t count)
{
    double seconds;

    COST_MEASURE(seconds, 1u,
    {
        for(uint32_t block = 0u; block < GOERTZEL_BLOCKS; block++)
        {
            for(uint32_t which = 0u; which < count; which++)
            {
                goertzel_t watcher = goertzel_init(goertzel_frequency(which,
                                                                      count),
                                                   GOERTZEL_SAMPLE_RATE,
                                                   GOERTZEL_BLOCK);

                goertzel_process_block(&watcher, goertzel_input,
                                       GOERTZEL_BLOCK);

                cost_sink += goertzel_magnitude_squared(&watcher);
            }
        }
    });

    return seconds;
}

static double goertzel_time_of_the_transform(void)
{
    double seconds;
    fft_t fft = fft_alloc(GOERTZEL_BLOCK);

    COST_MEASURE(seconds, 1u,
    {
        for(uint32_t block = 0u; block < GOERTZEL_BLOCKS; block++)
        {
            fft_forward_real_bins(&fft, goertzel_input, goertzel_spectrum);
            cost_sink += goertzel_spectrum[1].re;
        }
    });

    fft_free(&fft);

    return seconds;
}

void run_goertzel_cost_tests(void)
{
    double watching_few = 0.0;
    double watching_many = 0.0;
    double the_transform = 0.0;

    for(uint32_t index = 0u; index < GOERTZEL_BLOCK; index++)
    {
        goertzel_input[index] = cost_random_value();
    }

    // One run of each, in turn, for as many rounds as there were once
    // runs. cost.h says why the two sides of a claim are not measured
    // one after the other.
    for(uint32_t round = 0u; round < GOERTZEL_REPEATS; round++)
    {
        cost_keep_fastest(&watching_few, goertzel_time_of_watching(GOERTZEL_FEW), round);
        cost_keep_fastest(&watching_many, goertzel_time_of_watching(GOERTZEL_MANY), round);
        cost_keep_fastest(&the_transform, goertzel_time_of_the_transform(), round);
    }

    cost_claim_at_least("goertzel",
                        "one frequency costs less than the faster transform",
                        the_transform / watching_few, 1.5);

    cost_claim_at_least("goertzel",
                        "at 16 frequencies the transform costs far less",
                        watching_many / the_transform, 3.0);
}
