from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from datetime import datetime
from typing import Optional
from core.security import verify_password, create_access_token, create_refresh_token, decode_token


async def authenticate_user(db: AsyncSession, username: str, password: str) -> Optional[dict]:
    result = await db.execute(
        text("SELECT id, username, email, password_hash, role, is_active FROM users WHERE username = :username"),
        {"username": username}
    )
    row = result.fetchone()
    if not row:
        return None
    user = dict(row._mapping)
    if not user["is_active"]:
        return None
    if not verify_password(password, user["password_hash"]):
        return None
    await db.execute(
        text("UPDATE users SET last_login = :now WHERE id = :id"),
        {"now": datetime.utcnow(), "id": user["id"]}
    )
    await db.commit()
    return user


async def get_current_user(db: AsyncSession, token: str) -> Optional[dict]:
    payload = decode_token(token)
    if not payload or payload.get("type") != "access":
        return None
    user_id = payload.get("sub")
    result = await db.execute(
        text("SELECT id, username, email, role, is_active, created_at, last_login FROM users WHERE id = :id"),
        {"id": user_id}
    )
    row = result.fetchone()
    if not row:
        return None
    return dict(row._mapping)
