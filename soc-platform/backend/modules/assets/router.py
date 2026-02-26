from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from core.database import get_db

router = APIRouter()
security = HTTPBearer(auto_error=False)


@router.get("/summary")
async def get_summary(db: AsyncSession = Depends(get_db), credentials: HTTPAuthorizationCredentials = Depends(security)):
    total = await db.execute(text("SELECT COUNT(*) FROM assets"))
    active = await db.execute(text("SELECT COUNT(*) FROM assets WHERE is_active=true"))
    critical = await db.execute(text("SELECT COUNT(*) FROM assets WHERE criticality='critical'"))
    by_type = await db.execute(text("SELECT asset_type, COUNT(*) as count FROM assets GROUP BY asset_type"))
    return {
        "total": total.scalar(),
        "active": active.scalar(),
        "critical": critical.scalar(),
        "by_type": {r.asset_type or "unknown": r.count for r in by_type.fetchall()}
    }
