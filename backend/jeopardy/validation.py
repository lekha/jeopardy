from typing import Optional

from jeopardy import exceptions
from jeopardy.models.action import ActionType
from jeopardy.models.game import GameOrm
from jeopardy.models.game import RoundClass
from jeopardy.models.game import TileOrm
from jeopardy.models.team import TeamOrm
from jeopardy.models.user import UserOrm
from jeopardy.schema.action import Request
from jeopardy.parse import action_orm_from_type


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
        is_permitted = team == await game.next_chooser

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
    action = action_orm_from_type(action_type)
    return await action.exists(team=team, tile=tile)


def is_permitted_wager(team: TeamOrm, amount: int) -> bool:
    """Determine if team is allowed to wager an amount."""
    explicitly_forbidden = {14, 69, 88, 666, 1488}
    return 0 < amount < team.score and amount not in explicitly_forbidden


async def validate_game(game: Optional[GameOrm]) -> None:
    """Validate that the game is currently being played."""
    if game is None or not await is_active_game(game):
        raise exceptions.ForbiddenAccessException


async def validate_user(game: GameOrm, user: UserOrm) -> None:
    """Validate that the user is a player in the game."""
    if not await is_player(game, user):
        raise exceptions.ForbiddenAccessException


async def validate_request(
    game: GameOrm, user: UserOrm, request: Request
) -> None:
    """Validate a player's incoming request to perform an action on a tile."""
    if request.message_id != game.next_message_id:
        raise exceptions.InvalidRequestException

    if request.action.type_ != game.next_action_type:
        raise exceptions.ForbiddenActionException(game.next_action_type)

    tile = await request.action.tile

    if tile is None:
        raise exceptions.TileNotFoundException

    if await tile.round_ != await game.next_round:
        raise exceptions.TileNotFoundException

    action_type = request.action.type_

    if not await is_permitted_to_act(game, user, action_type, tile):
        raise exceptions.ActOutOfTurnException

    if action_type == ActionType.CHOICE:
        if len(await tile.choices) > 0:
            raise exceptions.TileAlreadyChosenException

    if action_type == ActionType.WAGER:
        team = await user.team(game)
        if not is_permitted_wager(team, request.action.amount):
            raise exceptions.ForbiddenWagerException
