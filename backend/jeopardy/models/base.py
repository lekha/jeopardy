from tortoise import fields
from tortoise.models import Model as TortoiseModel


class BaseOrmModel(TortoiseModel):
    id = fields.BigIntField(pk=True, generated=True)
    created_ts = fields.DatetimeField(auto_now_add=True)
    updated_ts = fields.DatetimeField(auto_now=True)

    class Meta:
        abstract = True
