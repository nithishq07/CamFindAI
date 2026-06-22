from fastapi import APIRouter, WebSocket, WebSocketDisconnect
import json
import asyncio
import random

router = APIRouter()

@router.websocket("")
async def websocket_status(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            status_data = {
                "Camera Health": "Online",
                "Database Status": "Online",
                "Kafka Status": "Online",
                "Inference Engine Status": "Online",
                "GPU Usage": random.randint(20, 80),
                "Memory Usage": random.randint(40, 90)
            }
            await websocket.send_text(json.dumps(status_data))
            await asyncio.sleep(5)
    except WebSocketDisconnect:
        pass
