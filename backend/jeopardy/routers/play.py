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
    # Check authentication
    if not user.is_active:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        return
    await websocket.accept()

    while True:
        data = await websocket.receive_json()
        await websocket.send_json(data)
