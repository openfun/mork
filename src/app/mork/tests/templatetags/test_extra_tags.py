"""Tests for Mork extra Jinja tags."""

from mork.templatetags.extra_tags import SVGStaticTag
from mork.tests.conftest import TEST_STATIC_PATH


def test_svgstatictag_render(monkeypatch):
    """Test the SVGStaticTag `render` method returns file encoded in base64."""
    static_filepath = TEST_STATIC_PATH / "images/red-square.svg"

    red_square_base64 = "data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHZpZXdCb3g9IjAgMCAxIDEiPgo8cGF0aCBkPSJNMCwwaDF2MUgwIiBmaWxsPSIjZjAwIi8+Cjwvc3ZnPg=="  # noqa: E501

    monkeypatch.setattr(
        "mork.templatetags.extra_tags.SVGStaticTag.__init__", lambda x: None
    )

    assert SVGStaticTag().render(static_filepath) == red_square_base64


def test_base64tag_render_unknown_file(monkeypatch):
    """Test that the SVGStaticTag `render` method should return an empty string."""
    static_filepath = "unknown-static-file.txt"

    monkeypatch.setattr(
        "mork.templatetags.extra_tags.SVGStaticTag.__init__", lambda x: None
    )

    assert SVGStaticTag().render(static_filepath) == ""
