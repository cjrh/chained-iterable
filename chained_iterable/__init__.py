"""The functional-itertools package."""
from chained_iterable.chained_iterable import ChainedIterable
from chained_iterable.errors import EmptyIterableError
from chained_iterable.errors import MultipleElementsError


__version__ = "0.4.0"
_ = {EmptyIterableError, MultipleElementsError, ChainedIterable}
