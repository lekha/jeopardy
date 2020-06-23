"""Entry point for jeopardy web app."""
from os import getenv

from fastapi import FastAPI
from tortoise.contrib.fastapi import register_tortoise


app = FastAPI(title="jeopardy")
register_tortoise(
    app,
    db_url = getenv("DATABASE_URI"),
    modules = {"models": ["jeopardy.models"]},
    add_exception_handlers=True,
)


@app.get("/health-check")
async def health_check():
    """Verify that app is able to respond incoming requests."""
    return {"status": "Look at this healthy server go!"}
