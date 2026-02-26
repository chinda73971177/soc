from fastapi import WebSocket
from typing import List, Dict
import json


class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, List[WebSocket]] = {
            "events": [],
            "alerts": [],
        }

    async def connect(self, websocket: WebSocket, channel: str):
        await websocket.accept()
        if channel not in self.active_connections:
            self.active_connections[channel] = []
        self.active_connections[channel].append(websocket)

    def disconnect(self, websocket: WebSocket, channel: str):
        if channel in self.active_connections:
            try:
                self.active_connections[channel].remove(websocket)
            except ValueError:
                pass

    async def broadcast(self, message: dict, channel: str):
        if channel not in self.active_connections:
            return
        dead = []
        for connection in self.active_connections[channel]:
            try:
                await connection.send_text(json.dumps(message))
            except Exception:
                dead.append(connection)
        for conn in dead:
            self.disconnect(conn, channel)

    async def send_personal(self, message: dict, websocket: WebSocket):
        try:
            await websocket.send_text(json.dumps(message))
        except Exception:
            pass


manager = ConnectionManager()
