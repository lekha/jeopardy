"""Entry point for jeopardy web app."""
from os import getenv

from fastapi import FastAPI
from starlette.middleware.sessions import SessionMiddleware
from tortoise.contrib.fastapi import register_tortoise

from jeopardy.middleware import AuthenticationMiddleware
from jeopardy.routers import auth


app = FastAPI(title="jeopardy")
app.add_middleware(SessionMiddleware, secret_key=getenv("SECRET_KEY"))
app.add_middleware(AuthenticationMiddleware)
register_tortoise(
    app,
    db_url = getenv("DATABASE_URI"),
    modules = {"models": ["jeopardy.models"]},
    add_exception_handlers=True,
)
app.include_router(auth.router, prefix="/user")


@app.get("/health-check")
async def health_check():
    """Verify that app is able to respond to incoming requests."""
    return {"status": "Look at this healthy server go!"}
