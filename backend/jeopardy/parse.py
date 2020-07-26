from jeopardy.models.action import ActionOrmModel
from jeopardy.models.action import ActionType
from jeopardy.models.action import BuzzOrm
from jeopardy.models.action import ChoiceOrm
from jeopardy.models.action import ResponseOrm
from jeopardy.models.action import WagerOrm


def action_from_type(action_type: ActionType) -> ActionOrmModel:
    type_to_action = {
        ActionType.CHOICE:   ChoiceOrm,
        ActionType.BUZZ:     BuzzOrm,
        ActionType.RESPONSE: ResponseOrm,
        ActionType.WAGER:    WagerOrm,
    }
    return type_to_action[action_type]
