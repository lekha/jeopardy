import inspect

from jeopardy.models.action import ActionOrmModel
from jeopardy.models.action import ActionType
from jeopardy.models.action import BuzzOrm
from jeopardy.models.action import ChoiceOrm
from jeopardy.models.action import ResponseOrm
from jeopardy.models.action import WagerOrm
from jeopardy.models.game import GameOrm
from jeopardy.models.game import RoundClass
from jeopardy.models.game import RoundOrm
from jeopardy.models.game import TileOrm
from jeopardy.models.team import TeamOrm
from jeopardy.models.user import UserOrm


async def is_active_game(game: GameOrm) -> bool:
    """Confirm that the game is active."""
    return game.is_started and not game.is_finished


async def is_player(game: GameOrm, user: UserOrm) -> bool:
    """Confirm that the user is a participant of the game.

    This holds when the player is an active user and a member of a team in the
    game.
    """
    if not user.is_active:
        return False

    team = await user.team(game)
    return team is not None


async def is_permitted_to_act(
    game: GameOrm, player: UserOrm, action_type: ActionType, tile: TileOrm
) -> bool:
    """Determine if chosen player is allowed to perform the next action.

    It is assumed that the player is already part of a team involved with the
    game, that the game is active, and that the action is a valid next action.
    """
    team = await player.team(game)
    round_ = await tile.category.board.round_

    if round_.class_ == RoundClass.FINAL:
        is_permitted = not await _has_team_acted(team, action_type, tile)

    elif action_type == ActionType.BUZZ:
        is_permitted = all((
            len(await tile.choices) == 1,
            not await _has_team_acted(team, action_type, tile),
        ))

    elif action_type == ActionType.CHOICE:
        is_permitted = all((
            team == await game.next_chooser,
            len(await tile.choices) == 0,
        ))

    elif action_type == ActionType.RESPONSE:
        if tile.is_daily_double:
            prev_action_type = ActionType.WAGER
        else:
            prev_action_type = ActionType.BUZZ
        is_permitted = await _has_team_acted(team, prev_action_type, tile)

    elif action_type == ActionType.WAGER:
        is_permitted = await _has_team_acted(team, ActionType.CHOICE, tile)

    return is_permitted


async def _has_team_acted(
    team: TeamOrm, action_type: ActionType, tile: TileOrm
) -> bool:
    """Determine if team has performed the action on the tile."""
    action = _orm_from_type(action_type)
    return await action.exists(team=team, tile=tile)


def _orm_from_type(action_type: ActionType) -> ActionOrmModel:
    type_to_action = {
        ActionType.CHOICE:   ChoiceOrm,
        ActionType.BUZZ:     BuzzOrm,
        ActionType.RESPONSE: ResponseOrm,
        ActionType.WAGER:    WagerOrm,
    }
    return type_to_action[action_type]


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


async def is_valid_action(
    game: GameOrm,
    round_: RoundOrm,
    user: UserOrm,
    action_type: ActionType,
    tile: TileOrm,
) -> bool:
    """Validate a player's incoming request to perform an action on a tile."""
    return (
        game is not None
        and round_ is not None
        and user is not None
        and action_type is not None
        and tile is not None
        and await is_active_game(game)
        and await is_player(game, user)
        and round_ == await game.next_round
        and action_type == game.next_action_type
        and await is_permitted_to_act(game, user, action_type, tile)
    )
