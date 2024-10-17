"""Module py.test fixtures."""

# ruff: noqa: F401

from pathlib import Path

from .fixtures.app import http_client
from .fixtures.asynchronous import anyio_backend
from .fixtures.auth import auth_headers
from .fixtures.db import db_engine, db_session, edx_mysql_db

TEST_STATIC_PATH = Path(__file__).parent / "static"
