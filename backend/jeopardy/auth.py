from os import getenv

from authlib.integrations.starlette_client import OAuth
from fastapi import Depends
from fastapi import Request

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


async def login_user(request: Request, user: UserOrm) -> None:
    user_token = await token_from_user(user)
    request.session["user_token"] = user_token


async def logout_user(request: Request) -> None:
    if "user_token" in request.session:
        request.session.pop("user_token")


async def token_from_user(user: UserOrm) -> str:
    return str(user.id)


async def user_from_token(token: str) -> UserOrm:
    return await UserOrm.get_or_none(id=token)


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
