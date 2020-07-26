from enum import Enum

from tortoise import fields

from jeopardy.models.action import ActionType
from jeopardy.models.base import BaseOrmModel


class RoundClass(Enum):
    SINGLE = "single"
    DOUBLE = "double"
    FINAL  = "final"


class GameOrm(BaseOrmModel):
    name = fields.CharField(255)
    code = fields.CharField(4, unique=True)
    owner = fields.ForeignKeyField("models.UserOrm", related_name="games")
    max_teams = fields.IntField()
    max_players_per_team = fields.IntField()
    is_started = fields.BooleanField(default=False)
    is_finished = fields.BooleanField(default=False)
    next_message_id = fields.BigIntField(null=True)
    next_round = fields.ForeignKeyField(
        "models.RoundOrm",
        related_name=None,
        on_delete="RESTRICT",
        null=True,
    )
    next_action_type = fields.CharEnumField(ActionType, null=True)
    next_chooser = fields.ForeignKeyField(
        "models.TeamOrm",
        related_name=None,
        on_delete="RESTRICT",
        null=True,
    )

    class Meta:
        table = "games"

    def __str__(self):
        return f"Game({self.id}, {self.code}, {self.name})"


class RoundOrm(BaseOrmModel):
    game = fields.ForeignKeyField(
        "models.GameOrm",
        related_name="rounds",
        on_delete="CASCADE",
    )
    class_ = fields.CharEnumField(RoundClass, source_field="class")
    ordinal = fields.IntField()

    class Meta:
        table = "rounds"
        unique_together = (("game", "class_"))

    def __str__(self):
        return f"Round({self.id}, {self.game})"


class BoardOrm(BaseOrmModel):
    round_ = fields.ForeignKeyField(
        "models.RoundOrm",
        source_field="round_id",
        related_name="board",
        on_delete="CASCADE",
    )
    num_categories = fields.IntField(
        default=6,
        source_field="categories"
    )
    num_tiles_per_category = fields.IntField(
        default=5,
        source_field="tiles_per_category"
    )

    class Meta:
        table = "boards"

    def __str__(self):
        return f"Board({self.id, self.round_})"


class CategoryOrm(BaseOrmModel):
    board = fields.ForeignKeyField(
        "models.BoardOrm",
        related_name="categories",
        on_delete="CASCADE",
    )
    name = fields.CharField(255)
    ordinal = fields.IntField()

    class Meta:
        table = "categories"
        unique_together = (("board", "name"), ("board", "ordinal"))

    def __str__(self):
        return f"Category({self.id}, {self.name})"


class TileOrm(BaseOrmModel):
    category = fields.ForeignKeyField(
        "models.CategoryOrm",
        related_name="tiles",
        on_delete="CASCADE",
    )
    trivia = fields.ForeignKeyField(
        "models.TriviaOrm",
        related_name="tiles",
        on_delete="RESTRICT",
    )
    ordinal = fields.IntField()
    is_daily_double = fields.BooleanField(default=False)

    class Meta:
        table = "tiles"
        unique_together = (("category", "trivia"), ("category", "ordinal"))

    def __str__(self):
        return f"Tile({self.id}, {self.category}, {self.points})"


class TriviaOrm(BaseOrmModel):
    answer = fields.TextField()
    question = fields.TextField()

    class Meta:
        table = "trivia"

    def __str__(self):
        return f"Trivia({self.id}, {self.answer})"
