from os import getenv

from authlib.integrations.starlette_client import OAuth

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
        display_name = metadata.given_name or metadata.email
        user = await UserOrm.create(
            display_name=display_name,
            auth_provider="google",
            google_metadata=metadata,
        )
    else:
        await metadata.fetch_related("user")
        user = metadata.user[0]

    return user
