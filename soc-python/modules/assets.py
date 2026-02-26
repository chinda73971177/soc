import json
from modules.database import get_conn


def get_all_assets(page: int = 1, page_size: int = 50) -> dict:
    conn = get_conn()
    total = conn.execute("SELECT COUNT(*) FROM assets").fetchone()[0]
    offset = (page - 1) * page_size
    rows = conn.execute(
        "SELECT * FROM assets ORDER BY last_seen DESC LIMIT ? OFFSET ?",
        (page_size, offset)
    ).fetchall()
    conn.close()
    assets = []
    for r in rows:
        a = dict(r)
        try:
            a["open_ports"] = json.loads(a["open_ports"] or "[]")
        except Exception:
            a["open_ports"] = []
        assets.append(a)
    return {"total": total, "assets": assets}


def get_asset(ip: str) -> dict | None:
    conn = get_conn()
    row = conn.execute("SELECT * FROM assets WHERE ip_address=?", (ip,)).fetchone()
    conn.close()
    if not row:
        return None
    a = dict(row)
    try:
        a["open_ports"] = json.loads(a["open_ports"] or "[]")
    except Exception:
        a["open_ports"] = []
    return a


def delete_asset(ip: str):
    conn = get_conn()
    conn.execute("DELETE FROM assets WHERE ip_address=?", (ip,))
    conn.commit()
    conn.close()


def get_asset_stats() -> dict:
    conn = get_conn()
    total = conn.execute("SELECT COUNT(*) FROM assets").fetchone()[0]
    up = conn.execute("SELECT COUNT(*) FROM assets WHERE status='up'").fetchone()[0]
    down = conn.execute("SELECT COUNT(*) FROM assets WHERE status='down'").fetchone()[0]
    conn.close()
    return {"total": total, "up": up, "down": down}
