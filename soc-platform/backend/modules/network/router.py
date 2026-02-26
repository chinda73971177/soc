import uuid
from fastapi import APIRouter, Depends, HTTPException, Request, BackgroundTasks
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from typing import List
from datetime import datetime
from core.database import get_db
from modules.network.schemas import Asset, ScanRequest, ScanResult, NetworkChange, PortInfo
from modules.network.scanner import run_scan

router = APIRouter()
security = HTTPBearer(auto_error=False)

_active_scans: dict = {}


async def _execute_scan(scan_id: str, target: str, scan_type: str, db_url: str):
    from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
    engine = create_async_engine(db_url)
    SessionLocal = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    try:
        results = await run_scan(target, scan_type)
        async with SessionLocal() as db:
            await db.execute(
                text("UPDATE network_scans SET status='completed', completed_at=NOW(), hosts_found=:hf, results=:res WHERE id=:id"),
                {"hf": len(results.get("hosts", [])), "res": str(results), "id": scan_id}
            )
            for host in results.get("hosts", []):
                existing = await db.execute(text("SELECT id FROM assets WHERE ip_address=:ip"), {"ip": host["ip"]})
                asset_row = existing.fetchone()
                if not asset_row:
                    asset_id = str(uuid.uuid4())
                    await db.execute(
                        text("INSERT INTO assets (id, ip_address, hostname, os_type, is_active) VALUES (:id, :ip, :hn, :os, true)"),
                        {"id": asset_id, "ip": host["ip"], "hn": host.get("hostname"), "os": host.get("os")}
                    )
                else:
                    asset_id = str(asset_row.id)
                    await db.execute(text("UPDATE assets SET last_seen=NOW() WHERE id=:id"), {"id": asset_id})
                for port in host.get("ports", []):
                    await db.execute(
                        text("""INSERT INTO asset_ports (id, asset_id, port, protocol, service, version, state)
                                VALUES (:id, :aid, :port, :proto, :svc, :ver, :state)
                                ON CONFLICT DO NOTHING"""),
                        {"id": str(uuid.uuid4()), "aid": asset_id, "port": port["port"],
                         "proto": port["protocol"], "svc": port.get("service"), "ver": port.get("version"), "state": port["state"]}
                    )
            await db.commit()
    except Exception as e:
        async with SessionLocal() as db:
            await db.execute(text("UPDATE network_scans SET status='failed' WHERE id=:id"), {"id": scan_id})
            await db.commit()
    finally:
        await engine.dispose()


@router.get("/assets", response_model=List[Asset])
async def list_assets(db: AsyncSession = Depends(get_db), credentials: HTTPAuthorizationCredentials = Depends(security)):
    result = await db.execute(text("SELECT id, ip_address, mac_address, hostname, os_type, os_version, asset_type, criticality, first_seen, last_seen, is_active FROM assets ORDER BY last_seen DESC LIMIT 500"))
    rows = result.fetchall()
    return [Asset(id=str(r.id), ip_address=str(r.ip_address), mac_address=r.mac_address, hostname=r.hostname,
                  os_type=r.os_type, os_version=r.os_version, asset_type=r.asset_type,
                  criticality=r.criticality, first_seen=r.first_seen, last_seen=r.last_seen, is_active=r.is_active) for r in rows]


@router.get("/assets/{asset_id}", response_model=Asset)
async def get_asset(asset_id: str, db: AsyncSession = Depends(get_db), credentials: HTTPAuthorizationCredentials = Depends(security)):
    result = await db.execute(text("SELECT * FROM assets WHERE id=:id"), {"id": asset_id})
    row = result.fetchone()
    if not row:
        raise HTTPException(status_code=404, detail="Asset not found")
    ports_result = await db.execute(text("SELECT port, protocol, service, version, state FROM asset_ports WHERE asset_id=:id"), {"id": asset_id})
    ports = [PortInfo(port=p.port, protocol=p.protocol, service=p.service, version=p.version, state=p.state) for p in ports_result.fetchall()]
    return Asset(id=str(row.id), ip_address=str(row.ip_address), hostname=row.hostname,
                 os_type=row.os_type, criticality=row.criticality, first_seen=row.first_seen,
                 last_seen=row.last_seen, is_active=row.is_active, ports=ports)


@router.post("/scan")
async def start_scan(scan_req: ScanRequest, background_tasks: BackgroundTasks, request: Request, db: AsyncSession = Depends(get_db), credentials: HTTPAuthorizationCredentials = Depends(security)):
    from core.config import settings
    scan_id = str(uuid.uuid4())
    await db.execute(
        text("INSERT INTO network_scans (id, scan_type, target, status) VALUES (:id, :type, :target, 'running')"),
        {"id": scan_id, "type": scan_req.scan_type, "target": scan_req.target}
    )
    await db.commit()
    background_tasks.add_task(_execute_scan, scan_id, scan_req.target, scan_req.scan_type, settings.database_url)
    return {"scan_id": scan_id, "status": "started", "target": scan_req.target}


@router.get("/scan/{scan_id}")
async def get_scan(scan_id: str, db: AsyncSession = Depends(get_db), credentials: HTTPAuthorizationCredentials = Depends(security)):
    result = await db.execute(text("SELECT * FROM network_scans WHERE id=:id"), {"id": scan_id})
    row = result.fetchone()
    if not row:
        raise HTTPException(status_code=404, detail="Scan not found")
    return dict(row._mapping)


@router.get("/changes", response_model=List[NetworkChange])
async def get_changes(db: AsyncSession = Depends(get_db), credentials: HTTPAuthorizationCredentials = Depends(security)):
    result = await db.execute(text("SELECT id, asset_id, change_type, previous, current, detected_at, acknowledged FROM network_changes ORDER BY detected_at DESC LIMIT 100"))
    return [NetworkChange(id=str(r.id), asset_id=str(r.asset_id) if r.asset_id else None,
                          change_type=r.change_type, previous=r.previous, current=r.current,
                          detected_at=r.detected_at, acknowledged=r.acknowledged) for r in result.fetchall()]


@router.put("/changes/{change_id}/ack")
async def ack_change(change_id: str, db: AsyncSession = Depends(get_db), credentials: HTTPAuthorizationCredentials = Depends(security)):
    await db.execute(text("UPDATE network_changes SET acknowledged=true WHERE id=:id"), {"id": change_id})
    await db.commit()
    return {"status": "acknowledged"}
