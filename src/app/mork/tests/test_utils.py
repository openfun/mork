"""Tests for utility functions."""

from mork.tests.conftest import TEST_STATIC_PATH
from mork.utils import svg_to_datauri


def test_utils_svg_to_datauri_path():
    """Image to base64 from path."""

    red_square_base64 = "data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHZpZXdCb3g9IjAgMCAxIDEiPgo8cGF0aCBkPSJNMCwwaDF2MUgwIiBmaWxsPSIjZjAwIi8+Cjwvc3ZnPg=="  # noqa: E501

    assert (
        svg_to_datauri(TEST_STATIC_PATH / "images/red-square.svg") == red_square_base64
    )
