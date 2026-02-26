import nmap
import asyncio
from typing import Dict, List
from datetime import datetime


SCAN_PROFILES = {
    "quick": "-sn",
    "standard": "-sS -sV -O --top-ports 1000",
    "full": "-sS -sV -O -p-",
    "vuln": "-sV --script vuln",
}


async def run_scan(target: str, scan_type: str = "standard") -> Dict:
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, _do_scan, target, scan_type)


def _do_scan(target: str, scan_type: str) -> Dict:
    nm = nmap.PortScanner()
    args = SCAN_PROFILES.get(scan_type, SCAN_PROFILES["standard"])
    try:
        nm.scan(hosts=target, arguments=args)
    except Exception as e:
        return {"error": str(e), "hosts": []}

    hosts = []
    for host in nm.all_hosts():
        host_data = {
            "ip": host,
            "hostname": nm[host].hostname(),
            "state": nm[host].state(),
            "os": _extract_os(nm, host),
            "ports": [],
        }
        for proto in nm[host].all_protocols():
            for port in sorted(nm[host][proto].keys()):
                port_info = nm[host][proto][port]
                host_data["ports"].append({
                    "port": port,
                    "protocol": proto,
                    "state": port_info.get("state", "unknown"),
                    "service": port_info.get("name", ""),
                    "version": f"{port_info.get('product', '')} {port_info.get('version', '')}".strip(),
                })
        hosts.append(host_data)

    return {"hosts": hosts, "scan_time": datetime.utcnow().isoformat()}


def _extract_os(nm, host) -> str:
    try:
        osmatch = nm[host].get("osmatch", [])
        if osmatch:
            return osmatch[0].get("name", "Unknown")
    except Exception:
        pass
    return "Unknown"
