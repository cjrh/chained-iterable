# chained-iterable
[![Build Status](https://dev.azure.com/baoweiur521/baoweiur521/_apis/build/status/baowei521.chained-iterable?branchName=master)](https://dev.azure.com/baoweiur521/baoweiur521/_build/latest?definitionId=2&branchName=master)
[![PyPI version](https://badge.fury.io/py/chained_iterable.svg)](https://badge.fury.io/py/chained_iterable)

## Overview
`chained_iterable` provides a single, light-weight object `ChainedIterable` that makes it easy to manipulate iterables in a functional-programming style. It:
* has access to all Python [built-in](https://docs.python.org/3/library/functions.html) functions relating to iterables, as well as those from [itertools](https://docs.python.org/3/library/itertools.html#module-itertools) and [functools](https://docs.python.org/3/library/functools.html#module-functools).
* can be used with third-party iterables (e.g., [more-itertools](https://github.com/erikrose/more-itertools) via the [pipe](https://en.wikipedia.org/wiki/Pipeline_(Unix) method.
* is [generic](https://docs.python.org/3/library/typing.html#typing.Generic), and thus can be type-checked.
* is easily extensible by virtue of being offered as a simple class with no metaclasses and the like.

## Examples

Given code like this:

```python
res = []
for x in range(10):
    y = 2 * x
    if 3 <= y <= 15:
        z = y - 1
        if z >= 6:
            res.append(z)
assert res == [7, 9, 11, 13]
```

You can reduce the complexity by using [generator expressions](https://www.python.org/dev/peps/pep-0289/) and [list comprehensions](https://docs.python.org/3/tutorial/datastructures.html#list-comprehensions) instead of nesting:

```python
x = range(10)
y = (2*i for i in x)
z = (i for i in y if 3 <= i <= 15)
a = (i-1 for i in z)
res = [i for i in a if i >= 6]
```

You can reduce the number of variables used by using a [functional programming](https://en.wikipedia.org/wiki/Functional_programming) style:

```python
x = range(10)
y = map(lambda i: 2*i, x)
z = filter(lambda i: 3 <= i <= 15, y)
a = map(lambda i: i-1, z)
res = list(filter(lambda i: i >= 6, a))
```

You can further reduce the number of variables used by using `ChainedIterable`:

```python
from chained_iterable import ChainedIterable

res = (
    ChainedIterable.range(10)
    .map(lambda i: 2*i)
    .filter(lambda i: 3 <= i <= 15)
    .map(lambda i: i-1)
    .filter(lambda i: i >= 6)
    .list()
)
```

The edge in clarity scales as the number of operations increase.

As mentioned, you have access to all [itertools](https://docs.python.org/3/library/itertools.html#module-itertools) and [functools](https://docs.python.org/3/library/functools.html#module-functools) as well, you can write:

```python
from chained_iterable import ChainedIterable

res = (
    ChainedIterable(["a", "b", "c", "d", "e", "f", "g"])
    .islice(2, 5)
    .map(lambda i: 2*i)
    .reduce(lambda i, j: "_".join([i, j]))
)
assert res == "cc_dd_ee"
```

## See also

- [more-itertools](https://github.com/erikrose/more-itertools)
- [PyFunctional](https://github.com/EntilZha/PyFunctional)
- [toolz](https://github.com/pytoolz/toolz)
- [fn.py](https://github.com/kachayev/fn.py)
