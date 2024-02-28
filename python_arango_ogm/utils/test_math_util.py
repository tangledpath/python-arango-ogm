import pytest

from python_arango_ogm.utils.math_util import Vector2d, Rect2d, lerp


def test_vector():
    v1 = Vector2d(3, 4)
    v2 = Vector2d((3, 4,))
    assert v1 == v2


def test_vector_decomposition():
    x, y = Vector2d(21, 12)
    assert x == 21
    assert y == 12


def test_rect():
    size = Vector2d(21, 12)
    origin = Vector2d(2, 1)
    rect = Rect2d(origin, size)
    assert rect == Rect2d(2, 1, 21, 12)
    assert rect.origin == Vector2d(2, 1)
    assert rect.size == Vector2d(21, 12)
    assert rect.right == 23
    assert rect.bottom == 13


def test_rect_decomposition():
    rect = Rect2d(2, 1, 21, 12)
    x, y, w, h = rect
    assert x == 2
    assert y == 1
    assert w == 21
    assert h == 12


def test_lerp():
    r = lerp(.5, 7.5, 8.0)
    assert r == 7.75
    with pytest.raises(ValueError):
        r = lerp(.5, 2112, 2021)
