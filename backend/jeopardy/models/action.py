from enum import Enum

from async_property import async_cached_property
from async_property import async_property
from tortoise import fields
from tortoise.models import ModelMeta

from jeopardy.models.base import BaseOrmModel


class ActionType(Enum):
    BUZZ     = "buzz"
    CHOICE   = "choice"
    RESPONSE = "response"
    WAGER    = "wager"


class ActionOrmModelMeta(ModelMeta):
    def __new__(cls, name, bases, attrs):
        extra_foreign_keys = {
            "game": "models.GameOrm",
            "tile": "models.TileOrm",
            "team": "models.TeamOrm",
            "user": "models.UserOrm",
        }
        related_name = attrs.get("_related_name")
        for field_name, model_name in extra_foreign_keys.items():
            attrs[field_name] = fields.ForeignKeyField(
                model_name,
                related_name=related_name,
            )

        return super().__new__(cls, name, bases, attrs)


class ActionOrmModel(BaseOrmModel, metaclass=ActionOrmModelMeta):
    """Automatically add default foreign keys to all actions."""
    class Meta:
        abstract = True

    @async_cached_property
    async def round_(self):
        return await self.tile.category.board.round_


class NoAction:
    type_ = None

    def __init__(self, round_):
        self._round = round_

    @async_property
    async def round_(self):
        return self._round


class ChoiceOrm(ActionOrmModel):
    _related_name = "choices"
    type_ = ActionType.CHOICE

    class Meta:
        table = "action_choices"
        unique_together = (("game", "tile"))

    def __str__(self):
        return f"Choice({self.id}, {self.game})"


class BuzzOrm(ActionOrmModel):
    _related_name = "buzzes"
    type_ = ActionType.BUZZ

    class Meta:
        table = "action_buzzes"
        unique_together = (("game", "tile", "team"))

    def __str__(self):
        return f"Buzz({self.id}, {self.game})"


class ResponseOrm(ActionOrmModel):
    _related_name = "responses"
    type_ = ActionType.RESPONSE
    is_correct = fields.BooleanField()

    class Meta:
        table = "action_responses"
        unique_together = (("game", "tile", "team"))

    def __str__(self):
        return f"Response({self.id}, {self.game})"


class WagerOrm(ActionOrmModel):
    _related_name = "wagers"
    type_ = ActionType.WAGER
    amount = fields.IntField()

    class Meta:
        table = "action_wagers"
        unique_together = (("game", "tile", "team"))

    def __str__(self):
        return f"Wager({self.id}, {self.game})"
