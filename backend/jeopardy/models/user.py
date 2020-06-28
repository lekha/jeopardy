from enum import Enum

from tortoise import fields

from jeopardy.models.base import BaseModel


class AuthProvider(Enum):
    NONE   = "none"
    GOOGLE = "google"


class AnonymousUserMetadata(BaseModel):
    expire_ts = fields.DatetimeField()

    class Meta:
        table = "user_metadata_anonymous"

    def __str__(self):
        return f"AnonymousUserMetadata({self.id})"


class GoogleUserMetadata(BaseModel):
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


class User(BaseModel):
    display_name = fields.CharField(255)
    is_active = fields.BooleanField(default=1)
    auth_provider = fields.CharEnumField(AuthProvider)
    anonymous_metadata = fields.ForeignKeyField(
        "models.AnonymousUserMetadata",
        related_name="user",
        on_delete="RESTRICT",
        null=True,
    )
    google_metadata = fields.ForeignKeyField(
        "models.GoogleUserMetadata",
        related_name="user",
        on_delete="RESTRICT",
        null=True,
    )

    class Meta:
        table = "users"

    def __str__(self):
        return f"User({self.id}, {self.display_name})"
