import io
import csv
import json
import re
import uuid
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, Request, UploadFile, File, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

router = APIRouter()
security = HTTPBearer(auto_error=False)

ALLOWED_EXTENSIONS = {".log", ".txt", ".json", ".csv"}
MAX_FILE_SIZE = 50 * 1024 * 1024  # 50 MB

SYSLOG_RE = re.compile(
    r"(?P<month>\w{3})\s+(?P<day>\d+)\s+(?P<time>\d{2}:\d{2}:\d{2})\s+"
    r"(?P<host>\S+)\s+(?P<program>[^:\[]+)(?:\[\d+\])?:\s*(?P<message>.+)"
)

SEVERITY_KEYWORDS = {
    "critical": ["critical", "emerg", "alert"],
    "high":     ["error", "err", "crit"],
    "medium":   ["warn", "warning"],
    "low":      ["notice"],
    "info":     ["info", "debug"],
}


def _detect_severity(text: str) -> str:
    lower = text.lower()
    for level, keywords in SEVERITY_KEYWORDS.items():
        if any(k in lower for k in keywords):
            return level
    return "info"


def _parse_syslog_line(line: str, filename: str) -> dict | None:
    line = line.strip()
    if not line:
        return None
    m = SYSLOG_RE.match(line)
    if m:
        return {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "host_name": m.group("host"),
            "program":   m.group("program").strip(),
            "message":   m.group("message").strip(),
            "log_source": filename,
            "log_type":  "system",
            "severity":  _detect_severity(m.group("message")),
            "raw":       {"original": line},
        }
    return {
        "timestamp":  datetime.now(timezone.utc).isoformat(),
        "message":    line,
        "log_source": filename,
        "log_type":   "system",
        "severity":   _detect_severity(line),
        "raw":        {"original": line},
    }


def _parse_txt(content: str, filename: str) -> list[dict]:
    return [r for line in content.splitlines() if (r := _parse_syslog_line(line, filename))]


def _parse_json(content: str, filename: str) -> list[dict]:
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
        record = {
            "timestamp":  item.get("timestamp") or item.get("time") or item.get("@timestamp") or datetime.now(timezone.utc).isoformat(),
            "message":    item.get("message") or item.get("msg") or json.dumps(item),
            "host_name":  item.get("host") or item.get("hostname") or item.get("host_name"),
            "program":    item.get("program") or item.get("process") or item.get("app"),
            "log_source": filename,
            "log_type":   item.get("log_type") or item.get("type") or "system",
            "severity":   item.get("severity") or item.get("level") or _detect_severity(str(item)),
            "src_ip":     item.get("src_ip") or item.get("source_ip") or item.get("src"),
            "dst_ip":     item.get("dst_ip") or item.get("dest_ip") or item.get("dst"),
            "src_port":   item.get("src_port") or item.get("sport"),
            "dst_port":   item.get("dst_port") or item.get("dport"),
            "protocol":   item.get("protocol") or item.get("proto"),
            "service":    item.get("service") or item.get("app_proto"),
            "raw":        item,
        }
        records.append(record)
    return records


def _parse_csv(content: str, filename: str) -> list[dict]:
    records = []
    reader = csv.DictReader(io.StringIO(content))
    for row in reader:
        row_lower = {k.lower().strip(): v for k, v in row.items()}
        record = {
            "timestamp":  row_lower.get("timestamp") or row_lower.get("time") or row_lower.get("date") or datetime.now(timezone.utc).isoformat(),
            "message":    row_lower.get("message") or row_lower.get("msg") or row_lower.get("description") or str(dict(row)),
            "host_name":  row_lower.get("host") or row_lower.get("hostname"),
            "program":    row_lower.get("program") or row_lower.get("process"),
            "log_source": filename,
            "log_type":   row_lower.get("type") or row_lower.get("log_type") or "system",
            "severity":   row_lower.get("severity") or row_lower.get("level") or _detect_severity(str(row)),
            "src_ip":     row_lower.get("src_ip") or row_lower.get("source_ip"),
            "dst_ip":     row_lower.get("dst_ip") or row_lower.get("dest_ip"),
            "raw":        dict(row),
        }
        try:
            sp = row_lower.get("src_port") or row_lower.get("sport")
            record["src_port"] = int(sp) if sp else None
        except (ValueError, TypeError):
            record["src_port"] = None
        try:
            dp = row_lower.get("dst_port") or row_lower.get("dport")
            record["dst_port"] = int(dp) if dp else None
        except (ValueError, TypeError):
            record["dst_port"] = None
        records.append(record)
    return records


@router.post("/upload")
async def upload_log_file(
    request: Request,
    file: UploadFile = File(...),
    credentials: HTTPAuthorizationCredentials = Depends(security),
):
    import os
    ext = os.path.splitext(file.filename or "")[1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(status_code=400, detail=f"Unsupported file type '{ext}'. Allowed: {', '.join(ALLOWED_EXTENSIONS)}")

    raw_bytes = await file.read()
    if len(raw_bytes) > MAX_FILE_SIZE:
        raise HTTPException(status_code=413, detail="File exceeds 50 MB limit")

    try:
        content = raw_bytes.decode("utf-8", errors="replace")
    except Exception:
        raise HTTPException(status_code=400, detail="Cannot decode file as UTF-8")

    filename = file.filename or "uploaded"

    if ext == ".json":
        records = _parse_json(content, filename)
    elif ext == ".csv":
        records = _parse_csv(content, filename)
    else:
        records = _parse_txt(content, filename)

    if not records:
        raise HTTPException(status_code=422, detail="No parseable log entries found in file")

    es = request.app.state.es
    index = f"soc-logs-{datetime.now(timezone.utc).strftime('%Y.%m.%d')}"

    bulk_body = []
    for record in records:
        doc_id = str(uuid.uuid4())
        bulk_body.append({"index": {"_index": index, "_id": doc_id}})
        bulk_body.append(record)

    response = await es.bulk(operations=bulk_body, refresh=True)

    errors = [item for item in response.get("items", []) if "error" in item.get("index", {})]
    indexed = len(records) - len(errors)

    return {
        "filename":  filename,
        "total":     len(records),
        "indexed":   indexed,
        "errors":    len(errors),
        "index":     index,
    }
