import json
import os
from pathlib import Path
from datetime import datetime, timedelta
from typing import List


SURICATA_EVE_LOG = os.getenv("SURICATA_EVE_LOG", "/var/log/suricata/eve.json")
SURICATA_RULES_PATH = os.getenv("SURICATA_RULES_PATH", "/app/suricata/rules/local.rules")


def parse_eve_alerts(limit: int = 100, hours: int = 24) -> List[dict]:
    alerts = []
    cutoff = datetime.utcnow() - timedelta(hours=hours)

    if not Path(SURICATA_EVE_LOG).exists():
        return _generate_demo_alerts(limit)

    try:
        with open(SURICATA_EVE_LOG, "r") as f:
            for line in f:
                try:
                    event = json.loads(line.strip())
                    if event.get("event_type") != "alert":
                        continue
                    ts = datetime.fromisoformat(event.get("timestamp", "").replace("Z", "+00:00").replace("+0000", "+00:00"))
                    if ts.replace(tzinfo=None) < cutoff:
                        continue
                    alert = event.get("alert", {})
                    alerts.append({
                        "id": event.get("flow_id", str(len(alerts))),
                        "timestamp": event.get("timestamp"),
                        "src_ip": event.get("src_ip"),
                        "src_port": event.get("src_port"),
                        "dst_ip": event.get("dest_ip"),
                        "dst_port": event.get("dest_port"),
                        "protocol": event.get("proto"),
                        "message": alert.get("signature"),
                        "rule_id": str(alert.get("signature_id")),
                        "category": alert.get("category"),
                        "severity": _map_severity(alert.get("severity", 3)),
                        "action": alert.get("action", "alert"),
                        "alert_type": _classify_alert(alert.get("signature", "")),
                    })
                except Exception:
                    continue
    except Exception:
        return _generate_demo_alerts(limit)

    return alerts[-limit:]


def _map_severity(suricata_sev: int) -> str:
    mapping = {1: "critical", 2: "high", 3: "medium", 4: "low"}
    return mapping.get(suricata_sev, "info")


def _classify_alert(signature: str) -> str:
    sig_lower = signature.lower()
    if "scan" in sig_lower:
        return "port_scan"
    if "brute" in sig_lower or "brute force" in sig_lower:
        return "brute_force"
    if "flood" in sig_lower or "dos" in sig_lower:
        return "dos"
    if "sql" in sig_lower or "injection" in sig_lower:
        return "web_attack"
    if "malware" in sig_lower or "trojan" in sig_lower:
        return "malware"
    return "anomaly"


def _generate_demo_alerts(limit: int) -> List[dict]:
    import random
    demo = []
    types = ["port_scan", "brute_force", "dos", "web_attack", "anomaly"]
    severities = ["critical", "high", "medium", "low"]
    messages = [
        "SOC PORT SCAN DETECTED",
        "SOC SSH BRUTE FORCE",
        "SOC SYN FLOOD",
        "SOC SQL INJECTION ATTEMPT",
        "SOC HTTP LOGIN BRUTE FORCE",
    ]
    for i in range(min(limit, 20)):
        demo.append({
            "id": f"demo-{i}",
            "timestamp": (datetime.utcnow() - timedelta(minutes=random.randint(1, 1440))).isoformat(),
            "src_ip": f"192.168.{random.randint(1,254)}.{random.randint(1,254)}",
            "src_port": random.randint(1024, 65535),
            "dst_ip": f"10.0.0.{random.randint(1,50)}",
            "dst_port": random.choice([22, 80, 443, 3389, 21, 3306]),
            "protocol": random.choice(["TCP", "UDP", "ICMP"]),
            "message": random.choice(messages),
            "rule_id": f"900000{i}",
            "category": random.choice(["network-scan", "attempted-admin", "dos-attack", "web-application-attack"]),
            "severity": random.choice(severities),
            "action": random.choice(["alert", "drop"]),
            "alert_type": random.choice(types),
        })
    return demo


def get_rules() -> List[dict]:
    rules = []
    if not Path(SURICATA_RULES_PATH).exists():
        return rules
    try:
        with open(SURICATA_RULES_PATH, "r") as f:
            for i, line in enumerate(f):
                line = line.strip()
                if line and not line.startswith("#"):
                    rules.append({"id": str(i), "content": line, "is_active": True, "name": f"Rule {i+1}", "severity": "medium"})
    except Exception:
        pass
    return rules


def add_rule(rule_content: str) -> bool:
    try:
        with open(SURICATA_RULES_PATH, "a") as f:
            f.write(f"\n{rule_content}\n")
        return True
    except Exception:
        return False
