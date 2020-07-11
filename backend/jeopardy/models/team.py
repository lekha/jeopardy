from tortoise import fields

from jeopardy.models.base import BaseOrmModel


class TeamOrm(BaseOrmModel):
    game = fields.ForeignKeyField("models.GameOrm", related_name="teams")
    name = fields.CharField(255)

    class Meta:
        table = "teams"
        unique_together=(("game", "name"))

    def __str__(self):
        return f"Team({self.id}, {self.name})"
