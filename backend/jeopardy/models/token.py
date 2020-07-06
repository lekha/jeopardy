from tortoise import fields

from jeopardy.models.base import BaseOrmModel


class UserTokenOrm(BaseOrmModel):
    value = fields.CharField(255, source_field="token", unique=True)
    user = fields.ForeignKeyField(
        "models.UserTokenOrm",
        related_name="token",
        on_delete="CASCADE",
    )
    is_active = fields.BooleanField(default=1)
    expire_seconds = fields.IntField(default=3600)

    class Meta:
        table = "user_tokens"

    def __str__(self):
        return f"UserToken({self.user_id, self.value})"
