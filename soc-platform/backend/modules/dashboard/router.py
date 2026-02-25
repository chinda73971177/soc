from fastapi import APIRouter, Depends, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from datetime import datetime, timedelta
from core.database import get_db
from modules.ids.suricata import parse_eve_alerts

router = APIRouter()
security = HTTPBearer(auto_error=False)


@router.get("/summary")
async def get_summary(request: Request, db: AsyncSession = Depends(get_db), credentials: HTTPAuthorizationCredentials = Depends(security)):
    now = datetime.utcnow()
    day_ago = now - timedelta(hours=24)

    total_alerts = await db.execute(text("SELECT COUNT(*) FROM security_alerts WHERE created_at >= :da"), {"da": day_ago})
    critical_alerts = await db.execute(text("SELECT COUNT(*) FROM security_alerts WHERE severity='critical' AND created_at >= :da"), {"da": day_ago})
    open_alerts = await db.execute(text("SELECT COUNT(*) FROM security_alerts WHERE status='open'"))
    total_assets = await db.execute(text("SELECT COUNT(*) FROM assets WHERE is_active=true"))
    ids_alerts = parse_eve_alerts(limit=1000)

    es = request.app.state.es
    try:
        log_count = await es.count(index="soc-logs-*", body={"query": {"range": {"@timestamp": {"gte": day_ago.isoformat()}}}})
        logs_today = log_count.get("count", 0)
    except Exception:
        logs_today = 0

    return {
        "alerts_today": total_alerts.scalar(),
        "critical_alerts": critical_alerts.scalar(),
        "open_alerts": open_alerts.scalar(),
        "total_assets": total_assets.scalar(),
        "ids_alerts_today": len(ids_alerts),
        "logs_today": logs_today,
        "timestamp": now.isoformat()
    }


@router.get("/timeline")
async def get_timeline(db: AsyncSession = Depends(get_db), credentials: HTTPAuthorizationCredentials = Depends(security)):
    result = await db.execute(text("""
        SELECT date_trunc('hour', created_at) as hour, COUNT(*) as count
        FROM security_alerts
        WHERE created_at >= NOW() - INTERVAL '24 hours'
        GROUP BY hour
        ORDER BY hour
    """))
    return [{"time": str(r.hour), "count": r.count} for r in result.fetchall()]


@router.get("/top-threats")
async def get_top_threats(db: AsyncSession = Depends(get_db), credentials: HTTPAuthorizationCredentials = Depends(security)):
    result = await db.execute(text("""
        SELECT alert_type, COUNT(*) as count, MAX(severity) as max_severity
        FROM security_alerts
        WHERE created_at >= NOW() - INTERVAL '24 hours'
        GROUP BY alert_type
        ORDER BY count DESC
        LIMIT 10
    """))
    return [{"type": r.alert_type, "count": r.count, "severity": r.max_severity} for r in result.fetchall()]


@router.get("/top-sources")
async def get_top_sources(db: AsyncSession = Depends(get_db), credentials: HTTPAuthorizationCredentials = Depends(security)):
    result = await db.execute(text("""
        SELECT source_ip::text as ip, COUNT(*) as count
        FROM security_alerts
        WHERE source_ip IS NOT NULL AND created_at >= NOW() - INTERVAL '24 hours'
        GROUP BY source_ip
        ORDER BY count DESC
        LIMIT 10
    """))
    return [{"ip": r.ip, "count": r.count} for r in result.fetchall()]


@router.get("/top-services")
async def get_top_services(db: AsyncSession = Depends(get_db), credentials: HTTPAuthorizationCredentials = Depends(security)):
    result = await db.execute(text("""
        SELECT service, COUNT(*) as count
        FROM security_alerts
        WHERE service IS NOT NULL AND created_at >= NOW() - INTERVAL '24 hours'
        GROUP BY service
        ORDER BY count DESC
        LIMIT 10
    """))
    return [{"service": r.service, "count": r.count} for r in result.fetchall()]
