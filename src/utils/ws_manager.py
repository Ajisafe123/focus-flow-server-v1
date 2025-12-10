from typing import Dict, Set, Any
from fastapi import WebSocket, WebSocketDisconnect

class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, Set[WebSocket]] = {}
        self.admin_connections: Set[WebSocket] = set()

    async def connect(self, room: str, websocket: WebSocket):
        await websocket.accept()
        conns = self.active_connections.setdefault(room, set())
        conns.add(websocket)
        # Notify admins that user is online (room usually equals conversation_id which maps to user)
        # We might need to map conversation_id -> user_id or just use conversation_id as proxy for user presence
        await self.broadcast_to_admins({"event": "user_status", "data": {"conversation_id": room, "status": "online"}})

    async def connect_admin(self, websocket: WebSocket):
        await websocket.accept()
        self.admin_connections.add(websocket)
        # Notify all active rooms (users) that admin is online
        # This might be heavy if many users, but for now it's fine
        for room in self.active_connections:
            await self.broadcast_room(room, {"event": "admin_status", "data": {"status": "online"}})

    def disconnect(self, room: str, websocket: WebSocket):
        conns = self.active_connections.get(room)
        if conns and websocket in conns:
            conns.remove(websocket)
            if not conns:
                del self.active_connections[room]
                # Notify admins user went offline
                # We can't await here directly if this is called from sync context? 
                # disconnect is usually called from async endpoint catch block, so we can't await?
                # Wait, disconnect is defined as sync def in original.
                # If I want to broadcast, I need async.
                # I will change disconnect to async or just fire-and-forget if possible?
                # FastAPI websocket endpoints are async, so I can await disconnect if I change it to async.
                pass 

    async def disconnect_async(self, room: str, websocket: WebSocket):
         conns = self.active_connections.get(room)
         if conns and websocket in conns:
            conns.remove(websocket)
            if not conns:
                del self.active_connections[room]
                await self.broadcast_to_admins({"event": "user_status", "data": {"conversation_id": room, "status": "offline"}})

    def disconnect_admin(self, websocket: WebSocket):
        if websocket in self.admin_connections:
            self.admin_connections.remove(websocket)

    async def disconnect_admin_async(self, websocket: WebSocket):
        if websocket in self.admin_connections:
            self.admin_connections.remove(websocket)
            # Notify users admin offline
            for room in self.active_connections:
                 await self.broadcast_room(room, {"event": "admin_status", "data": {"status": "offline"}})

    async def send_personal(self, websocket: WebSocket, message: Any):
        await websocket.send_json(message)

    async def broadcast_to_admins(self, message: Any):
        for conn in list(self.admin_connections):
            try:
                await conn.send_json(message)
            except Exception:
                pass

    async def broadcast_room(self, room: str, message: Any):
        # Send to room participants
        conns = self.active_connections.get(room, set())
        for conn in list(conns):
            try:
                await conn.send_json(message)
            except Exception:
                pass
        
        # Send to all admins
        await self.broadcast_to_admins(message)

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
