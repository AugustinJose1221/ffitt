// This file is left out of the build when FFITT_NO_UTIL is defined.
// ffitt/core/README.md says which areas may be left out and
// which of them need which others.
#ifndef FFITT_NO_UTIL

#ifndef TEST
#include <ffitt/util/stats.h>
#include <ffitt/core/defs.h>
#else
#include "stats.h"
#include "defs.h"
#endif

#include <math.h>

static void stats_swap(real_t* data, uint32_t left, uint32_t right)
{
    real_t held = data[left];
    data[left] = data[right];
    data[right] = held;
}

// Put the sample that belongs at the given place into that place, and put every
// smaller sample below it and every larger one above it.
//
// This is the method of the quick select. It is the quick sort with one half
// left out: after a split, only the half that holds the wanted place is worked
// on again. Thus it costs about one pass over the list and not one pass for
// each level, which is what a whole sort would cost.
static void stats_select(real_t* data, uint32_t size, uint32_t place)
{
    uint32_t low = 0;
    uint32_t high = (size > 0u) ? (size - 1u) : 0u;

    while(low < high)
    {
        // Take the middle sample as the pivot and not the first one. A list
        // that is already in order is a common input, and the first sample
        // would then split it into nothing and everything, which is the worst
        // case of this method.
        uint32_t middle = low + ((high - low) / 2u);
        stats_swap(data, middle, high);

        real_t pivot = data[high];
        uint32_t store = low;

        for(uint32_t index = low; index < high; index++)
        {
            if(data[index] < pivot)
            {
                stats_swap(data, index, store);
                store++;
            }
        }
        stats_swap(data, store, high);

        if(place == store)
        {
            return;
        }
        if(place < store)
        {
            high = (store > low) ? (store - 1u) : low;
        }
        else
        {
            low = store + 1u;
        }
    }
}

// A SUM THAT KEEPS WHAT EACH ADDITION ROUNDS AWAY.
//
// Every sum in this module runs at the width of the build, and a sum is where
// the digits run out first. At 32 bits a number holds about seven digits.
// Adding a thousand samples that each sit near eight million gives a total
// near eight thousand million, where one step is 512. Added plainly, every
// sample after the first few loses its low digits to the rounding of the
// total, and the error grows with the number of samples.
//
// This is the compensated sum of Neumaier. Each addition rounds, and the part
// it rounds away is worked out exactly from the two numbers that were added:
// whichever of them is the larger, less the rounded total, plus the smaller.
// That part is kept in a second value, the carry, and the carry is added back
// at the end. It needs no wider type, thus it works the same way at both
// widths. Measured at 32 bits, on a million samples near eight million, the
// plain sum is out by 3.6e-3 of the total and this one by 9.4e-6.
//
// THE CARRY IS A PLAIN SUM ITSELF. Thus a very long list loses digits in the
// carry, much later than a plain sum would lose them in the total. The mean
// and the variance therefore also take each sample as its distance from the
// first one; stats_offset_of_mean says why.
//
// IT COSTS ABOUT FOUR OPERATIONS FOR EACH SAMPLE AND NOT ONE. The table of
// costs holds the measured time.
//
// A BUILD WITH -ffast-math OR -fassociative-math BREAKS IT. Those options let
// the compiler treat (larger - total) + smaller as zero, which it is in exact
// arithmetic, and the carry is then always zero. The build of this library
// gives neither option.
typedef struct{
    real_t total;               // The sum, rounded to the width
    real_t carry;               // What the rounding of the sum lost
}stats_accumulator_t;

static void stats_add(stats_accumulator_t* sum, real_t value)
{
    real_t total = sum->total + value;

    if(REAL_ABS(sum->total) >= REAL_ABS(value))
    {
        sum->carry += (sum->total - total) + value;
    }
    else
    {
        sum->carry += (value - total) + sum->total;
    }

    sum->total = total;
}

// The sum divided by a count. The carry is divided on its own and not added
// to the total first, because the total and the carry together hold more
// digits than one value can, and the division keeps them apart a step longer.
static real_t stats_share(const stats_accumulator_t* sum, uint32_t count)
{
    return (sum->total / (real_t)count) + (sum->carry / (real_t)count);
}

real_t stats_sum(const real_t* data, uint32_t size)
{
    ASSERT(data != NULL);

    stats_accumulator_t sum = { REAL_C(0.0), REAL_C(0.0) };

    for(uint32_t index = 0; index < size; index++)
    {
        stats_add(&sum, data[index]);
    }

    return sum.total + sum.carry;
}

// HOW FAR THE MEAN STANDS FROM THE FIRST SAMPLE.
//
// The samples of a reading that sits far from zero are large, and their sum is
// larger still, thus the steps of the width at that sum are coarse. How far
// each sample stands from the first one is small, and for two samples within a
// factor of two of each other that distance is held exactly. Thus the mean of
// the distances is worked out where the steps are fine, and the first sample
// is added back one time at the end.
//
// Measured at 32 bits, on 65536 samples near a million, the compensated sum of
// the samples themselves gave a mean one step of the width low: the carry is a
// plain sum too, and it lost a little. The mean of the distances is right.
static real_t stats_offset_of_mean(const real_t* data, uint32_t size,
                                   real_t first)
{
    stats_accumulator_t sum = { REAL_C(0.0), REAL_C(0.0) };

    for(uint32_t index = 0; index < size; index++)
    {
        stats_add(&sum, data[index] - first);
    }

    return stats_share(&sum, size);
}

real_t stats_mean(const real_t* data, uint32_t size)
{
    ASSERT(data != NULL);

    if(size == 0u)
    {
        return REAL_C(0.0);
    }

    return data[0] + stats_offset_of_mean(data, size, data[0]);
}

real_t stats_variance(const real_t* data, uint32_t size)
{
    ASSERT(data != NULL);

    if(size == 0u)
    {
        return REAL_C(0.0);
    }

    // Take the mean away first, and only then square.
    //
    // The other way, which is the mean of the squares less the square of the
    // mean, needs one pass and not two. It is also wrong for the signals that
    // this library meets. A reading that sits at 8 000 000 and moves by 1
    // gives two numbers near 64 000 000 000 000 whose difference is 1. A float
    // holds about seven digits, thus that difference is lost and the answer
    // comes out as noise or as a negative number.
    //
    // The distances are taken from the first sample and then from the mean of
    // those distances, and not from the mean itself. The mean is rounded to
    // the step of the width where the samples stand, and that rounding would
    // be squared into the answer. The mean of the distances from the first
    // sample stands where the steps are fine.
    real_t first = data[0];
    real_t offset = stats_offset_of_mean(data, size, first);
    stats_accumulator_t sum = { REAL_C(0.0), REAL_C(0.0) };

    for(uint32_t index = 0; index < size; index++)
    {
        real_t distance = (data[index] - first) - offset;
        stats_add(&sum, distance * distance);
    }

    return stats_share(&sum, size);
}

real_t stats_deviation(const real_t* data, uint32_t size)
{
    return REAL_SQRT(stats_variance(data, size));
}

real_t stats_rms(const real_t* data, uint32_t size)
{
    ASSERT(data != NULL);

    if(size == 0u)
    {
        return REAL_C(0.0);
    }

    stats_accumulator_t sum = { REAL_C(0.0), REAL_C(0.0) };

    for(uint32_t index = 0; index < size; index++)
    {
        stats_add(&sum, data[index] * data[index]);
    }

    return REAL_SQRT(stats_share(&sum, size));
}

real_t stats_min(const real_t* data, uint32_t size)
{
    ASSERT(data != NULL);

    if(size == 0u)
    {
        return REAL_C(0.0);
    }

    real_t smallest = data[0];

    for(uint32_t index = 1; index < size; index++)
    {
        if(data[index] < smallest)
        {
            smallest = data[index];
        }
    }

    return smallest;
}

real_t stats_max(const real_t* data, uint32_t size)
{
    ASSERT(data != NULL);

    if(size == 0u)
    {
        return REAL_C(0.0);
    }

    real_t largest = data[0];

    for(uint32_t index = 1; index < size; index++)
    {
        if(data[index] > largest)
        {
            largest = data[index];
        }
    }

    return largest;
}

real_t stats_median(real_t* data, uint32_t size)
{
    ASSERT(data != NULL);

    if(size == 0u)
    {
        return REAL_C(0.0);
    }

    uint32_t middle = size / 2u;
    stats_select(data, size, middle);

    if((size % 2u) == 1u)
    {
        return data[middle];
    }

    // For an even size the median lies between the two middle samples. The
    // select above put every smaller sample below the middle, thus the largest
    // of those is the other one, and it can be found without another select.
    real_t upper = data[middle];
    real_t lower = data[0];

    for(uint32_t index = 1; index < middle; index++)
    {
        if(data[index] > lower)
        {
            lower = data[index];
        }
    }

    return (lower + upper) / REAL_C(2.0);
}

real_t stats_percentile(real_t* data, uint32_t size, real_t part)
{
    ASSERT(data != NULL);

    if(size == 0u)
    {
        return REAL_C(0.0);
    }
    if(size == 1u)
    {
        return data[0];
    }
    if(part <= REAL_C(0.0))
    {
        return stats_min(data, size);
    }
    if(part >= REAL_C(1.0))
    {
        return stats_max(data, size);
    }

    // The place that the part asks for, which usually lies between two
    // samples.
    real_t place = part * (real_t)(size - 1u);
    uint32_t below = (uint32_t)place;
    real_t between = place - (real_t)below;

    stats_select(data, size, below);
    real_t lower = data[below];

    if(between <= REAL_C(0.0))
    {
        return lower;
    }

    // The next sample up is the smallest of those that stand above the place.
    real_t upper = data[below + 1u];
    for(uint32_t index = below + 1u; index < size; index++)
    {
        if(data[index] < upper)
        {
            upper = data[index];
        }
    }

    return lower + (between * (upper - lower));
}

real_t stats_mad(const real_t* data, uint32_t size, real_t* work)
{
    ASSERT(data != NULL);
    ASSERT(work != NULL);

    if(size == 0u)
    {
        return REAL_C(0.0);
    }

    for(uint32_t index = 0; index < size; index++)
    {
        work[index] = data[index];
    }

    real_t middle = stats_median(work, size);

    for(uint32_t index = 0; index < size; index++)
    {
        work[index] = REAL_ABS(data[index] - middle);
    }

    return stats_median(work, size);
}

#else

// An empty translation unit is not C, thus one name is
// declared and nothing is defined. Nothing links against it.
typedef int stats_is_not_in_this_build_t;

#endif//FFITT_NO_UTIL
