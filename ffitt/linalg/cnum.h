#ifndef CNUM_H
#define CNUM_H

#include <stdbool.h>
#ifndef TEST
#include <ffitt/core/real.h>
#else
#include "real.h"
#endif

// A complex number.
//
// The C standard gives <complex.h> and the type float _Complex. This library
// does not use them for two reasons. Many small compilers do not give them.
// And <complex.h> gives the macro `complex`, thus a module of this library
// could not carry that name. A structure with two float members works on every
// compiler, and it holds the values in the same way as the rest of the
// library.

// Method:
// A complex number is held as two real values:
//
//     z = re + i*im
//
// and the operations are written out on those two:
//
//     (a + i*b) * (c + i*d) = (a*c - b*d) + i*(a*d + b*c)
//     |z|                   = sqrt(re*re + im*im)
//     angle of z            = atan2(im, re)
//
// The standard gives <complex.h> and float _Complex, and this library uses
// neither. Many small compilers do not offer them. And <complex.h> gives the
// macro `complex`, thus no module of this library could carry that name.
//
// A structure of two members works on every compiler and holds its values the
// same way the rest of the library holds numbers.


typedef struct{
    real_t re;                   // The real part
    real_t im;                   // The imaginary part
}cnum_t;

// Give a complex number with the given real part and imaginary part.
cnum_t cnum_make(real_t re, real_t im);
// Give a complex number whose imaginary part is zero.
cnum_t cnum_from_real(real_t re);
// Give the number zero.
cnum_t cnum_zero(void);
// Give the number one.
cnum_t cnum_one(void);

// Give the sum of the two numbers.
cnum_t cnum_add(cnum_t a, cnum_t b);
// Give the first number less the second one.
cnum_t cnum_subtract(cnum_t a, cnum_t b);
// Give the product of the two numbers.
cnum_t cnum_multiply(cnum_t a, cnum_t b);

// Give the quotient of the two numbers. If the second number is zero, the
// quotient has no value, and the function gives zero.
cnum_t cnum_divide(cnum_t a, cnum_t b);

// Give the number with both parts multiplied by a real factor.
cnum_t cnum_scale(cnum_t a, real_t factor);
// Give the number with the sign of the imaginary part changed.
cnum_t cnum_conjugate(cnum_t a);
// Give the number with the sign of both parts changed.
cnum_t cnum_negate(cnum_t a);

// Give the real part of the number.
real_t cnum_real(cnum_t a);
// Give the imaginary part of the number.
real_t cnum_imaginary(cnum_t a);

// Give the distance of the number from zero.
real_t cnum_magnitude(cnum_t a);

// Give the square of the distance from zero. This function does not take a
// square root, thus it is faster than cnum_magnitude and it keeps more of the
// accuracy. Use it when you only compare two distances.
real_t cnum_magnitude_squared(cnum_t a);

// True if both parts of the number are zero.
bool cnum_is_zero(cnum_t a);
// True if both parts of the two numbers are the same.
bool cnum_is_equal(cnum_t a, cnum_t b);

// Give true if the two numbers differ by less than the tolerance. A float
// keeps about 7 digits, thus a calculation with several steps gives a result
// that is near the correct value but not equal to it.
bool cnum_is_near(cnum_t a, cnum_t b, real_t tolerance);

#endif//CNUM_H
