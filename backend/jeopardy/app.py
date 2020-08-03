"""Entry point for jeopardy web app."""
from os import getenv

from fastapi import FastAPI
from fastapi import Security
from starlette.middleware.sessions import SessionMiddleware
from tortoise.contrib.fastapi import register_tortoise

from jeopardy.auth import authorize
from jeopardy.middleware import AuthenticationMiddleware
from jeopardy.routers import auth
from jeopardy.routers import create
from jeopardy.routers import play


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
app.include_router(
    create.router,
    prefix="/api/v1",
    dependencies=[Security(authorize, scopes=["create"])],
)
app.include_router(play.router, prefix="/api/v1")


@app.get("/health-check")
async def health_check():
    """Verify that app is able to respond to incoming requests."""
    return {"status": "Look at this healthy server go!"}
