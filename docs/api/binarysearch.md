# binarysearch

This file comes from the comments in the headers. Do not change it by hand.
To make it again, give:

```bash
python3 scripts/api_doc.py
```

Binary search. Declared in `ffitt/util/binarysearch.h`.

[Back to the index](../API.md) | [How the util modules work](../../ffitt/util/README.md) | [How it works](../diagrams/util/binarysearch.html) ([preview](https://htmlpreview.github.io/?https://github.com/AugustinJose1221/ffitt/blob/development/docs/diagrams/util/binarysearch.html))

## Method

The list is halved again and again until one place is left:

    while low < high:
        middle = (low + high) / 2
        if x[middle] < value: low = middle + 1
        else:                 high = middle

Thus the cost is log2(n) reads and not n. A list of a million is found in
twenty steps.

The list must rise. Nothing here checks that, because checking would cost the
n reads the search exists to avoid.

The answer is always an index the caller can use. Where every value is less
than the one asked for, the answer is the last index rather than one past the
end, thus a caller that reads the list at the answer never reads past it.

## Functions

### `binarysearch_get_index`

```c
uint32_t binarysearch_get_index(real_t* data, real_t value, uint32_t size);
```

Give the index of the first value of the list that is not less than the
given value. The values of the list must rise.

The result is always an index that the caller can use. If every value of the
list is less than the given value, the result is the index of the last
value. Thus a caller that reads the list at the result never reads memory
after the end of the list.
