from tortoise import fields

from jeopardy.models.base import BaseOrmModel


class TeamOrm(BaseOrmModel):
    game = fields.ForeignKeyField("models.GameOrm", related_name="teams")
    name = fields.CharField(255)
    players = fields.ManyToManyField(
        "models.UserOrm",
        related_name="teams",
        through="team_memberships",
        forward_key="user_id",
        backward_key="team_id",
    )

    class Meta:
        table = "teams"
        unique_together=(("game", "name"))

    def __str__(self):
        return f"Team({self.id}, {self.name})"


class TeamMembershipOrm(BaseOrmModel):
    team = fields.ForeignKeyField("models.TeamOrm")
    user = fields.ForeignKeyField("models.UserOrm", index=True)

    class Meta:
        table = "team_memberships"
        unique_together = (("team", "user"))

    def __str__(self):
        return f"TeamMembership({self.team}, {self.user})"
