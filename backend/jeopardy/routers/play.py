import logging

from fastapi import APIRouter
from fastapi import Depends
from fastapi import status
from starlette.websockets import WebSocket

from jeopardy.auth import current_user
from jeopardy.models.user import UserOrm


router = APIRouter()


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

    while True:
        data = await websocket.receive_json()
        await websocket.send_json(data)
