from typing import Dict, Set, Any
from fastapi import WebSocket, WebSocketDisconnect

class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, Set[WebSocket]] = {}

    async def connect(self, room: str, websocket: WebSocket):
        await websocket.accept()
        conns = self.active_connections.setdefault(room, set())
        conns.add(websocket)

    def disconnect(self, room: str, websocket: WebSocket):
        conns = self.active_connections.get(room)
        if conns and websocket in conns:
            conns.remove(websocket)
            if not conns:
                del self.active_connections[room]

    async def send_personal(self, websocket: WebSocket, message: Any):
        await websocket.send_json(message)

    async def broadcast_room(self, room: str, message: Any):
        conns = self.active_connections.get(room, set())
        for conn in list(conns):
            try:
                await conn.send_json(message)
            except Exception:
                pass

manager = ConnectionManager()

async def websocket_endpoint(websocket: WebSocket, room: str):
    await manager.connect(room, websocket)
    try:
        while True:
            data = await websocket.receive_json()
            action = data.get("action")
            payload = data.get("payload")
            
            if action == "send_message":
                await manager.broadcast_room(room, {"event": "receive_message", "data": payload})
            elif action == "typing":
                await manager.broadcast_room(room, {"event": "typing", "data": payload})
            elif action == "message_read":
                await manager.broadcast_room(room, {"event": "messages_read", "data": payload})
            elif action == "edit_message":
                await manager.broadcast_room(room, {"event": "edit_message", "data": payload})
            elif action == "delete_message":
                await manager.broadcast_room(room, {"event": "delete_message", "data": payload})
            else:
                await manager.send_personal(websocket, {"event": "unknown", "action": action})
    except WebSocketDisconnect:
        manager.disconnect(room, websocket)
