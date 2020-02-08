from functools import reduce
from itertools import accumulate
from itertools import chain
from itertools import combinations
from itertools import combinations_with_replacement
from itertools import compress
from itertools import count
from itertools import cycle
from itertools import dropwhile
from itertools import filterfalse
from itertools import groupby
from itertools import islice
from itertools import permutations
from itertools import product
from itertools import repeat
from itertools import starmap
from itertools import tee
from itertools import zip_longest
from operator import add
from operator import itemgetter
from typing import Any
from typing import Callable
from typing import Dict
from typing import FrozenSet
from typing import Iterable
from typing import Iterator
from typing import List
from typing import Optional
from typing import Set
from typing import Tuple
from typing import Type
from typing import TypeVar
from typing import Union

from more_itertools.recipes import all_equal
from more_itertools.recipes import consume
from more_itertools.recipes import dotproduct
from more_itertools.recipes import first_true
from more_itertools.recipes import flatten
from more_itertools.recipes import grouper
from more_itertools.recipes import iter_except
from more_itertools.recipes import ncycles
from more_itertools.recipes import nth
from more_itertools.recipes import nth_combination
from more_itertools.recipes import padnone
from more_itertools.recipes import pairwise
from more_itertools.recipes import partition
from more_itertools.recipes import powerset
from more_itertools.recipes import prepend
from more_itertools.recipes import quantify
from more_itertools.recipes import random_combination
from more_itertools.recipes import random_combination_with_replacement
from more_itertools.recipes import random_permutation
from more_itertools.recipes import random_product
from more_itertools.recipes import repeatfunc
from more_itertools.recipes import roundrobin
from more_itertools.recipes import tabulate
from more_itertools.recipes import tail
from more_itertools.recipes import take
from more_itertools.recipes import unique_everseen
from more_itertools.recipes import unique_justseen

from chained_iterable.errors import EmptyIterableError
from chained_iterable.errors import MultipleElementsError
from chained_iterable.errors import UnsupportVersionError
from chained_iterable.utilities import drop_sentinel
from chained_iterable.utilities import second
from chained_iterable.utilities import Sentinel
from chained_iterable.utilities import sentinel
from chained_iterable.utilities import VERSION
from chained_iterable.utilities import Version


_T = TypeVar("_T")
_U = TypeVar("_U")
_GroupByTU = Tuple[_U, Iterator[_T]]


if VERSION in {Version.py36, Version.py37}:

    def _accumulate(
        self: "ChainedIterable[_T]", func: Callable[[_T, _T], _T] = add,
    ) -> "ChainedIterable[_T]":
        return self.pipe(accumulate, func, index=0)

    _max_min_key_annotation = Union[Callable[[_T], Any], Sentinel]
    _max_min_key_default = sentinel


elif VERSION is Version.py38:

    def _accumulate(
        self: "ChainedIterable[_T]",
        func: Callable[[_T, _T], _T] = add,
        initial: Optional[_T] = None,
    ) -> "ChainedIterable[_T]":
        return self.pipe(accumulate, func, initial=initial, index=0)

    _max_min_key_annotation = Optional[Callable[[_T], Any]]
    _max_min_key_default = None


else:
    raise UnsupportVersionError(VERSION)


class ChainedIterable(Iterable[_T]):
    __slots__ = ("_iterable",)

    def __init__(self, iterable: Iterable[_T]) -> None:
        try:
            iter(iterable)
        except TypeError as error:
            (msg,) = error.args
            raise TypeError(
                f"{type(self).__name__} expected an itrable, but {msg}",
            )
        else:
            self._iterable = iterable

    def __eq__(self, other: Any) -> bool:
        try:
            iter(other)
        except TypeError:
            return False
        else:
            return self.list() == list(other)

    def __getitem__(self, item: Union[int, slice]) -> _T:
        if isinstance(item, int):
            try:
                value = self.nth(item, default=sentinel)
            except ValueError:
                raise IndexError(f"Expected a non-negative index; got {item}")
            else:
                if value is sentinel:
                    raise IndexError(
                        f"{type(self).__name__} index out of range",
                    )
                else:
                    return value
        elif isinstance(item, slice):
            return self.islice(item.start, item.stop, item.step)
        else:
            raise TypeError(
                f"Expected an int or slice; got a(n) {type(item).__name__}",
            )

    def __iter__(self) -> Iterator[_T]:
        yield from self._iterable

    def __repr__(self) -> str:
        return f"{type(self).__name__}({self._iterable!r})"

    def __str__(self) -> str:
        return f"{type(self).__name__}({self._iterable})"

    # built-in

    def all(self: "ChainedIterable[bool]") -> bool:
        return all(self._iterable)

    def any(self: "ChainedIterable[bool]") -> bool:
        return any(self._iterable)

    def dict(self: "ChainedIterable[Tuple[_T,_U]]") -> Dict[_T, _U]:
        return dict(self._iterable)

    def enumerate(self, start: int = 0) -> "ChainedIterable[Tuple[int, _T]]":
        return self.pipe(enumerate, start=start, index=0)

    def filter(
        self, func: Optional[Callable[[_T], bool]],
    ) -> "ChainedIterable[_T]":
        return self.pipe(filter, func, index=1)

    def frozenset(self) -> FrozenSet[_T]:
        return frozenset(self._iterable)

    def list(self) -> List[_T]:
        return list(self._iterable)

    def map(
        self, func: Callable[..., _U], *iterables: Iterable,
    ) -> "ChainedIterable[_U]":
        return self.pipe(map, func, *iterables, index=1)

    def max(
        self,
        *,
        key: _max_min_key_annotation = _max_min_key_default,
        default: Union[_T, Sentinel] = sentinel,
    ) -> _T:
        _, kwargs = drop_sentinel(key=key, default=default)
        return max(self._iterable, **kwargs)

    def min(
        self,
        *,
        key: _max_min_key_annotation = _max_min_key_default,
        default: Union[_T, Sentinel] = sentinel,
    ) -> _T:
        _, kwargs = drop_sentinel(key=key, default=default)
        return min(self._iterable, **kwargs)

    @classmethod
    def range(
        cls,
        start: int,
        stop: Union[int, Sentinel] = sentinel,
        step: Union[int, Sentinel] = sentinel,
    ) -> "ChainedIterable[int]":
        args, _ = drop_sentinel(stop, step)
        return cls(range(start, *args))

    def reversed(self) -> "ChainedIterable[_T]":
        return self.pipe(reversed, index=0)

    def set(self) -> Set[_T]:
        return set(self._iterable)

    def sorted(
        self,
        *,
        key: Optional[Callable[[_T], Any]] = None,
        reverse: bool = False,
    ) -> List[_T]:
        return sorted(self._iterable, key=key, reverse=reverse)

    def sum(self, start: Union[_T, Sentinel] = sentinel) -> _T:
        args, _ = drop_sentinel(start)
        return sum(self._iterable, *args)

    def tuple(self) -> Tuple[_T, ...]:
        return tuple(self._iterable)

    def zip(self, *iterables: Iterable) -> "ChainedIterable[Tuple]":
        return self.pipe(zip, *iterables, index=0)

    # extra public methods

    def cache(self) -> "ChainedIterable[_T]":
        return self.pipe(list, index=0)

    def first(self) -> _T:
        return self[0]

    def last(self) -> _T:
        return self.reduce(second)

    def len(self) -> int:
        return self.enumerate(start=1).map(itemgetter(0)).last()

    def one(self) -> _T:
        head: List[_T] = self.islice(2).list()
        if head:
            try:
                (x,) = head
            except ValueError:
                x, y = head
                raise MultipleElementsError(f"{x}, {y}")
            else:
                return x
        else:
            raise EmptyIterableError

    def pipe(
        self,
        func: Callable[..., Iterable[_U]],
        *args: Any,
        index: int = 0,
        **kwargs: Any,
    ) -> "ChainedIterable[_U]":
        new_args = chain(
            islice(args, index), [self._iterable], islice(args, index, None),
        )
        return type(self)(func(*new_args, **kwargs))

    def unzip(self: "ChainedIterable[Tuple]") -> "ChainedIterable":
        return type(self)(zip(*self._iterable))

    # functools

    def reduce(
        self,
        func: Callable[[_T, _T], _T],
        initial: Union[_T, Sentinel] = sentinel,
    ) -> _T:
        args, _ = drop_sentinel(initial)
        try:
            return reduce(func, self._iterable, *args)
        except TypeError as error:
            (msg,) = error.args
            if msg == "reduce() of empty sequence with no initial value":
                raise EmptyIterableError from None
            else:
                raise error

    # itertools

    @classmethod
    def count(cls, start: int = 0, step: int = 1) -> "ChainedIterable[int]":
        return cls(count(start=start, step=step))

    def cycle(self) -> "ChainedIterable[_T]":
        return self.pipe(cycle, index=0)

    @classmethod
    def repeat(
        cls, x: _T, times: Optional[int] = None,
    ) -> "ChainedIterable[_T]":
        return cls(repeat(x, times=times))

    accumulate = _accumulate

    def chain(
        self, *iterables: Iterable[_U],
    ) -> "ChainedIterable[Union[_T,_U]]":
        return self.pipe(chain, *iterables, index=0)

    def compress(self, selectors: Iterable) -> "ChainedIterable[_T]":
        return self.pipe(compress, selectors, index=0)

    def dropwhile(
        self, func: Callable[[_T], bool],
    ) -> "ChainedIterable[Tuple[_T]]":
        return self.pipe(dropwhile, func, index=0)

    def filterfalse(
        self, func: Callable[[_T], bool],
    ) -> "ChainedIterable[Tuple[_T]]":
        return self.pipe(filterfalse, func, index=0)

    def groupby(
        self, key: Optional[Callable[[_T], _U]] = None,
    ) -> "ChainedIterable[_GroupByTU]":
        return self.pipe(groupby, key=key, index=0)

    def islice(
        self,
        start: int,
        stop: Union[int, Sentinel] = sentinel,
        step: Union[int, Sentinel] = sentinel,
    ) -> "ChainedIterable[_T]":
        args, _ = drop_sentinel(stop, step)
        return self.pipe(islice, start, *args, index=0)

    def starmap(self, func: Callable[[Tuple], _U]) -> "ChainedIterable[_U]":
        return self.pipe(starmap, func, index=1)

    def tee(self, n: int = 2) -> "ChainedIterable[_T]":
        return self.pipe(tee, n=n, index=0)

    def zip_longest(
        self, *iterables: Iterable, fillvalue: Any = None,
    ) -> "ChainedIterable[Iterable[Tuple]]":
        return self.pipe(zip_longest, *iterables, fillvalue=fillvalue, index=0)

    def product(
        self, *iterables: Iterable, repeat: int = 1,
    ) -> "ChainedIterable[_T]":
        return self.pipe(product, *iterables, repeat=repeat, index=0)

    def permutations(
        self, r: Optional[int] = None,
    ) -> "ChainedIterable[Tuple[_T]]":
        return self.pipe(permutations, r=r, index=0)

    def combinations(self, r: int) -> "ChainedIterable[Tuple[_T]]":
        return self.pipe(combinations, r, index=0)

    def combinations_with_replacement(
        self, r: int,
    ) -> "ChainedIterable[Tuple[_T]]":
        return self.pipe(combinations_with_replacement, r, index=0)

    # itertools-recipes

    def take(self, n: int) -> "ChainedIterable[_T]":
        return self.pipe(take, n, index=1)

    def prepend(self, value: _T) -> "ChainedIterable[_T]":
        return self.pipe(prepend, value, index=1)

    @classmethod
    def tabulate(
        cls, func: Callable[[int], _T], start: int = 0,
    ) -> "ChainedIterable[_T]":
        return cls(tabulate(func, start=start))

    def tail(self, n: int) -> "ChainedIterable[_T]":
        return self.pipe(tail, n, index=1)

    def consume(self, n: Optional[int] = None) -> "ChainedIterable[_T]":
        return self.pipe(consume, n=n, index=1)

    def nth(self, n: int, default: Optional[_T] = None) -> "_T":
        return nth(self._iterable, n, default=default)

    def all_equal(self) -> bool:
        return all_equal(self._iterable)

    def quantify(self, pred: Callable[[_T], bool] = bool) -> int:
        return quantify(self._iterable, pred=pred)

    def padnone(self) -> "ChainedIterable[Optional[_T]]":
        return self.pipe(padnone, index=0)

    def ncycles(self, n: int) -> "ChainedIterable[_T]":
        return self.pipe(ncycles, n, index=0)

    def dotproduct(self, iterable: Iterable[_T]) -> _T:
        return dotproduct(self._iterable, iterable)

    def flatten(self: "ChainedIterable[Iterable[_T]]") -> "ChainedIterable[_T]":
        return self.pipe(flatten, index=0)

    @classmethod
    def repeatfunc(
        cls, func: Callable[..., _T], times: Optional[int] = None, *args: Any,
    ) -> "ChainedIterable[_T]":
        return cls(repeatfunc(func, times=times, *args))

    def pairwise(self) -> "ChainedIterable[Tuple[_T,_T]]":
        return self.pipe(pairwise, index=0)

    def grouper(
        self, n: int, fillvalue: Optional[_T] = None,
    ) -> "ChainedIterable[Tuple[_T,...]]":
        return self.pipe(grouper, n, fillvalue=fillvalue, index=0)

    def partition(
        self, func: Callable[[_T], bool],
    ) -> Tuple["ChainedIterable[_T]", "ChainedIterable[_T]"]:
        return self.pipe(partition, func, index=1).map(type(self)).tuple()

    def powerset(self) -> "ChainedIterable[Tuple[_T,...]]":
        return self.pipe(powerset, index=0)

    def roundrobin(self, *iterables: Iterable[_T]) -> "ChainedIterable[_T]":
        return self.pipe(roundrobin, *iterables, index=0)

    def unique_everseen(
        self, key: Optional[Callable[[_T], Any]] = None,
    ) -> "ChainedIterable[_T]":
        return self.pipe(unique_everseen, key=key, index=0)

    def unique_justseen(
        self, key: Optional[Callable[[_T], Any]] = None,
    ) -> "ChainedIterable[_T]":
        return self.pipe(unique_justseen, key=key, index=0)

    @classmethod
    def iter_except(
        cls,
        func: Callable[..., _T],
        exception: Type[Exception],
        first: Optional[_T] = None,
    ) -> "ChainedIterable[_T]":
        return cls(iter_except(func, exception, first=first))

    def first_true(
        self,
        default: bool = False,
        pred: Optional[Callable[[_T], bool]] = None,
    ) -> "ChainedIterable[_T]":
        return first_true(self._iterable, default=default, pred=pred)

    def random_product(
        self, *iterables: Iterable, repeat: int = 1,
    ) -> Tuple[_T, ...]:
        return random_product(self._iterable, *iterables, repeat=repeat)

    def random_permutation(self, r: Optional[int] = None) -> Tuple[_T, ...]:
        return random_permutation(self._iterable, r=r)

    def random_combination(self, r: int) -> Tuple[_T, ...]:
        return random_combination(self._iterable, r)

    def random_combination_with_replacement(self, r: int) -> Tuple[_T, ...]:
        return random_combination_with_replacement(self._iterable, r)

    def nth_combination(self, r: int, index: int) -> Tuple[_T, ...]:
        return nth_combination(self._iterable, r, index)
