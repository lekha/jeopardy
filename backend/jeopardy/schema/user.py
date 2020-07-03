from typing import Optional

from pydantic import BaseModel
from pydantic import constr

from jeopardy.models.user import AuthProvider


class AnonymousUserMetadata(BaseModel):
    expire_seconds: int = 8*3600  # 8 hours chosen arbitrarily


class GoogleUserMetadata(BaseModel):
    subject: constr(max_length=255)
    email: constr(max_length=255)
    given_name: Optional[constr(max_length=255)] = None
    issuer: constr(max_length=255)
    family_name: Optional[constr(max_length=255)] = None
    name: Optional[constr(max_length=255)] = None
    locale: Optional[constr(max_length=255)] = None
    picture: Optional[constr(max_length=255)] = None


class User(BaseModel):
    display_name: constr(max_length=255)
    is_active: bool = True
    auth_provider: AuthProvider
    anonymous_metadata: Optional[AnonymousUserMetadata] = None
    google_metadata: Optional[GoogleUserMetadata] = None
