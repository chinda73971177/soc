from fastapi import APIRouter, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from pydantic import BaseModel
from typing import Optional
from core.database import get_db
import json
import os

router = APIRouter()
security = HTTPBearer(auto_error=False)

CONFIG_FILE = "/app/network_config.json"

DEFAULT_CONFIG = {
    "network_range": "192.168.1.0/24",
    "scan_type": "standard",
    "scan_interval_minutes": 15,
    "auto_scan_enabled": True,
    "interface": "eth0",
    "home_net": "192.168.0.0/16,10.0.0.0/8,172.16.0.0/12",
    "ids_mode": "ids",
    "alert_on_new_host": True,
    "alert_on_port_change": True,
}


class NetworkConfig(BaseModel):
    network_range: str
    scan_type: str
    scan_interval_minutes: int
    auto_scan_enabled: bool
    interface: str
    home_net: str
    ids_mode: str
    alert_on_new_host: bool
    alert_on_port_change: bool


def load_config() -> dict:
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE) as f:
                return {**DEFAULT_CONFIG, **json.load(f)}
        except Exception:
            pass
    return DEFAULT_CONFIG.copy()


def save_config(config: dict):
    with open(CONFIG_FILE, "w") as f:
        json.dump(config, f, indent=2)


@router.get("/config")
async def get_network_config(credentials: HTTPAuthorizationCredentials = Depends(security)):
    return load_config()


@router.put("/config")
async def update_network_config(config: NetworkConfig, credentials: HTTPAuthorizationCredentials = Depends(security)):
    save_config(config.model_dump())
    return {"status": "saved", "config": config.model_dump()}


@router.get("/interfaces")
async def get_interfaces(credentials: HTTPAuthorizationCredentials = Depends(security)):
    try:
        import subprocess
        result = subprocess.run(["ip", "-o", "link", "show"], capture_output=True, text=True)
        interfaces = []
        for line in result.stdout.splitlines():
            parts = line.split(":")
            if len(parts) >= 2:
                name = parts[1].strip()
                if name != "lo":
                    interfaces.append(name)
        return {"interfaces": interfaces}
    except Exception:
        return {"interfaces": ["eth0", "ens18", "ens33"]}


@router.get("/subnet")
async def detect_subnet(credentials: HTTPAuthorizationCredentials = Depends(security)):
    try:
        import subprocess
        result = subprocess.run(["ip", "route"], capture_output=True, text=True)
        subnets = []
        for line in result.stdout.splitlines():
            if "/" in line and "src" in line:
                parts = line.split()
                subnets.append(parts[0])
        return {"subnets": subnets}
    except Exception:
        return {"subnets": ["192.168.1.0/24"]}
