#ifndef BINARYSEARCH_H
#define BINARYSEARCH_H

#include <stdio.h>
#include <stdint.h>
#ifndef TEST
#include <ffitt/core/real.h>
#else
#include "real.h"
#endif

// Method:
// The list is halved again and again until one place is left:
//
//     while low < high:
//         middle = (low + high) / 2
//         if x[middle] < value: low = middle + 1
//         else:                 high = middle
//
// Thus the cost is log2(n) reads and not n. A list of a million is found in
// twenty steps.
//
// The list must rise. Nothing here checks that, because checking would cost the
// n reads the search exists to avoid.
//
// The answer is always an index the caller can use. Where every value is less
// than the one asked for, the answer is the last index rather than one past the
// end, thus a caller that reads the list at the answer never reads past it.


// Give the index of the first value of the list that is not less than the
// given value. The values of the list must rise.
//
// The result is always an index that the caller can use. If every value of the
// list is less than the given value, the result is the index of the last
// value. Thus a caller that reads the list at the result never reads memory
// after the end of the list.
uint32_t binarysearch_get_index(real_t* data, real_t value, uint32_t size);

#endif//BINARYSEARCH_H
