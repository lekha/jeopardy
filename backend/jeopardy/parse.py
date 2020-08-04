from typing import Dict

from pydantic import ValidationError

from jeopardy.exceptions import ForbiddenActionException
from jeopardy.exceptions import MissingFieldException
from jeopardy.models.action import ActionOrmModel
from jeopardy.models.action import ActionType
from jeopardy.models.action import BuzzOrm
from jeopardy.models.action import ChoiceOrm
from jeopardy.models.action import ResponseOrm
from jeopardy.models.action import WagerOrm
from jeopardy.models.game import TileOrm
from jeopardy.schema.action import Action
from jeopardy.schema.action import Request
from jeopardy.schema.action import Response
from jeopardy.schema.action import Wager


def action_orm_from_type(action_type: ActionType) -> ActionOrmModel:
    type_to_orm = {
        ActionType.CHOICE:   ChoiceOrm,
        ActionType.BUZZ:     BuzzOrm,
        ActionType.RESPONSE: ResponseOrm,
        ActionType.WAGER:    WagerOrm,
    }
    return type_to_orm[action_type]


def action_schema_from_type(action_type: ActionType) -> Action:
    type_to_schema = {
        ActionType.CHOICE:   Action,
        ActionType.BUZZ:     Action,
        ActionType.RESPONSE: Response,
        ActionType.WAGER:    Wager,
    }
    return type_to_schema[action_type]


def parse_game_code(game_code: str) -> str:
    return game_code.upper()


def parse_request(action_type: ActionType, request: Dict) -> Request:
    action = action_schema_from_type(action_type)
    try:
         request = Request[action].parse_obj(request)
    except ValidationError as exc:
        if "type_error.enum" in [x["type"] for x in exc.errors()]:
            raise ForbiddenActionException(action_type)
        else:
            raise MissingFieldException(Request[action].schema_json())

    if request.action.type_ != action_type:
        raise ForbiddenActionException(action_type)

    return request
