"""Custom template tags for Mork."""

from jinja2_simple_tags import StandaloneTag

from mork.conf import settings
from mork.utils import svg_to_datauri


class SVGStaticTag(StandaloneTag):
    """Extension Jinja tag for converting SVG files to data URI."""

    tags = {"svg_static"}

    def render(self, path: str):
        """Return a SVG static file into data URI format."""
        full_path = settings.STATIC_PATH / path
        if full_path.exists():
            return svg_to_datauri(full_path)
        return ""
