from tortoise import fields

from jeopardy.models.base import BaseModel


class Player(BaseModel):
    name = fields.CharField(255)

    def __str__(self):
        return f"Player({self.id}, {self.name})"
