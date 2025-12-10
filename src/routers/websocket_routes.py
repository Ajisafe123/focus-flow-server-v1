from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from src.utils.ws_manager import manager

router = APIRouter(prefix="/ws/chat", tags=["WebSocket"])

@router.websocket("/{conversation_id}")
async def websocket_endpoint(websocket: WebSocket, conversation_id: str):
    await manager.connect(conversation_id, websocket)
    try:
        while True:
            data = await websocket.receive_json()
            action = data.get("action")
            payload = data.get("payload")
            if action == "send_message":
                await manager.broadcast_room(conversation_id, {"event": "receive_message", "data": payload})
            elif action == "typing":
                await manager.broadcast_room(conversation_id, {"event": "typing", "data": payload})
            elif action == "message_read":
                await manager.broadcast_room(conversation_id, {"event": "messages_read", "data": payload})
            else:
                await manager.send_personal(websocket, {"event": "unknown", "action": action})
    except WebSocketDisconnect:
        await manager.disconnect_async(conversation_id, websocket)
@router.websocket("/admin")
async def admin_websocket_endpoint(websocket: WebSocket):
    await manager.connect_admin(websocket)
    try:
        while True:
             # Keep connection alive, ignore incoming messages from admin for now
            await websocket.receive_text()
    except WebSocketDisconnect:
        await manager.disconnect_admin_async(websocket)
