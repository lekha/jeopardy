from jeopardy.models.action import ActionType
from jeopardy.models.game import GameOrm
from jeopardy.models.game import TileOrm
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

    await game.fetch_related("teams__players")
    for team in game.teams:
        for player in team.players:
            if player.id == user.id:
                return True

    return False
