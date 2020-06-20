from tortoise import fields
from tortoise.models import Model


class BaseModel(Model):
    id = fields.BigIntField(pk=True)
    created_ts = fields.DatetimeField(auto_now_add=True)
    updated_ts = fields.DatetimeField(auto_now=True)

    class Meta:
        abstract = True
