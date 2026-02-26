from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


class PortInfo(BaseModel):
    port: int
    protocol: str
    service: Optional[str] = None
    version: Optional[str] = None
    state: str


class Asset(BaseModel):
    id: Optional[str] = None
    ip_address: str
    mac_address: Optional[str] = None
    hostname: Optional[str] = None
    os_type: Optional[str] = None
    os_version: Optional[str] = None
    asset_type: Optional[str] = None
    criticality: str = "medium"
    first_seen: Optional[datetime] = None
    last_seen: Optional[datetime] = None
    is_active: bool = True
    ports: Optional[List[PortInfo]] = None
    tags: Optional[List[str]] = None


class ScanRequest(BaseModel):
    target: str
    scan_type: str = "standard"


class ScanResult(BaseModel):
    id: str
    target: str
    scan_type: str
    status: str
    started_at: datetime
    completed_at: Optional[datetime] = None
    hosts_found: int = 0
    results: Optional[dict] = None


class NetworkChange(BaseModel):
    id: str
    asset_id: Optional[str] = None
    change_type: str
    previous: Optional[dict] = None
    current: Optional[dict] = None
    detected_at: datetime
    acknowledged: bool = False
