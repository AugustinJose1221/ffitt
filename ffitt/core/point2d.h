#ifndef POINT2D_H
#define POINT2D_H

#ifndef TEST
#include <ffitt/core/real.h>
#else
#include "real.h"
#endif

// Method:
// There is no arithmetic here at all. The module holds one shape:
//
//     point2d_t = { x, y }
//
// A place on a plane comes up in enough of this library to be worth a name of
// its own: a peak at a place and a height, a reading from two axes, a point of
// a curve being fitted.
//
// Giving it a name rather than passing two loose values is what keeps a caller
// from passing them the wrong way round, which is the only fault this can have.

// A point on a plane.
typedef struct{
    real_t x;
    real_t y;
}point2d_t;

#endif//POINT2D_H
