from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from src.utils.ws_manager import manager

router = APIRouter(prefix="/ws/chat", tags=["WebSocket"])

@router.websocket("/admin")
async def admin_websocket_endpoint(websocket: WebSocket):
    print("WS DEBUG: Admin WebSocket endpoint called!")
    try:
        print("WS DEBUG: About to connect admin...")
        await manager.connect_admin(websocket)
        print("WS DEBUG: Admin connected successfully!")
        try:
            while True:
                # Keep connection alive, ignore incoming messages from admin for now
                data = await websocket.receive_text()
                print(f"WS DEBUG: Admin sent data: {data}")
        except WebSocketDisconnect:
            print("WS DEBUG: Admin disconnecting...")
            await manager.disconnect_admin_async(websocket)
    except Exception as e:
        print(f"WS DEBUG: Admin connection error: {e}")
        try:
            await manager.disconnect_admin_async(websocket)
        except:
            pass

@router.websocket("/{conversation_id}")
async def websocket_endpoint(websocket: WebSocket, conversation_id: str):
    await manager.connect(conversation_id, websocket)
    try:
        while True:
            try:
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
                raise # Re-raise to be caught by outer block
            except Exception as e:
                print(f"WS ERROR: Error handling message: {e}")
                try:
                    await manager.send_personal(websocket, {"event": "error", "message": "Invalid message format"})
                except:
                    pass
    except WebSocketDisconnect:
        await manager.disconnect_async(conversation_id, websocket)
