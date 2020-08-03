from typing import List
from typing import Optional

from pydantic import BaseModel
from pydantic import Field
from pydantic import constr
from pydantic import validator

from jeopardy.models.game import RoundClass


def cast_to_list(value) -> List:
    return [x for x in value]


def first(value):
    return value[0]


def sorted_by_ordinal(value) -> List:
    result = [x for x in value]
    result.sort(key=lambda x: x.ordinal)
    return result


class Player(BaseModel):
    username: str

    class Config:
        orm_mode = True


class Team(BaseModel):
    has_pressed_buzzer: bool = False
    name: str
    players: List[Player] = []

    class Config:
        orm_mode = True

    _player = validator("players", pre=True, allow_reuse=True)(cast_to_list)


class Tile(BaseModel):
    id: int
    answer: Optional[str] = Field(alias="trivia")
    question: Optional[str] = Field(alias="trivia")
    points: Optional[int]

    class Config:
        orm_mode = True

    @validator("answer", pre=True)
    def flatten_answer(cls, value):
        return value.answer

    @validator("question", pre=True)
    def flatten_question(cls, value):
        return value.question


class Category(BaseModel):
    id: int
    name: Optional[str]
    tiles: List[Tile] = []

    class Config:
        orm_mode = True

    _tiles = validator("tiles", pre=True, allow_reuse=True)(sorted_by_ordinal)


class Board(BaseModel):
    categories: List[Category] = []
    num_categories: int

    class Config:
        orm_mode = True

    _categories = validator(
        "categories", pre=True, allow_reuse=True
    )(sorted_by_ordinal)


class Round(BaseModel):
    class_: RoundClass
    board: Optional[Board] = Field(alias="board")

    class Config:
        orm_mode = True

    _board = validator("board", pre=True, allow_reuse=True)(first)


class Display(BaseModel):
    level: str = "game"
    id: Optional[int]


class Game(BaseModel):
    code: constr(min_length=4, max_length=4)
    display: Display = Field(default_factory=Display)
    message_id: int = Field(alias="next_message_id")
    round_: Optional[Round] = Field(alias="next_round")
    team_that_chooses: Optional[str] = Field(alias="next_chooser")
    teams: List[Team] = []
    status: str = "joinable"

    class Config:
        orm_mode = True

    _team = validator("teams", pre=True, allow_reuse=True)(cast_to_list)

    @validator("team_that_chooses", pre=True)
    def parse_team_that_chooses(cls, value):
        return getattr(value, "name", None)
