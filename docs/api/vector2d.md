# vector2d

This file comes from the comments in the headers. Do not change it by hand.
To make it again, give:

```bash
python3 scripts/api_doc.py
```

Vectors with two values. Declared in `ffitt/linalg/vector2d.h`.

[Back to the index](../API.md) | [How the linalg modules work](../../ffitt/linalg/README.md) | [How it works](../diagrams/linalg/vector2d.html) ([preview](https://htmlpreview.github.io/?https://github.com/AugustinJose1221/ffitt/blob/development/docs/diagrams/linalg/vector2d.html))

## Overview

A vector with two values.

This module gives the operations of the vector module for a vector of the
size 2, thus the caller does not give the size at each call. The result is a
vector_t, and every function of the vector module takes it.

## Method

There is no arithmetic here that the vector module does not already do:

    dot(a, b) = a.x*b.x + a.y*b.y
    norm(a)   = sqrt(dot(a, a))

The size is 2 and the caller never says so. That is the whole of what this
module adds, and the answer is a vector_t, thus every function of the vector
module takes it unchanged.

A plane is common enough to be worth the saving: a point on a screen, a
reading from two axes, a place in a picture. Writing the size at every call
for a size that never changes is noise in the code that reads it.

## Functions

### `vector2d_alloc`

```c
vector_t vector2d_alloc(void);
```

Give a vector with two values. The memory comes from the heap. Give the
vector to vector_free when you no longer need it.

### `vector2d_static_alloc`

```c
vector_t vector2d_static_alloc(real_t* mempool);
```

Give a vector with two values that uses the memory at mempool. That memory
must hold two float values. This function takes no memory from the heap.

### `vector2d_add_point_at_index`

```c
void vector2d_add_point_at_index(vector_t* vector, uint32_t index, real_t data);
```

Write a value into the vector at the given index. The index must be 0 or 1.

### `vector2d_add_from_array`

```c
void vector2d_add_from_array(vector_t* vector, real_t* data);
```

Write two values from an array into the vector.

### `vector2d_printf`

```c
void vector2d_printf(vector_t* vector, int (*func)(const char *, ...));
```

Write the vector, one value for each line. Give NULL as the function to
write with printf.

### `vector2d_get`

```c
real_t vector2d_get(vector_t* vector, uint32_t index);
```

Give the value of the vector at the given index. The index must be 0 or 1.

### `vector2d_dot_product`

```c
real_t vector2d_dot_product(vector_t* x, vector_t* y);
```

Give the dot product of the two vectors.

### `vector2d_norm`

```c
real_t vector2d_norm(vector_t* x);
```

Give the length of the vector.
