"""The functional-itertools package."""
from functional_itertools.errors import EmptyIterableError
from functional_itertools.errors import MultipleElementsError
from functional_itertools.functional_itertools import ChainedIterable


__version__ = "0.3.0"
_ = {EmptyIterableError, MultipleElementsError, ChainedIterable}
