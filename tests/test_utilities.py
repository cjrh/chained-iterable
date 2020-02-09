from chained_iterable.utilities import sentinel


def test_sentinel() -> None:
    assert repr(sentinel) == "<sentinel>"
