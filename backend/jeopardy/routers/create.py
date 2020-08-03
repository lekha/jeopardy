from typing import Mapping

from fastapi import APIRouter
from fastapi import Depends

from jeopardy import create
from jeopardy.auth import current_user
from jeopardy.models.user import UserOrm
from jeopardy.schema.state import Game


router = APIRouter()


@router.post("/game")
async def create_game(
    max_teams: int = 3,
    max_players_per_team: int = 3,
    user: UserOrm = Depends(current_user),
) -> Mapping:
    """Create a new game."""
    new_game = await create.game(
        owner=user,
        name="Untitled Game",
        max_teams=max_teams,
        max_players_per_team=max_players_per_team,
    )
    return new_game.dict()
