from jeopardy.models.action import ActionType
from jeopardy.models.game import GameOrm
from jeopardy.models.game import TileOrm
from jeopardy.models.user import UserOrm


async def is_active_game(game: GameOrm) -> bool:
    """Confirm that the game is active."""
    return game.is_started and not game.is_finished
