#ifndef CALLBACK_H
#define CALLBACK_H

// Method:
// There is no arithmetic here. The module holds one shape:
//
//     int (*print_t)(const char*, ...)
//
// That is the shape of printf, thus a caller on a machine with a console gives
// printf itself and nothing is written to make it fit.
//
// A caller on a target with no console gives its own function of that shape,
// writing to a serial port or to nothing at all. A caller that gives NULL gets
// printf.
//
// Every module of this library that writes anything takes a function of this
// type rather than calling printf itself. That one indirection is what keeps
// the library from depending on a console that a target may not have.


// The type of a function that writes text.
//
// Each module that writes something takes a function of this type. printf has
// this type, thus a caller can give printf directly. A caller on a target with
// no console gives its own function, for example one that writes to a serial
// port. A caller that gives NULL gets printf.
typedef int (*print_t)(const char*, ...);

#endif//CALLBACK_H
