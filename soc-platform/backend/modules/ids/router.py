from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from core.database import get_db
from modules.ids.schemas import IDSAlert, IDSStatus, IDSModeRequest, IDSRule
from modules.ids.suricata import parse_eve_alerts, get_rules, add_rule
from typing import List

router = APIRouter()
security = HTTPBearer(auto_error=False)


@router.get("/status", response_model=IDSStatus)
async def get_ids_status(request: Request, db: AsyncSession = Depends(get_db), credentials: HTTPAuthorizationCredentials = Depends(security)):
    result = await db.execute(text("SELECT mode, interface FROM ids_config ORDER BY updated_at DESC LIMIT 1"))
    row = result.fetchone()
    mode = row.mode if row else "ids"
    interface = row.interface if row else "eth0"
    alerts = parse_eve_alerts(limit=1000)
    categories = {}
    for a in alerts:
        cat = a.get("category", "unknown")
        categories[cat] = categories.get(cat, 0) + 1
    top_cats = sorted([{"category": k, "count": v} for k, v in categories.items()], key=lambda x: -x["count"])[:5]
    return IDSStatus(mode=mode, interface=interface, is_running=True, alerts_today=len(alerts), top_categories=top_cats)


@router.get("/alerts", response_model=List[IDSAlert])
async def get_ids_alerts(limit: int = 100, credentials: HTTPAuthorizationCredentials = Depends(security)):
    alerts = parse_eve_alerts(limit=limit)
    return [IDSAlert(**a) for a in alerts]


@router.put("/mode")
async def set_ids_mode(request_body: IDSModeRequest, db: AsyncSession = Depends(get_db), credentials: HTTPAuthorizationCredentials = Depends(security)):
    if request_body.mode not in ["ids", "ips", "off"]:
        raise HTTPException(status_code=400, detail="Mode must be ids, ips, or off")
    await db.execute(text("UPDATE ids_config SET mode = :mode, updated_at = NOW()"), {"mode": request_body.mode})
    await db.commit()
    return {"mode": request_body.mode, "status": "updated"}


@router.get("/rules", response_model=List[IDSRule])
async def list_rules(credentials: HTTPAuthorizationCredentials = Depends(security)):
    rules = get_rules()
    return [IDSRule(**r) for r in rules]


@router.post("/rules")
async def create_rule(rule: IDSRule, credentials: HTTPAuthorizationCredentials = Depends(security)):
    success = add_rule(rule.content)
    if not success:
        raise HTTPException(status_code=500, detail="Failed to add rule")
    return {"status": "created"}
