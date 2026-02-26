import uuid
from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from typing import List
from datetime import datetime
from core.database import get_db
from modules.alerts.schemas import SecurityAlert, AlertUpdateRequest, AlertRule
from modules.alerts.telegram import send_telegram_alert
from modules.alerts.whatsapp import send_whatsapp_alert

router = APIRouter()
security = HTTPBearer(auto_error=False)


@router.get("", response_model=List[SecurityAlert])
async def list_alerts(
    severity: str = None,
    status: str = None,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    conditions = []
    params = {"limit": limit}
    if severity:
        conditions.append("severity = :severity")
        params["severity"] = severity
    if status:
        conditions.append("status = :status")
        params["status"] = status
    where = ("WHERE " + " AND ".join(conditions)) if conditions else ""
    result = await db.execute(text(f"SELECT id, alert_type, severity, title, description, source_ip, destination_ip, source_port, destination_port, protocol, service, rule_id, status, created_at, updated_at FROM security_alerts {where} ORDER BY created_at DESC LIMIT :limit"), params)
    rows = result.fetchall()
    return [SecurityAlert(id=str(r.id), alert_type=r.alert_type, severity=r.severity, title=r.title,
                          description=r.description, source_ip=str(r.source_ip) if r.source_ip else None,
                          destination_ip=str(r.destination_ip) if r.destination_ip else None,
                          source_port=r.source_port, destination_port=r.destination_port,
                          protocol=r.protocol, service=r.service, rule_id=r.rule_id,
                          status=r.status, created_at=r.created_at, updated_at=r.updated_at) for r in rows]


@router.get("/{alert_id}", response_model=SecurityAlert)
async def get_alert(alert_id: str, db: AsyncSession = Depends(get_db), credentials: HTTPAuthorizationCredentials = Depends(security)):
    result = await db.execute(text("SELECT * FROM security_alerts WHERE id=:id"), {"id": alert_id})
    row = result.fetchone()
    if not row:
        raise HTTPException(status_code=404, detail="Alert not found")
    d = dict(row._mapping)
    d["id"] = str(d["id"])
    if d.get("source_ip"):
        d["source_ip"] = str(d["source_ip"])
    if d.get("destination_ip"):
        d["destination_ip"] = str(d["destination_ip"])
    return SecurityAlert(**{k: v for k, v in d.items() if k in SecurityAlert.model_fields})


@router.put("/{alert_id}/status")
async def update_alert_status(alert_id: str, body: AlertUpdateRequest, db: AsyncSession = Depends(get_db), credentials: HTTPAuthorizationCredentials = Depends(security)):
    if body.status not in ["open", "investigating", "resolved", "false_positive"]:
        raise HTTPException(status_code=400, detail="Invalid status")
    await db.execute(text("UPDATE security_alerts SET status=:status, updated_at=NOW() WHERE id=:id"), {"status": body.status, "id": alert_id})
    await db.commit()
    return {"status": "updated"}


@router.post("")
async def create_alert(alert: SecurityAlert, db: AsyncSession = Depends(get_db), credentials: HTTPAuthorizationCredentials = Depends(security)):
    alert_id = str(uuid.uuid4())
    await db.execute(
        text("""INSERT INTO security_alerts (id, alert_type, severity, title, description, source_ip, destination_ip, source_port, destination_port, protocol, service, rule_id)
                VALUES (:id, :type, :sev, :title, :desc, :sip, :dip, :sport, :dport, :proto, :svc, :rid)"""),
        {"id": alert_id, "type": alert.alert_type, "sev": alert.severity, "title": alert.title,
         "desc": alert.description, "sip": alert.source_ip, "dip": alert.destination_ip,
         "sport": alert.source_port, "dport": alert.destination_port, "proto": alert.protocol,
         "svc": alert.service, "rid": alert.rule_id}
    )
    await db.commit()
    alert_dict = alert.model_dump()
    alert_dict["id"] = alert_id
    alert_dict["timestamp"] = datetime.utcnow().isoformat()
    if alert.severity in ["critical", "high"]:
        await send_telegram_alert(alert_dict)
        await send_whatsapp_alert(alert_dict)
    return {"id": alert_id, "status": "created"}


@router.get("/rules/list", response_model=List[AlertRule])
async def list_rules(db: AsyncSession = Depends(get_db), credentials: HTTPAuthorizationCredentials = Depends(security)):
    result = await db.execute(text("SELECT id, name, description, conditions, severity, is_active, notify_telegram, notify_whatsapp FROM alert_rules ORDER BY created_at DESC"))
    return [AlertRule(id=str(r.id), name=r.name, description=r.description, conditions=r.conditions,
                      severity=r.severity, is_active=r.is_active, notify_telegram=r.notify_telegram,
                      notify_whatsapp=r.notify_whatsapp) for r in result.fetchall()]


@router.post("/rules")
async def create_rule(rule: AlertRule, db: AsyncSession = Depends(get_db), credentials: HTTPAuthorizationCredentials = Depends(security)):
    rule_id = str(uuid.uuid4())
    await db.execute(
        text("INSERT INTO alert_rules (id, name, description, conditions, severity, is_active, notify_telegram, notify_whatsapp) VALUES (:id, :name, :desc, :cond, :sev, :active, :tg, :wa)"),
        {"id": rule_id, "name": rule.name, "desc": rule.description, "cond": str(rule.conditions),
         "sev": rule.severity, "active": rule.is_active, "tg": rule.notify_telegram, "wa": rule.notify_whatsapp}
    )
    await db.commit()
    return {"id": rule_id, "status": "created"}
