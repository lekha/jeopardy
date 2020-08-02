import inspect

from jeopardy.models.action import ActionOrmModel
from jeopardy.models.action import ActionType
from jeopardy.models.action import ResponseOrm
from jeopardy.models.game import GameOrm
from jeopardy.models.game import RoundClass
from jeopardy.models.game import RoundOrm
from jeopardy.models.game import TileOrm
from jeopardy.models.user import UserOrm


async def next_round_action_type(prev_action: ActionOrmModel) -> ActionType:
    """Determine actions that are permitted next in the round."""
    basic_round_mapping = {
        None:                ActionType.CHOICE,
        ActionType.BUZZ:     ActionType.RESPONSE,
        ActionType.CHOICE:   _buzz_or_wager,
        ActionType.RESPONSE: _buzz_or_choice_if_tiles_available,
        ActionType.WAGER:    ActionType.RESPONSE,
    }
    final_round_mapping = {
        None:                ActionType.WAGER,
        ActionType.RESPONSE: _collect_responses,
        ActionType.WAGER:    _collect_wagers,
    }

    round_ = await prev_action.round_
    if round_.class_ == RoundClass.FINAL:
        next_action_type_mapping = final_round_mapping
    else:
        next_action_type_mapping = basic_round_mapping

    func_or_const = next_action_type_mapping[prev_action.type_]
    if inspect.iscoroutinefunction(func_or_const):
        next_action_type = await func_or_const(prev_action)
    else:
        next_action_type = func_or_const

    return next_action_type


async def _buzz_or_wager(prev_action: ActionOrmModel) -> ActionType:
    """Helper for determining next action type."""
    await prev_action.fetch_related("tile")
    if prev_action.tile.is_daily_double:
        next_action_type = ActionType.WAGER
    else:
        next_action_type = ActionType.BUZZ
    return next_action_type


async def _buzz_or_choice_if_tiles_available(
    prev_action: ResponseOrm
) -> ActionType:
    """Helper for determining next action type."""
    if await _all_teams_have_response(prev_action):
        tiles_available = (
            await TileOrm
            .filter(category__board__round_=await prev_action.round_)
            .filter(choices__id=None)
            .count()
        )
        if tiles_available:
            next_action_type = ActionType.CHOICE
        else:
            next_action_type = None

    elif prev_action.is_correct:
        next_action_type = ActionType.CHOICE

    else:
        next_action_type = ActionType.BUZZ

    return next_action_type


async def _collect_responses(prev_action: ActionOrmModel) -> ActionType:
    """Helper for determining next action type."""
    await prev_action.fetch_related("game__teams")
    await prev_action.fetch_related("tile__responses")
    if await _all_teams_have_response(prev_action):
        next_action_type = None
    else:
        next_action_type = ActionType.RESPONSE
    return next_action_type


async def _all_teams_have_response(prev_action: ActionOrmModel) -> bool:
    """Helper for determining next action type."""
    await prev_action.fetch_related("game__teams")
    await prev_action.fetch_related("tile__responses")
    return len(prev_action.game.teams) == len(prev_action.tile.responses)


async def _collect_wagers(prev_action: ActionOrmModel) -> ActionType:
    """Helper for determining next action type."""
    await prev_action.fetch_related("game__teams")
    await prev_action.fetch_related("tile__wagers")
    if len(prev_action.game.teams) != len(prev_action.tile.wagers):
        next_action_type = ActionType.WAGER
    else:
        next_action_type = ActionType.RESPONSE
    return next_action_type
