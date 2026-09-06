# callback

This file comes from the comments in the headers. Do not change it by hand.
To make it again, give:

```bash
python3 scripts/api_doc.py
```

The print callback. Declared in `ffitt/core/callback.h`.

[Back to the index](../API.md) | [How the core modules work](../../ffitt/core/README.md)

## Overview

The type of a function that writes text.

Each module that writes something takes a function of this type. printf has
this type, thus a caller can give printf directly. A caller on a target with
no console gives its own function, for example one that writes to a serial
port. A caller that gives NULL gets printf.
