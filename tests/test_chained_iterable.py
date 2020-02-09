from functools import reduce
from itertools import count
from itertools import islice
from operator import add
from operator import mod
from operator import sub
from re import escape
from sys import maxsize
from typing import Any
from typing import Callable
from typing import Dict
from typing import Iterable
from typing import List
from typing import Optional
from typing import Tuple
from typing import Union

from hypothesis import assume
from hypothesis import given
from hypothesis.strategies import booleans
from hypothesis.strategies import composite
from hypothesis.strategies import data
from hypothesis.strategies import dictionaries
from hypothesis.strategies import fixed_dictionaries
from hypothesis.strategies import integers
from hypothesis.strategies import just
from hypothesis.strategies import lists
from hypothesis.strategies import sampled_from
from hypothesis.strategies import tuples
from more_itertools import chunked
from pytest import mark
from pytest import raises

from chained_iterable import ChainedIterable
from chained_iterable import EmptyIterableError
from chained_iterable import MultipleElementsError
from chained_iterable.errors import UnsupportVersionError
from chained_iterable.utilities import drop_sentinel
from chained_iterable.utilities import Sentinel
from chained_iterable.utilities import sentinel
from chained_iterable.utilities import VERSION
from chained_iterable.utilities import Version


def _assert_same_type_and_equal(x: Any, y: Any) -> None:
    assert type(x) == type(y)
    assert x == y


@composite
def _int_to_bool_funcs(draw: Any) -> Callable[[int], bool]:
    modulus = draw(integers(min_value=1))
    remainder = draw(integers(0, modulus - 1))
    return lambda x: (mod(x, modulus) == remainder)


@composite
def _incrementers(draw: Any) -> Callable[[int], int]:
    increment = draw(integers(0, 1))
    return lambda x: (x + increment)


@composite
def _modulusers(draw: Any) -> Callable[[int], int]:
    modulus = draw(integers(min_value=1))
    return lambda x: mod(x, modulus)


@composite
def _int_to_int_funcs(draw: Any) -> Callable[[int], int]:
    return draw(_incrementers() | _modulusers())


@composite
def _int_to_any_funcs(draw: Any) -> Callable[[int], Any]:
    return draw(_int_to_bool_funcs() | _int_to_int_funcs())


@composite
def _int_and_int_to_int_funcs(draw: Any) -> Callable[[int, int], int]:
    func_1, func_2 = draw(tuples(_int_to_int_funcs(), _int_to_int_funcs()))
    combiner = draw(sampled_from([add, sub]))
    return lambda x, y: combiner(func_1(x), func_2(y))


# core


@given(input_=integers() | lists(integers()))
def test_init(input_: Union[int, List[int]]) -> None:
    if isinstance(input_, int):
        with raises(
            TypeError,
            match="ChainedIterable expected an iterable, "
            "but 'int' object is not iterable",
        ):
            ChainedIterable(input_)
    else:
        assert isinstance(ChainedIterable(iter(input_)), ChainedIterable)


@given(ints=lists(integers()), other=integers() | lists(integers()))
def test_eq(ints: List[int], other: Union[int, List[int]]) -> None:
    _assert_same_type_and_equal(
        ChainedIterable(iter(ints)) == other, ints == other,
    )


@given(ints=lists(integers()), index=integers())
def test_get_item(ints: List[int], index: int) -> None:
    iterable = ChainedIterable(iter(ints))
    num_ints = len(ints)
    if index < 0:
        with raises(
            IndexError, match=f"Expected a non-negative index; got {index}",
        ):
            iterable[index]
    elif 0 <= index < num_ints:
        _assert_same_type_and_equal(iterable[index], ints[index])
    elif num_ints <= index <= maxsize:
        with raises(IndexError, match="ChainedIterable index out of range"):
            iterable[index]
    else:
        with raises(
            IndexError,
            match=f"Expected an index at most {maxsize}; got {index}",
        ):
            iterable[index]


@given(ints=lists(integers()))
def test_iter(ints: List[int]) -> None:
    assert list(ChainedIterable(iter(ints))) == ints


@given(ints=lists(integers()))
def test_repr(ints: List[int]) -> None:
    assert repr(ChainedIterable(ints)) == f"ChainedIterable({ints!r})"


@given(ints=lists(integers()))
def test_str(ints: List[int]) -> None:
    assert str(ChainedIterable(ints)) == f"ChainedIterable({ints})"


# built-ins


@given(bools=lists(booleans()))
def test_any(bools: List[bool]) -> None:
    _assert_same_type_and_equal(ChainedIterable(iter(bools)).any(), any(bools))


@given(bools=lists(booleans()))
def test_all(bools: List[bool]) -> None:
    _assert_same_type_and_equal(ChainedIterable(iter(bools)).all(), all(bools))


@given(mapping=dictionaries(integers(), integers()))
def test_dict(mapping: Dict[int, int]) -> None:
    _assert_same_type_and_equal(
        ChainedIterable(mapping.items()).dict(), mapping,
    )


@given(ints=lists(integers()), start=integers())
def test_enumerate(ints: List[int], start: int) -> None:
    iterable = ChainedIterable(iter(ints)).enumerate(start=start)
    assert isinstance(iterable, ChainedIterable)
    assert iterable == enumerate(ints, start=start)


@given(ints=lists(integers()), func=_int_to_bool_funcs())
def test_filter(ints: List[int], func: Callable[[int], bool]) -> None:
    iterable = ChainedIterable(iter(ints)).filter(func)
    assert isinstance(iterable, ChainedIterable)
    assert iterable == filter(func, ints)


@given(ints=lists(integers()))
@mark.parametrize("func", [frozenset, list, set, tuple])
def test_frozenset_and_list_and_set_and_tuple(
    ints: List[int], func: Callable[[Iterable[int]], Iterable[int]],
) -> None:
    _assert_same_type_and_equal(
        getattr(ChainedIterable(iter(ints)), func.__name__)(), func(ints),
    )


@given(ints=lists(integers()), func=_int_to_int_funcs())
def test_map(ints: List[int], func: Callable[[int], int]) -> None:
    iterable = ChainedIterable(iter(ints)).map(func)
    assert isinstance(iterable, ChainedIterable)
    assert iterable == map(func, ints)


@given(
    data=data(),
    ints=lists(integers()),
    default_kwargs=just({}) | fixed_dictionaries({"default": integers()}),
)
@mark.parametrize("func", [max, min])
def test_max_and_min(
    data: Any,
    ints: List[int],
    func: Callable[..., int],
    default_kwargs: Dict[str, int],
) -> None:
    method = getattr(ChainedIterable(iter(ints)), func.__name__)
    key_kwargs_strategies = just({}) | fixed_dictionaries(
        {"key": _int_to_any_funcs()},
    )
    if VERSION in {Version.py36, Version.py37}:
        key_kwargs = data.draw(key_kwargs_strategies)
    elif VERSION is Version.py38:
        key_kwargs = data.draw(key_kwargs_strategies | just({"key": None}))
    else:
        raise UnsupportVersionError(VERSION)
    try:
        res = method(**key_kwargs, **default_kwargs)
    except ValueError:
        with raises(
            ValueError,
            match=escape(f"{func.__name__}() arg is an empty sequence"),
        ):
            func(ints, **key_kwargs, **default_kwargs)
    else:
        _assert_same_type_and_equal(
            res, func(ints, **key_kwargs, **default_kwargs),
        )


@given(
    start=integers(-1000, 1000),
    stop=integers(-1000, 1000) | just(sentinel),
    step=integers(-1000, 1000).filter(lambda x: x != 0) | just(sentinel),
)
def test_range(
    start: int, stop: Union[int, Sentinel], step: Union[int, Sentinel],
) -> None:
    if step is sentinel:
        assume(stop is not sentinel)
    args, _ = drop_sentinel(stop, step)
    iterable = ChainedIterable.range(start, *args)
    assert isinstance(iterable, ChainedIterable)
    assert iterable == range(start, *args)


@given(ints=lists(integers()))
def test_reversed(ints: List[int]) -> None:
    iterable = ChainedIterable(ints).reversed()
    assert isinstance(iterable, ChainedIterable)
    assert iterable == reversed(ints)


@given(ints=lists(integers()), key=_int_to_any_funcs(), reverse=booleans())
def test_sorted(
    ints: List[int], key: Optional[Callable[[int], Any]], reverse: bool,
) -> None:
    _assert_same_type_and_equal(
        ChainedIterable(iter(ints)).sorted(key=key, reverse=reverse),
        sorted(ints, key=key, reverse=reverse),
    )


@given(
    ints=lists(integers()), args=just(()) | tuples(integers()),
)
def test_sum(ints: List[int], args: Tuple[str, ...]) -> None:
    _assert_same_type_and_equal(
        ChainedIterable(iter(ints)).sum(*args), sum(ints, *args),
    )


@given(
    ints=lists(integers()), iterables=lists(lists(integers())),
)
def test_zip(ints: List[int], iterables: List[List[int]]) -> None:
    iterable = ChainedIterable(iter(ints)).zip(*iterables)
    assert isinstance(iterable, ChainedIterable)
    assert iterable == zip(ints, *iterables)


# public


@given(ints=lists(integers()))
def test_cache(ints: List[int]) -> None:
    iterable = ChainedIterable(iter(ints)).cache()
    assert isinstance(iterable, ChainedIterable)
    assert iterable == ints


@given(ints=lists(integers()))
@mark.parametrize("method_name, index", [("first", 0), ("last", -1)])
def test_first_and_last(ints: List[int], method_name: str, index: int) -> None:
    method = getattr(ChainedIterable(iter(ints)), method_name)
    if ints:
        assert method() == ints[index]
    else:
        with raises(EmptyIterableError):
            method()


@given(ints=lists(integers()))
def test_len(ints: List[int]) -> None:
    _assert_same_type_and_equal(ChainedIterable(iter(ints)).len(), len(ints))


@given(ints=lists(integers()))
def test_one(ints: List[int]) -> None:
    iterable = ChainedIterable(iter(ints))
    num_ints = len(ints)
    if num_ints == 0:
        with raises(EmptyIterableError):
            iterable.one()
    elif num_ints == 1:
        assert iterable.one() == ints[0]
    else:
        with raises(MultipleElementsError, match=f"{ints[0]}, {ints[1]}"):
            iterable.one()


@given(ints=lists(integers()), n=integers(0, 1000))
def test_pipe(ints: List[int], n: int) -> None:
    iterable = ChainedIterable(iter(ints)).pipe(chunked, n)
    assert isinstance(iterable, ChainedIterable)
    assert iterable == chunked(ints, n)


@given(iterables=lists(lists(integers())))
def test_unzip(iterables: List[List[int]]) -> None:
    iterable = ChainedIterable(iterables).unzip()
    assert isinstance(iterable, ChainedIterable)
    assert iterable == zip(*iterables)


# functools


@given(
    ints=lists(integers()),
    func=_int_and_int_to_int_funcs(),
    initial_args=just(()) | tuples(integers()),
)
def test_reduce(
    ints: List[int],
    func: Callable[[int, int], int],
    initial_args: Tuple[int, ...],
) -> None:
    try:
        res = ChainedIterable(iter(ints)).reduce(func, *initial_args)
    except EmptyIterableError:
        with raises(
            TypeError,
            match=escape(f"reduce() of empty sequence with no initial value"),
        ):
            reduce(func, ints, *initial_args)
    else:
        _assert_same_type_and_equal(
            res, reduce(func, ints, *initial_args),
        )


# itertools


@given(
    start=integers(), step=integers(), length=integers(0, 1000),
)
def test_count(start: int, step: int, length: int) -> None:
    iterable = ChainedIterable.count(start=start, step=step)
    assert isinstance(iterable, ChainedIterable)
    assert iterable[:length] == islice(count(start=start, step=step), length)
