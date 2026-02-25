import asyncio
import json
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from websocket.manager import manager
from modules.ids.suricata import parse_eve_alerts
from datetime import datetime

router = APIRouter()


@router.websocket("/ws/events")
async def websocket_events(websocket: WebSocket):
    await manager.connect(websocket, "events")
    try:
        while True:
            await asyncio.sleep(5)
            event = {
                "type": "heartbeat",
                "timestamp": datetime.utcnow().isoformat(),
                "message": "SOC Platform alive"
            }
            await manager.send_personal(event, websocket)
    except WebSocketDisconnect:
        manager.disconnect(websocket, "events")


@router.websocket("/ws/alerts")
async def websocket_alerts(websocket: WebSocket):
    await manager.connect(websocket, "alerts")
    last_count = 0
    try:
        while True:
            await asyncio.sleep(10)
            alerts = parse_eve_alerts(limit=5)
            if len(alerts) != last_count:
                last_count = len(alerts)
                for alert in alerts[-3:]:
                    await manager.send_personal({"type": "ids_alert", "data": alert}, websocket)
    except WebSocketDisconnect:
        manager.disconnect(websocket, "alerts")
