# point2d

This file comes from the comments in the headers. Do not change it by hand.
To make it again, give:

```bash
python3 scripts/api_doc.py
```

A point on a plane. Declared in `ffitt/core/point2d.h`.

[Back to the index](../API.md) | [How the core modules work](../../ffitt/core/README.md) | [How it works](../diagrams/core/point2d.html) ([preview](https://htmlpreview.github.io/?https://github.com/AugustinJose1221/ffitt/blob/development/docs/diagrams/core/point2d.html))

## Method

There is no arithmetic here at all. The module holds one shape:

    point2d_t = { x, y }

A place on a plane comes up in enough of this library to be worth a name of
its own: a peak at a place and a height, a reading from two axes, a point of
a curve being fitted.

Giving it a name rather than passing two loose values is what keeps a caller
from passing them the wrong way round, which is the only fault this can have.

## Types

### `point2d_t`

A point on a plane.

```c
typedef struct{
    real_t x;
    real_t y;
}point2d_t;
```
