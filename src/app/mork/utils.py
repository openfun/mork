"""Utility functions."""

from pathlib import Path

from datauri import DataURI


def svg_to_datauri(path: Path | str):
    """Return the data URI string of an SVG image."""
    return str(DataURI.from_file(path))
