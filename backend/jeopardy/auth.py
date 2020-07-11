from datetime import datetime
from datetime import timedelta
from os import getenv
from typing import Optional

from authlib.integrations.starlette_client import OAuth
from fastapi import Depends
from fastapi import Header
from fastapi import Response
import jwt

from jeopardy.models.user import GoogleUserMetadataOrm
from jeopardy.models.user import UserOrm
from jeopardy.schema.user import GoogleUserMetadata


oauth = OAuth()


oauth.register(
    name="google",
    server_metadata_url="https://accounts.google.com/.well-known/openid-configuration",
    client_id=getenv("GOOGLE_CLIENT_ID"),
    client_secret=getenv("GOOGLE_CLIENT_SECRET"),
    client_kwargs={
        "scope": "openid email profile",
    }
)


class Nobody:
    id = None
    is_active = False


async def login_user(response: Response, user: UserOrm) -> None:
    user_token = await token_from_user(user)
    response.set_cookie("user", value=user_token)


async def logout_user(response: Response) -> None:
    response.delete_cookie("user")


async def token_from_user(user: UserOrm) -> str:
    """Create a new JWT associated with a user."""
    now = datetime.utcnow()
    time_to_expiration = timedelta(seconds=3600)
    payload = {
        "iat": now,
        "exp": now + time_to_expiration,
        "sub": user.id,
        "roles": ["player"],
        "name": user.username,
    }

    unescaped_private_key = getenv("RSA_PRIVATE_KEY")
    private_key = unescaped_private_key.encode("utf-8").decode("unicode_escape")

    token_bytes = jwt.encode(payload, private_key, algorithm="RS256")
    return token_bytes.decode("utf-8")


async def user_from_token(token: str) -> UserOrm:
    """Determine the user associated with a JWT."""
    unescaped_public_key = getenv("RSA_PUBLIC_KEY")
    public_key = unescaped_public_key.encode("utf-8").decode("unicode_escape")

    try:
        token_bytes = token.encode("utf-8")
        payload = jwt.decode(token_bytes, public_key, algorithms="RS256")
        user_id = payload["sub"]
        user = await UserOrm.get_or_none(id=user_id)
    except:
        user = Nobody

    return user


async def user_from_google_metadata(
    new_metadata: GoogleUserMetadata
) -> UserOrm:
    """Fetch pre-existing user associated with the metadata.

    Create new user if one doesn't already exist.
    """
    # Update old metadata or create new one
    old_metadata = await GoogleUserMetadataOrm.get_or_none(
        subject=new_metadata.subject
    )
    if old_metadata is None:
        metadata = GoogleUserMetadataOrm(**new_metadata.dict())
    else:
        metadata = old_metadata
        metadata.update_from_dict(new_metadata.dict())
    await metadata.save()

    # Fetch old user or create new one
    if old_metadata is None:
        username = metadata.given_name or metadata.email
        user = await UserOrm.create(
            username=username,
            auth_provider="google",
            google_metadata=metadata,
        )
    else:
        await metadata.fetch_related("user")
        user = metadata.user[0]

    return user


async def current_user(authorization: Optional[str] = Header(None)):
    """Determine the currently-logged in user from the request header."""
    try:
        user = await user_from_token(authorization)
        if not user.is_active:
            user = Nobody
    except:
        user = Nobody
    return user
