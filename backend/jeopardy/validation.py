from jeopardy.models.action import ActionType
from jeopardy.models.game import GameOrm
from jeopardy.models.game import RoundClass
from jeopardy.models.game import RoundOrm
from jeopardy.models.game import TileOrm
from jeopardy.models.team import TeamOrm
from jeopardy.models.user import UserOrm
from jeopardy.parse import action_from_type


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
    action = action_from_type(action_type)
    return await action.exists(team=team, tile=tile)


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
