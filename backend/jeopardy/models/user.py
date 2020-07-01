from enum import Enum
from typing import Optional

from pydantic import BaseModel as PydanticOrmModel
from pydantic import constr
from tortoise import fields

from jeopardy.models.base import BaseOrmModel


class AuthProvider(Enum):
    NONE   = "none"
    GOOGLE = "google"


class AnonymousUserMetadata(PydanticOrmModel):
    expire_seconds: int = 8*3600  # 8 hours chosen arbitrarily


class AnonymousUserMetadataOrm(BaseOrmModel):
    expire_seconds = fields.IntField(default=8*3600)

    class Meta:
        table = "user_metadata_anonymous"

    def __str__(self):
        return f"AnonymousUserMetadata({self.id})"


class GoogleUserMetadata(PydanticOrmModel):
    subject: constr(max_length=255)
    email: constr(max_length=255)
    given_name: Optional[constr(max_length=255)] = None
    issuer: constr(max_length=255)
    family_name: Optional[constr(max_length=255)] = None
    name: Optional[constr(max_length=255)] = None
    locale: Optional[constr(max_length=255)] = None
    picture: Optional[constr(max_length=255)] = None


class GoogleUserMetadataOrm(BaseOrmModel):
    subject = fields.CharField(255, unique=True)
    email = fields.CharField(255)
    given_name = fields.CharField(255, null=True)
    issuer = fields.CharField(255)
    family_name = fields.CharField(255, null=True)
    name = fields.CharField(255, null=True)
    locale = fields.CharField(255, null=True)
    picture = fields.CharField(255, null=True)

    class Meta:
        table = "user_metadata_google"

    def __str__(self):
        return f"GoogleUserMetadata({self.id}, {self.email})"


class User(PydanticOrmModel):
    display_name: constr(max_length=255)
    is_active: bool = True
    auth_provider: AuthProvider
    anonymous_metadata: Optional[AnonymousUserMetadata] = None
    google_metadata: Optional[GoogleUserMetadata] = None


class UserOrm(BaseOrmModel):
    display_name = fields.CharField(255)
    is_active = fields.BooleanField(default=1)
    auth_provider = fields.CharEnumField(AuthProvider)
    anonymous_metadata = fields.ForeignKeyField(
        "models.AnonymousUserMetadataOrm",
        related_name="user",
        on_delete="RESTRICT",
        null=True,
    )
    google_metadata = fields.ForeignKeyField(
        "models.GoogleUserMetadataOrm",
        related_name="user",
        on_delete="RESTRICT",
        null=True,
    )

    class Meta:
        table = "users"

    def __str__(self):
        return f"User({self.id}, {self.display_name})"
