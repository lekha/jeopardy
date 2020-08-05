from enum import Enum

from tortoise import fields

from jeopardy.models.base import BaseOrmModel


class BoardLevel(Enum):
    CATEGORY = "category"
    TILE = "tile"


class BoardLevelDetail(Enum):
    NAME = "name"
    IS_DAILY_DOUBLE = "is_daily_double"
    ANSWER = "answer"
    QUESTION = "question"


class RoundRevealOrm(BaseOrmModel):
    round_ = fields.ForeignKeyField(
        "models.RoundOrm",
        source_field="round_id",
        related_name="reveals",
        on_delete="CASCADE",
    )
    level = fields.CharEnumField(BoardLevel)
    level_id = fields.BigIntField()
    detail = fields.CharEnumField(BoardLevelDetail)

    class Meta:
        table = "round_reveals"
        unique_together = (("round_", "level", "level_id", "detail"))

    def __str__(self):
        return f"RoundReveal({self.id}, {self.level}, self.level_id)"
