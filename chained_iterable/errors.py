class UnsupportVersionError(RuntimeError):
    """Raised when the version of Python is unsupported."""


class EmptyIterableError(ValueError):
    """Raised when an Iterable is unexpectedly empty."""


class MultipleElementsError(ValueError):
    """Raised when an Iterable unexpectedly contains more than 1 element."""
