import logging
from typing import Mapping

from fastapi import APIRouter
from fastapi import Depends
from fastapi import status
from starlette.websockets import WebSocket

from jeopardy import exceptions
from jeopardy import state
from jeopardy.auth import current_user
from jeopardy.models.game import GameOrm
from jeopardy.models.game import GameStatus
from jeopardy.models.user import UserOrm
from jeopardy.play import assign
from jeopardy.play import game_from_code
from jeopardy.play import start
from jeopardy.validation import is_active_game


router = APIRouter()


@router.get("/game/{raw_game_code}")
async def get_game(game: GameOrm = Depends(game_from_code)) -> Mapping:
    return (await state.full(game)).dict()


@router.post("/start/{raw_game_code}")
async def start_game(game: GameOrm = Depends(game_from_code)) -> Mapping:
    """Allow users to start joining a game."""
    if game.status == GameStatus.EDITABLE:
        await start(game)
    return (await state.full(game)).dict()


@router.websocket("/play/{game_code}")
async def play(
    websocket: WebSocket,
    game_code: str,
    user: UserOrm = Depends(current_user),
) -> None:
    logging.info(f"New user attempting to connect to game: {game_code}")
    await websocket.accept()
    frontend_endpoint = f"play.{game_code}"

    # Check authentication
    if not user.is_active:
        redirect_to_login = {
            "status_code": 302,
            "redirect_url": f"/user/login?next={frontend_endpoint}",
        }
        await websocket.send_json(redirect_to_login)
        await websocket.close()
        return

    # Find game
    try:
        game = await game_from_code(game_code)
        if not (await is_active_game(game)):
            raise exceptions.ForbiddenAccessException
    except exceptions.ForbiddenAccessException:
        game_unavailable_response = {
            "status_code": 404,
            "message": "Game unavailable. Please check the URL entered.",
        }
        await websocket.send_json(game_unavailable_response)
        await websocket.close()
        return

    # Assign to team
    team_state = await state.full(game)
    team_state.display.level = "team"
    await websocket.send_json(team_state.json())

    while True:
        data = await websocket.receive_json()
        if data["action"]["type"] == "join":
            team_name = data["action"]["team"]
            await assign(game, user, team_name)

        team_state = await state.full(game)
        team_state.display.level = "team"
        await websocket.send_json(team_state.json())

    while True:
        data = await websocket.receive_json()
        await websocket.send_json(data)
