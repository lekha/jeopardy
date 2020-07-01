from tortoise import fields

from jeopardy.models.base import BaseOrmModel


class Game(BaseOrmModel):
    name = fields.CharField(255)
    code = fields.CharField(4, unique=True)
    owner = fields.ForeignKeyField("models.UserOrm", related_name="games")
    max_teams = fields.IntField()
    max_players_per_team = fields.IntField()
    is_active = fields.BooleanField(default=False)

    class Meta:
        table = "games"

    def __str__(self):
        return f"Game({self.id}, {self.code}, {self.name})"
