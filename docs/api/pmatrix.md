# pmatrix

This file comes from the comments in the headers. Do not change it by hand.
To make it again, give:

```bash
python3 scripts/api_doc.py
```

Matrices with a parameter. Declared in `ffitt/linalg/pmatrix.h`.

[Back to the index](../API.md) | [How the linalg modules work](../../ffitt/linalg/README.md) | [How it works](../diagrams/linalg/pmatrix.html) ([preview](https://htmlpreview.github.io/?https://github.com/AugustinJose1221/ffitt/blob/development/docs/diagrams/linalg/pmatrix.html))

## Overview

A matrix with a parameter, for example:

    [ sin(x)  cos(x) ]
    [   0       1    ]

Each element is a pointer to a function of the parameter. To use the matrix,
give a value for the parameter. The matrix then gives a matrix of float
values, which every other module of the library can take.

Why a pointer to a function, and not an expression that the module reads
from text:

A module that reads an expression from text must hold a tree of operations.
Such a tree needs memory while the program runs, and it needs a parser. Both
go against the way this library works, because the library must run on a
target with no heap. A pointer to a function needs no memory while the
program runs, and the compiler makes the code for the expression. The
library already uses a pointer to a function for the print callback, thus
this way fits the library.

The cost is one pointer for each element, where a matrix of float values
holds one float for each element. On a small target a pointer is often the
same size as a float or two times that size. Keep a parameter matrix small,
and give the value of the parameter one time for each step of the
calculation.

A function of the standard library that takes a float and gives a float,
such as real_sin or real_cos, fits the type of an element directly.

## Method

Each element is not a number but a function of one parameter:

    M(x)(i,j) = f_ij(x)

Giving a value for x calls every one of those functions once and writes the
answers into a plain matrix:

    matrix(i,j) = f_ij(x)

which every other module of the library can then take.

That is the whole of it. The module holds pointers to functions rather than
values, and the evaluation is one pass over the elements. Nothing is
differentiated, nothing is solved, and no arithmetic is done on the functions
themselves.

It exists because a state that moves with time or with an angle is written
once as a shape, and then evaluated at each step, rather than rebuilt by hand
at every step by the caller.

## Types

### `pmatrix_t`

```c
typedef struct{
    uint32_t m;
    uint32_t n;
    pmatrix_function_t *elem;
    bool dynamic_alloc;
}pmatrix_t;
```

## Functions

### `pmatrix_alloc`

```c
pmatrix_t pmatrix_alloc(uint32_t m, uint32_t n);
```

Give a parameter matrix with m rows and n columns. The memory comes from
the heap, and every element holds zero. Give the matrix to pmatrix_free when
you no longer need it.

### `pmatrix_static_alloc`

```c
pmatrix_t pmatrix_static_alloc(uint32_t m, uint32_t n, pmatrix_function_t* elem);
```

Give a parameter matrix that uses the memory at elem. That memory must hold
m*n pointers to a function. Every element holds zero after the call. This
function takes no memory from the heap.

### `pmatrix_add_element`

```c
void pmatrix_add_element(pmatrix_t* matrix, uint32_t i, uint32_t j, pmatrix_function_t function);
```

An element that holds NULL gives the value zero. Thus a new matrix that
pmatrix_set_zero cleared holds zero at every place, and a user who needs a
zero at one place does not need a function for it.

### `pmatrix_get_element`

```c
pmatrix_function_t pmatrix_get_element(pmatrix_t* matrix, uint32_t i, uint32_t j);
```

Give the function that stands at the row i and the column j. The result is
NULL if that element holds zero.

### `pmatrix_set_zero`

```c
void pmatrix_set_zero(pmatrix_t* matrix);
```

Write zero into every element of the matrix.

### `pmatrix_evaluate_element`

```c
real_t pmatrix_evaluate_element(pmatrix_t* matrix, uint32_t i, uint32_t j, real_t x);
```

Give the value of one element for the given value of the parameter.

### `pmatrix_evaluate`

```c
matrix_t pmatrix_evaluate(pmatrix_t* matrix, real_t x);
```

Give a new matrix of float values for the given value of the parameter. This
function gets memory. Use pmatrix_evaluate_into on a target with no heap.

### `pmatrix_evaluate_into`

```c
void pmatrix_evaluate_into(pmatrix_t* matrix, real_t x, matrix_t* dest);
```

Write the values into a matrix that already holds memory. The destination
must have the same order as the parameter matrix.

### `pmatrix_zero`

```c
real_t pmatrix_zero(real_t x);
```

An element that always gives zero.

### `pmatrix_one`

```c
real_t pmatrix_one(real_t x);
```

An element that always gives one.

### `pmatrix_free`

```c
void pmatrix_free(pmatrix_t* matrix);
```

Release the memory of a matrix that came from pmatrix_alloc. This function
does nothing for a matrix that came from pmatrix_static_alloc.
