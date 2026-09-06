# callback

This file comes from the comments in the headers. Do not change it by hand.
To make it again, give:

```bash
python3 scripts/api_doc.py
```

The print callback. Declared in `ffitt/core/callback.h`.

[Back to the index](../API.md) | [How the core modules work](../../ffitt/core/README.md) | [How it works](../diagrams/core/callback.html) ([preview](https://htmlpreview.github.io/?https://github.com/AugustinJose1221/ffitt/blob/development/docs/diagrams/core/callback.html))

## Method

There is no arithmetic here. The module holds one shape:

    int (*print_t)(const char*, ...)

That is the shape of printf, thus a caller on a machine with a console gives
printf itself and nothing is written to make it fit.

A caller on a target with no console gives its own function of that shape,
writing to a serial port or to nothing at all. A caller that gives NULL gets
printf.

Every module of this library that writes anything takes a function of this
type rather than calling printf itself. That one indirection is what keeps
the library from depending on a console that a target may not have.
