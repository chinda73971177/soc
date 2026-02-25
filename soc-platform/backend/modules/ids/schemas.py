from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


class IDSAlert(BaseModel):
    id: Optional[str] = None
    timestamp: Optional[datetime] = None
    alert_type: Optional[str] = None
    severity: Optional[str] = None
    message: Optional[str] = None
    src_ip: Optional[str] = None
    src_port: Optional[int] = None
    dst_ip: Optional[str] = None
    dst_port: Optional[int] = None
    protocol: Optional[str] = None
    rule_id: Optional[str] = None
    action: Optional[str] = None
    category: Optional[str] = None


class IDSStatus(BaseModel):
    mode: str
    interface: str
    is_running: bool
    alerts_today: int
    top_categories: List[dict]


class IDSModeRequest(BaseModel):
    mode: str

class IDSRule(BaseModel):
    id: Optional[str] = None
    sid: Optional[int] = None
    name: str
    content: str
    severity: str = "medium"
    is_active: bool = True
