from enum import auto
from enum import Enum
from sys import version_info
from typing import Any
from typing import Dict
from typing import Tuple
from typing import TypeVar

from chained_iterable.errors import UnsupportVersionError


_T = TypeVar("_T")


def second(_: Any, x: _T) -> _T:  # noqa: U101
    return x


# sentinel


class Sentinel:
    def __repr__(self) -> str:
        return "<sentinel>"

    __str__ = __repr__


sentinel = Sentinel()


def drop_sentinel(*args: Any, **kwargs: Any) -> Tuple[Tuple, Dict[str, Any]]:
    return (
        tuple(x for x in args if x is not sentinel),
        {k: v for k, v in kwargs.items() if v is not sentinel},
    )


# version


class Version(Enum):
    py36 = auto()
    py37 = auto()
    py38 = auto()


def _get_version() -> Version:
    major, minor, *_ = version_info
    if major != 3:
        raise RuntimeError(f"Expected Python 3; got {major}")
    mapping = {6: Version.py36, 7: Version.py37, 8: Version.py38}
    try:
        return mapping[minor]
    except KeyError:
        raise UnsupportVersionError(
            f"Expected Python 3.6-3.8; got 3.{minor}",
        ) from None


VERSION = _get_version()
