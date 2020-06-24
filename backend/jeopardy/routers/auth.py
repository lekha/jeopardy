from fastapi import APIRouter
from fastapi import Request

from jeopardy.auth import oauth


router = APIRouter()


@router.api_route("/login")
async def login(request: Request):
    callback_url = request.url_for("callback")
    return await oauth.google.authorize_redirect(request, callback_url)


@router.api_route("/oauth2callback")
async def callback(request: Request):
    token = await oauth.google.authorize_access_token(request)
    user = await oauth.google.parse_id_token(request, token)
    import logging
    logging.error(user)
    return user
