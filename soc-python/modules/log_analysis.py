import io
import csv
import json
import re
import os
from datetime import datetime, timezone
from modules.database import get_conn

SYSLOG_RE = re.compile(
    r"(?P<month>\w{3})\s+(?P<day>\d+)\s+(?P<time>\d{2}:\d{2}:\d{2})\s+"
    r"(?P<host>\S+)\s+(?P<program>[^:\[]+)(?:\[\d+\])?:\s*(?P<message>.+)"
)

SEVERITY_KEYWORDS = {
    "critical": ["critical", "emerg", "panic"],
    "high":     ["error", "err", "crit", "alert"],
    "medium":   ["warn", "warning"],
    "low":      ["notice"],
    "info":     ["info", "debug"],
}


def detect_severity(text: str) -> str:
    lower = text.lower()
    for level, keywords in SEVERITY_KEYWORDS.items():
        if any(k in lower for k in keywords):
            return level
    return "info"


def parse_syslog_line(line: str, filename: str) -> dict | None:
    line = line.strip()
    if not line:
        return None
    m = SYSLOG_RE.match(line)
    ts = datetime.now(timezone.utc).isoformat()
    if m:
        return {
            "timestamp": ts, "host_name": m.group("host"),
            "program": m.group("program").strip(),
            "message": m.group("message").strip(),
            "log_source": filename, "log_type": "system",
            "severity": detect_severity(m.group("message")),
            "raw": json.dumps({"original": line}),
        }
    return {
        "timestamp": ts, "message": line,
        "log_source": filename, "log_type": "system",
        "severity": detect_severity(line),
        "raw": json.dumps({"original": line}),
    }


def parse_txt(content: str, filename: str) -> list[dict]:
    return [r for line in content.splitlines() if (r := parse_syslog_line(line, filename))]


def parse_json(content: str, filename: str) -> list[dict]:
    records = []
    try:
        data = json.loads(content)
        items = data if isinstance(data, list) else [data]
    except json.JSONDecodeError:
        items = []
        for line in content.splitlines():
            line = line.strip()
            if not line:
                continue
            try:
                items.append(json.loads(line))
            except json.JSONDecodeError:
                pass
    for item in items:
        if not isinstance(item, dict):
            continue
        records.append({
            "timestamp":  item.get("timestamp") or item.get("time") or item.get("@timestamp") or datetime.now(timezone.utc).isoformat(),
            "message":    item.get("message") or item.get("msg") or json.dumps(item),
            "host_name":  item.get("host") or item.get("hostname"),
            "program":    item.get("program") or item.get("process") or item.get("app"),
            "log_source": filename,
            "log_type":   item.get("log_type") or item.get("type") or "system",
            "severity":   item.get("severity") or item.get("level") or detect_severity(str(item)),
            "src_ip":     item.get("src_ip") or item.get("source_ip") or item.get("src"),
            "dst_ip":     item.get("dst_ip") or item.get("dest_ip") or item.get("dst"),
            "src_port":   item.get("src_port") or item.get("sport"),
            "dst_port":   item.get("dst_port") or item.get("dport"),
            "protocol":   item.get("protocol") or item.get("proto"),
            "service":    item.get("service") or item.get("app_proto"),
            "raw":        json.dumps(item),
        })
    return records


def parse_csv(content: str, filename: str) -> list[dict]:
    records = []
    reader = csv.DictReader(io.StringIO(content))
    for row in reader:
        r = {k.lower().strip(): v for k, v in row.items()}
        record = {
            "timestamp":  r.get("timestamp") or r.get("time") or r.get("date") or datetime.now(timezone.utc).isoformat(),
            "message":    r.get("message") or r.get("msg") or r.get("description") or str(dict(row)),
            "host_name":  r.get("host") or r.get("hostname"),
            "program":    r.get("program") or r.get("process"),
            "log_source": filename,
            "log_type":   r.get("type") or r.get("log_type") or "system",
            "severity":   r.get("severity") or r.get("level") or detect_severity(str(row)),
            "src_ip":     r.get("src_ip") or r.get("source_ip"),
            "dst_ip":     r.get("dst_ip") or r.get("dest_ip"),
            "src_port":   _int(r.get("src_port") or r.get("sport")),
            "dst_port":   _int(r.get("dst_port") or r.get("dport")),
            "protocol":   r.get("protocol") or r.get("proto"),
            "service":    r.get("service"),
            "raw":        json.dumps(dict(row)),
        }
        records.append(record)
    return records


def _int(v):
    try:
        return int(v) if v else None
    except (ValueError, TypeError):
        return None


def ingest_records(records: list[dict]) -> tuple[int, int]:
    conn = get_conn()
    ok = 0
    err = 0
    for r in records:
        try:
            conn.execute("""
                INSERT INTO logs (timestamp,message,host_name,log_source,log_type,severity,
                                  program,src_ip,dst_ip,src_port,dst_port,protocol,service,raw)
                VALUES (:timestamp,:message,:host_name,:log_source,:log_type,:severity,
                        :program,:src_ip,:dst_ip,:src_port,:dst_port,:protocol,:service,:raw)
            """, r)
            ok += 1
        except Exception:
            err += 1
    conn.commit()
    conn.close()
    return ok, err


def process_upload(file_path: str, filename: str) -> dict:
    with open(file_path, "r", encoding="utf-8", errors="replace") as f:
        content = f.read()
    ext = os.path.splitext(filename)[1].lower()
    if ext == ".json":
        records = parse_json(content, filename)
    elif ext == ".csv":
        records = parse_csv(content, filename)
    else:
        records = parse_txt(content, filename)
    if not records:
        return {"total": 0, "indexed": 0, "errors": 0}
    indexed, errors = ingest_records(records)
    return {"total": len(records), "indexed": indexed, "errors": errors}


def search_logs(query="", severity="", log_type="", src_ip="", dst_ip="",
                protocol="", service="", page=1, page_size=50) -> dict:
    conn = get_conn()
    conditions = ["1=1"]
    params = []
    if query:
        conditions.append("(message LIKE ? OR host_name LIKE ? OR program LIKE ?)")
        params += [f"%{query}%", f"%{query}%", f"%{query}%"]
    if severity:
        conditions.append("severity=?")
        params.append(severity)
    if log_type:
        conditions.append("log_type=?")
        params.append(log_type)
    if src_ip:
        conditions.append("src_ip LIKE ?")
        params.append(f"%{src_ip}%")
    if dst_ip:
        conditions.append("dst_ip LIKE ?")
        params.append(f"%{dst_ip}%")
    if protocol:
        conditions.append("protocol=?")
        params.append(protocol)
    if service:
        conditions.append("service LIKE ?")
        params.append(f"%{service}%")
    where = " AND ".join(conditions)
    total = conn.execute(f"SELECT COUNT(*) FROM logs WHERE {where}", params).fetchone()[0]
    offset = (page - 1) * page_size
    rows = conn.execute(
        f"SELECT * FROM logs WHERE {where} ORDER BY created_at DESC LIMIT ? OFFSET ?",
        params + [page_size, offset]
    ).fetchall()
    conn.close()
    return {"total": total, "logs": [dict(r) for r in rows]}


def get_log_stats() -> dict:
    conn = get_conn()
    total = conn.execute("SELECT COUNT(*) FROM logs WHERE date(created_at)=date('now')").fetchone()[0]
    by_sev = {r[0]: r[1] for r in conn.execute("SELECT severity, COUNT(*) FROM logs GROUP BY severity")}
    by_type = {r[0]: r[1] for r in conn.execute("SELECT log_type, COUNT(*) FROM logs GROUP BY log_type")}
    by_src = {r[0]: r[1] for r in conn.execute("SELECT log_source, COUNT(*) FROM logs GROUP BY log_source LIMIT 10")}
    conn.close()
    return {"total_today": total, "by_severity": by_sev, "by_type": by_type, "by_source": by_src}
