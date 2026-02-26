import threading
import json
from datetime import datetime, timezone
from modules.database import get_conn
from modules.config import load_config

try:
    import nmap
    NMAP_AVAILABLE = True
except ImportError:
    NMAP_AVAILABLE = False

_scan_lock = threading.Lock()
_scan_status = {"running": False, "last_run": None, "last_result": None}


def get_status() -> dict:
    return _scan_status.copy()


def scan_network(target: str = None, scan_type: str = "standard") -> dict:
    cfg = load_config()
    target = target or cfg.get("network_range", "192.168.1.0/24")

    if not NMAP_AVAILABLE:
        return {"error": "python-nmap not installed", "hosts": []}

    profiles = {
        "quick":    "-sn",
        "standard": "-sV -O --top-ports 1000 -T4",
        "full":     "-sV -O -p- -T4",
        "vuln":     "-sV --script vuln -T4",
    }
    args = profiles.get(scan_type, profiles["standard"])

    with _scan_lock:
        _scan_status["running"] = True

    try:
        nm = nmap.PortScanner()
        nm.scan(hosts=target, arguments=args)
        hosts = []
        for host in nm.all_hosts():
            info = nm[host]
            open_ports = []
            for proto in info.all_protocols():
                for port in info[proto].keys():
                    pd = info[proto][port]
                    if pd["state"] == "open":
                        open_ports.append({
                            "port": port, "protocol": proto,
                            "service": pd.get("name", ""),
                            "version": pd.get("version", ""),
                        })
            hostname = ""
            if info.hostname():
                hostname = info.hostname()
            os_info = ""
            if "osmatch" in info and info["osmatch"]:
                os_info = info["osmatch"][0].get("name", "")
            hosts.append({
                "ip": host,
                "hostname": hostname,
                "status": info.state(),
                "os": os_info,
                "open_ports": open_ports,
            })
            _upsert_asset(host, hostname, os_info, open_ports, info.state())
        result = {"target": target, "scan_type": scan_type, "hosts": hosts, "count": len(hosts)}
        _scan_status["last_result"] = result
        _scan_status["last_run"] = datetime.now(timezone.utc).isoformat()
        return result
    except Exception as e:
        return {"error": str(e), "hosts": []}
    finally:
        _scan_status["running"] = False


def scan_async(target: str = None, scan_type: str = "standard"):
    t = threading.Thread(target=scan_network, args=(target, scan_type), daemon=True)
    t.start()


def _upsert_asset(ip, hostname, os_info, open_ports, status):
    conn = get_conn()
    now = datetime.now(timezone.utc).isoformat()
    ports_json = json.dumps(open_ports)
    existing = conn.execute("SELECT id FROM assets WHERE ip_address=?", (ip,)).fetchone()
    if existing:
        conn.execute("""
            UPDATE assets SET hostname=?, os_info=?, open_ports=?, status=?, last_seen=?
            WHERE ip_address=?
        """, (hostname, os_info, ports_json, status, now, ip))
    else:
        conn.execute("""
            INSERT INTO assets (ip_address,hostname,os_info,open_ports,status,first_seen,last_seen)
            VALUES (?,?,?,?,?,?,?)
        """, (ip, hostname, os_info, ports_json, status, now, now))
    conn.commit()
    conn.close()
