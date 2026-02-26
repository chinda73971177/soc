import os
import json

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")
UPLOAD_DIR = os.path.join(BASE_DIR, "uploads")
DB_PATH = os.path.join(DATA_DIR, "soc.db")
CONFIG_PATH = os.path.join(DATA_DIR, "config.json")

DEFAULT_CONFIG = {
    "secret_key": "soc-platform-secret-change-me",
    "network_range": "192.168.1.0/24",
    "scan_type": "standard",
    "scan_interval_minutes": 15,
    "auto_scan_enabled": False,
    "interface": "eth0",
    "home_net": "192.168.0.0/16,10.0.0.0/8,172.16.0.0/12",
    "ids_mode": "ids",
    "alert_on_new_host": True,
    "alert_on_port_change": True,
    "telegram_token": "",
    "telegram_chat_id": "",
    "telegram_min_severity": "high",
    "twilio_sid": "",
    "twilio_token": "",
    "twilio_from": "",
    "twilio_to": "",
    "whatsapp_min_severity": "high",
}


def load_config() -> dict:
    os.makedirs(DATA_DIR, exist_ok=True)
    if os.path.exists(CONFIG_PATH):
        try:
            with open(CONFIG_PATH) as f:
                return {**DEFAULT_CONFIG, **json.load(f)}
        except Exception:
            pass
    return DEFAULT_CONFIG.copy()


def save_config(cfg: dict):
    os.makedirs(DATA_DIR, exist_ok=True)
    with open(CONFIG_PATH, "w") as f:
        json.dump(cfg, f, indent=2)
