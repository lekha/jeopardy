from typing import Generic
from typing import TypeVar

from async_property import async_cached_property
from async_property.cached import AsyncCachedPropertyDescriptor
from pydantic import BaseModel
from pydantic import Field
from pydantic.generics import GenericModel

from jeopardy.models.action import ActionType
from jeopardy.models.game import TileOrm


ActionT = TypeVar("ActionT")


class Action(BaseModel):
    type_: ActionType = Field(..., alias="type")
    tile_id: int

    class Config:
        allow_mutation = False
        keep_untouched = (AsyncCachedPropertyDescriptor,)

    @async_cached_property
    async def tile(self):
        return await TileOrm.get_or_none(id=self.tile_id)


class Response(Action):
    question: str


class Wager(Action):
    amount: int


class Request(GenericModel, Generic[ActionT]):
    message_id: int
    action: ActionT

    class Config:
        allow_mutation = False
