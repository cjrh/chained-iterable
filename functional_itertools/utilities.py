from enum import auto
from enum import Enum
from sys import version_info
from typing import Any
from typing import Tuple
from typing import TypeVar

_T = TypeVar("_T")


class Sentinel:
    def __repr__(self) -> str:
        return "Sentinel"

    __str__ = __repr__


# sentinel
sentinel = Sentinel()


def is_not_sentinel(x: Any) -> bool:
    return x is not sentinel


def second_is_not_sentinel(pair: Tuple[Any, _T]) -> _T:
    _, x = pair
    return is_not_sentinel(x)


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
        raise RuntimeError(f"Expected Python 3.6-3.8; got 3.{minor}") from None


_VERSION = _get_version()
