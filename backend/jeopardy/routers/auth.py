from fastapi import APIRouter
from fastapi import Request

from jeopardy.auth import login_user
from jeopardy.auth import logout_user
from jeopardy.auth import oauth
from jeopardy.auth import user_from_google_metadata
from jeopardy.schema.user import GoogleUserMetadata


router = APIRouter()


@router.api_route("/login")
async def login(request: Request):
    callback_url = request.url_for("callback")
    return await oauth.google.authorize_redirect(request, callback_url)


@router.api_route("/oauth2callback")
async def callback(request: Request):
    token = await oauth.google.authorize_access_token(request)
    raw_metadata = await oauth.google.parse_id_token(request, token)
    metadata = GoogleUserMetadata(**raw_metadata)
    user = await user_from_google_metadata(metadata)
    await login_user(request, user)
    return {"user": user}


@router.api_route("/logout")
async def logout(request: Request):
    await logout_user(request)
