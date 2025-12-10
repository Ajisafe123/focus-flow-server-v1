from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from src.utils.ws_manager import manager

router = APIRouter(prefix="/ws/notifications", tags=["WebSocket-Notifications"])


@router.websocket("/{room}")
async def websocket_notifications(websocket: WebSocket, room: str):
    """
    Clients should connect with room = user_id for personal notifications
    or 'all' for broadcast messages.
    """
    await manager.connect(f"notifications:{room}", websocket)
    try:
        while True:
            # notifications are push-only; echo back any ping payload
            data = await websocket.receive_json()
            await manager.send_personal(websocket, {"event": "ack", "data": data})
    except WebSocketDisconnect:
        manager.disconnect(f"notifications:{room}", websocket)

