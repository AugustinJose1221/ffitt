// WHAT THE HEADER OF fft CLAIMS.
//
//   "That costs a transform of half the size and one pass over the bins,
//    against a transform of the whole size for fft_forward_real."
//
// A transform of half the size is a little less than half the work, and the
// pass over the bins adds some back. Thus the claim is about two times, and it
// is held at 1.4 for the forward road. The inverse road gains more, because
// fft_inverse_real first rebuilds the mirrored half and then does a whole
// complex transform, and it is held at 1.5.
//
// WHAT IS SET AGAINST WHAT. Each road is given the same signal, or the same
// half spectrum, and the same fft_t. The plain road and the faster road give
// the same bins, which the unit tests hold, thus only the time differs.

#include <perf/cost/cost.h>

#include <ffitt/transform/fft.h>

#define FFT_COST_SIZE       1024u
#define FFT_COST_BLOCKS     400u
#define FFT_COST_REPEATS    7u

static real_t fft_cost_signal[FFT_COST_SIZE];
static real_t fft_cost_answer[FFT_COST_SIZE];
static cnum_t fft_cost_full[FFT_COST_SIZE];
static cnum_t fft_cost_bins[FFT_REAL_BIN_COUNT(FFT_COST_SIZE)];
static cnum_t fft_cost_work[FFT_COST_SIZE];

static double fft_cost_time_forward(fft_t* fft, bool faster)
{
    double seconds;

    COST_MEASURE(seconds, 1u,
    {
        for(uint32_t block = 0u; block < FFT_COST_BLOCKS; block++)
        {
            if(faster)
            {
                fft_forward_half(fft, fft_cost_signal, fft_cost_bins);
                cost_sink += fft_cost_bins[1].re;
            }
            else
            {
                fft_forward_real(fft, fft_cost_signal, fft_cost_full);
                cost_sink += fft_cost_full[1].re;
            }
        }
    });

    return seconds;
}

static double fft_cost_time_inverse(fft_t* fft, bool faster)
{
    double seconds;

    COST_MEASURE(seconds, 1u,
    {
        for(uint32_t block = 0u; block < FFT_COST_BLOCKS; block++)
        {
            if(faster)
            {
                fft_inverse_half(fft, fft_cost_bins, fft_cost_answer,
                                 fft_cost_work);
            }
            else
            {
                fft_inverse_real(fft, fft_cost_bins, fft_cost_answer,
                                 fft_cost_work);
            }
            cost_sink += fft_cost_answer[1];
        }
    });

    return seconds;
}

void run_fft_cost_tests(void)
{
    double forward_plain = 0.0;
    double forward_half = 0.0;
    double inverse_plain = 0.0;
    double inverse_half = 0.0;
    fft_t fft = fft_alloc(FFT_COST_SIZE);

    for(uint32_t index = 0u; index < FFT_COST_SIZE; index++)
    {
        fft_cost_signal[index] = cost_random_value();
    }

    // The inverse roads are given a true half spectrum, the one the signal
    // gives.
    fft_forward_half(&fft, fft_cost_signal, fft_cost_bins);

    // One run of each, in turn. cost.h says why the two sides of a claim are
    // not measured one after the other.
    for(uint32_t round = 0u; round < FFT_COST_REPEATS; round++)
    {
        cost_keep_fastest(&forward_plain, fft_cost_time_forward(&fft, false), round);
        cost_keep_fastest(&forward_half, fft_cost_time_forward(&fft, true), round);
        cost_keep_fastest(&inverse_plain, fft_cost_time_inverse(&fft, false), round);
        cost_keep_fastest(&inverse_half, fft_cost_time_inverse(&fft, true), round);
    }

    fft_free(&fft);

    cost_claim_at_least("fft",
                        "the forward half road costs about half the work",
                        forward_plain / forward_half, 1.4);

    cost_claim_at_least("fft",
                        "the inverse half road costs about half the work",
                        inverse_plain / inverse_half, 1.5);
}
