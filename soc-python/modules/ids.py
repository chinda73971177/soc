import threading
import json
from datetime import datetime, timezone
from modules.database import get_conn
from modules.config import load_config

_capture_thread = None
_capture_running = False
_captured_count = 0

IDS_RULES = [
    {"id": "R001", "name": "Port Scan Detected",       "proto": None,  "dst_port": None,  "flags": "S",   "severity": "high",     "category": "reconnaissance"},
    {"id": "R002", "name": "SSH Brute Force",           "proto": "TCP", "dst_port": 22,    "flags": None,  "severity": "high",     "category": "brute-force"},
    {"id": "R003", "name": "Telnet Access",             "proto": "TCP", "dst_port": 23,    "flags": None,  "severity": "medium",   "category": "suspicious"},
    {"id": "R004", "name": "HTTP Traffic",              "proto": "TCP", "dst_port": 80,    "flags": None,  "severity": "info",     "category": "network"},
    {"id": "R005", "name": "HTTPS Traffic",             "proto": "TCP", "dst_port": 443,   "flags": None,  "severity": "info",     "category": "network"},
    {"id": "R006", "name": "DNS Query",                 "proto": "UDP", "dst_port": 53,    "flags": None,  "severity": "info",     "category": "network"},
    {"id": "R007", "name": "FTP Access",                "proto": "TCP", "dst_port": 21,    "flags": None,  "severity": "medium",   "category": "suspicious"},
    {"id": "R008", "name": "SMB Traffic",               "proto": "TCP", "dst_port": 445,   "flags": None,  "severity": "medium",   "category": "lateral-movement"},
    {"id": "R009", "name": "RDP Access",                "proto": "TCP", "dst_port": 3389,  "flags": None,  "severity": "medium",   "category": "remote-access"},
    {"id": "R010", "name": "ICMP Flood Detected",       "proto": "ICMP","dst_port": None,  "flags": None,  "severity": "medium",   "category": "dos"},
]


def _check_rules(pkt_info: dict) -> list[dict]:
    triggered = []
    for rule in IDS_RULES:
        if rule["proto"] and rule["proto"] != pkt_info.get("protocol"):
            continue
        if rule["dst_port"] and rule["dst_port"] != pkt_info.get("dst_port"):
            continue
        if rule["flags"] and rule["flags"] not in (pkt_info.get("flags") or ""):
            continue
        triggered.append(rule)
    return triggered


def _save_packet(pkt_info: dict, alert_triggered: bool):
    conn = get_conn()
    conn.execute("""
        INSERT INTO packets (timestamp,src_ip,dst_ip,src_port,dst_port,protocol,
                             length,flags,payload_preview,alert_triggered)
        VALUES (:timestamp,:src_ip,:dst_ip,:src_port,:dst_port,:protocol,
                :length,:flags,:payload_preview,:alert_triggered)
    """, {**pkt_info, "alert_triggered": int(alert_triggered)})
    conn.commit()
    conn.close()


def _save_alert(pkt_info: dict, rule: dict):
    conn = get_conn()
    conn.execute("""
        INSERT INTO alerts (timestamp,title,description,severity,category,
                            src_ip,dst_ip,src_port,dst_port,protocol,rule_id,status)
        VALUES (?,?,?,?,?,?,?,?,?,?,?,?)
    """, (
        pkt_info["timestamp"],
        rule["name"],
        f"{rule['name']} from {pkt_info.get('src_ip')} to {pkt_info.get('dst_ip')}:{pkt_info.get('dst_port')}",
        rule["severity"],
        rule["category"],
        pkt_info.get("src_ip"),
        pkt_info.get("dst_ip"),
        pkt_info.get("src_port"),
        pkt_info.get("dst_port"),
        pkt_info.get("protocol"),
        rule["id"],
        "open",
    ))
    conn.commit()
    conn.close()
    _send_alert_notification(rule, pkt_info)


def _send_alert_notification(rule: dict, pkt_info: dict):
    from modules.notifications import send_alert
    send_alert(
        title=rule["name"],
        severity=rule["severity"],
        description=f"{rule['name']} from {pkt_info.get('src_ip')} → {pkt_info.get('dst_ip')}:{pkt_info.get('dst_port')}",
    )


def _packet_handler(pkt):
    global _captured_count
    try:
        from scapy.layers.inet import IP, TCP, UDP, ICMP
        if not pkt.haslayer(IP):
            return
        ip = pkt[IP]
        proto = "OTHER"
        src_port = dst_port = flags = None
        if pkt.haslayer(TCP):
            proto = "TCP"
            src_port = pkt[TCP].sport
            dst_port = pkt[TCP].dport
            flags = str(pkt[TCP].flags)
        elif pkt.haslayer(UDP):
            proto = "UDP"
            src_port = pkt[UDP].sport
            dst_port = pkt[UDP].dport
        elif pkt.haslayer(ICMP):
            proto = "ICMP"

        payload_preview = ""
        if pkt.haslayer("Raw"):
            payload_preview = bytes(pkt["Raw"].load[:64]).hex()

        pkt_info = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "src_ip": ip.src, "dst_ip": ip.dst,
            "src_port": src_port, "dst_port": dst_port,
            "protocol": proto, "length": len(pkt),
            "flags": flags, "payload_preview": payload_preview,
        }
        rules_triggered = _check_rules(pkt_info)
        _save_packet(pkt_info, bool(rules_triggered))
        for rule in rules_triggered:
            _save_alert(pkt_info, rule)
        _captured_count += 1
    except Exception:
        pass


def start_capture(interface: str = None, packet_count: int = 0):
    global _capture_running, _capture_thread, _captured_count
    if _capture_running:
        return {"status": "already running"}
    try:
        from scapy.all import sniff
        cfg = load_config()
        iface = interface or cfg.get("interface", "eth0")
        _capture_running = True
        _captured_count = 0

        def _run():
            global _capture_running
            sniff(iface=iface, prn=_packet_handler,
                  count=packet_count, store=False,
                  stop_filter=lambda x: not _capture_running)
            _capture_running = False

        _capture_thread = threading.Thread(target=_run, daemon=True)
        _capture_thread.start()
        return {"status": "started", "interface": iface}
    except ImportError:
        return {"error": "scapy not installed"}
    except Exception as e:
        _capture_running = False
        return {"error": str(e)}


def stop_capture():
    global _capture_running
    _capture_running = False
    return {"status": "stopped", "captured": _captured_count}


def capture_status() -> dict:
    return {"running": _capture_running, "captured": _captured_count}


def get_recent_packets(limit: int = 100) -> list[dict]:
    conn = get_conn()
    rows = conn.execute(
        "SELECT * FROM packets ORDER BY created_at DESC LIMIT ?", (limit,)
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_alerts(status: str = None, severity: str = None, page: int = 1, page_size: int = 50) -> dict:
    conn = get_conn()
    conditions = ["1=1"]
    params = []
    if status:
        conditions.append("status=?")
        params.append(status)
    if severity:
        conditions.append("severity=?")
        params.append(severity)
    where = " AND ".join(conditions)
    total = conn.execute(f"SELECT COUNT(*) FROM alerts WHERE {where}", params).fetchone()[0]
    offset = (page - 1) * page_size
    rows = conn.execute(
        f"SELECT * FROM alerts WHERE {where} ORDER BY created_at DESC LIMIT ? OFFSET ?",
        params + [page_size, offset]
    ).fetchall()
    conn.close()
    return {"total": total, "alerts": [dict(r) for r in rows]}


def update_alert_status(alert_id: int, status: str):
    conn = get_conn()
    conn.execute("UPDATE alerts SET status=? WHERE id=?", (status, alert_id))
    conn.commit()
    conn.close()


def get_alert_stats() -> dict:
    conn = get_conn()
    total = conn.execute("SELECT COUNT(*) FROM alerts").fetchone()[0]
    open_c = conn.execute("SELECT COUNT(*) FROM alerts WHERE status='open'").fetchone()[0]
    by_sev = {r[0]: r[1] for r in conn.execute("SELECT severity, COUNT(*) FROM alerts GROUP BY severity")}
    by_cat = {r[0]: r[1] for r in conn.execute("SELECT category, COUNT(*) FROM alerts GROUP BY category")}
    conn.close()
    return {"total": total, "open": open_c, "by_severity": by_sev, "by_category": by_cat}
