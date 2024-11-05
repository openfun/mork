"""Mork API v1."""

from fastapi import FastAPI

from mork.api.v1.routers import tasks, users

app = FastAPI(title="Mork API (v1)")

app.include_router(tasks.router)
app.include_router(users.router)
