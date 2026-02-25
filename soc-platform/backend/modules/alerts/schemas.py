from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


class SecurityAlert(BaseModel):
    id: Optional[str] = None
    alert_type: str
    severity: str
    title: str
    description: Optional[str] = None
    source_ip: Optional[str] = None
    destination_ip: Optional[str] = None
    source_port: Optional[int] = None
    destination_port: Optional[int] = None
    protocol: Optional[str] = None
    service: Optional[str] = None
    rule_id: Optional[str] = None
    status: str = "open"
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class AlertUpdateRequest(BaseModel):
    status: str


class AlertAssignRequest(BaseModel):
    user_id: str


class AlertRule(BaseModel):
    id: Optional[str] = None
    name: str
    description: Optional[str] = None
    conditions: dict
    severity: str = "medium"
    is_active: bool = True
    notify_telegram: bool = False
    notify_whatsapp: bool = False
