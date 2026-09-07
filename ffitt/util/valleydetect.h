#ifndef VALLEYDETECT_H
#define VALLEYDETECT_H

#include <stdint.h>
#include <stdio.h>
#ifndef TEST
#include <ffitt/core/real.h>
#else
#include "real.h"
#endif

// Method:
// A valley is one line, and it is the mirror of a peak:
//
//     x[n] < x[n-1] and x[n] < x[n+1]
//
// Thus the first sample and the last are never valleys, because each has only
// one neighbour, and a signal of fewer than three samples holds no valley at
// all.
//
// The function writes the index and the value of each valley into buffers the
// caller holds, thus it takes no memory of its own. Both buffers must have room
// for as many valleys as the signal could hold, which is one for every other
// sample.
//
// Everything said of a peak applies here upside down. This finds every local
// minimum and judges none of them; where the signal holds noise, most of what
// it finds will not be valleys in any useful sense.


// Find every valley of the signal and give the number of them.
//
// A valley is a sample that is smaller than the sample before it and smaller
// than the sample after it. Thus the first sample and the last sample are
// never valleys, and a signal with fewer than three samples holds no valley.
//
// The function writes the index of each valley into index_buffer and the value
// of each valley into valley_buffer. Both buffers must hold room for as many
// values as the signal holds.
uint32_t valleydetect_get_valley(real_t* input, real_t* index_buffer, real_t* valley_buffer, uint32_t size);

#endif//VALLEYDETECT_H
