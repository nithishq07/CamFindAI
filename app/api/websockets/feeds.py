from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from typing import Dict, List

router = APIRouter()

class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[int, List[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, camera_id: int):
        await websocket.accept()
        if camera_id not in self.active_connections:
            self.active_connections[camera_id] = []
        self.active_connections[camera_id].append(websocket)

    def disconnect(self, websocket: WebSocket, camera_id: int):
        if camera_id in self.active_connections:
            self.active_connections[camera_id].remove(websocket)

    async def broadcast(self, camera_id: int, message: str):
        if camera_id in self.active_connections:
            for connection in self.active_connections[camera_id]:
                try:
                    await connection.send_text(message)
                except Exception:
                    self.disconnect(connection, camera_id)

manager = ConnectionManager()

@router.websocket("/{camera_id}")
async def websocket_feed(websocket: WebSocket, camera_id: int):
    # This is for UI clients to receive the feed
    await manager.connect(websocket, camera_id)
    try:
        while True:
            # Keep connection alive
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket, camera_id)

@router.websocket("/{camera_id}/publish")
async def websocket_publish(websocket: WebSocket, camera_id: int):
    # This is for the camera worker to push the feed
    await websocket.accept()
    try:
        while True:
            # Expecting base64 encoded frame
            frame_data = await websocket.receive_text()
            await manager.broadcast(camera_id, frame_data)
    except WebSocketDisconnect:
        pass
