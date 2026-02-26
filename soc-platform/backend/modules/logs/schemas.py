from pydantic import BaseModel
from typing import Optional, List, Any
from datetime import datetime


class LogEntry(BaseModel):
    id: Optional[str] = None
    timestamp: Optional[datetime] = None
    message: Optional[str] = None
    host_name: Optional[str] = None
    log_source: Optional[str] = None
    log_type: Optional[str] = None
    severity: Optional[str] = None
    program: Optional[str] = None
    src_ip: Optional[str] = None
    dst_ip: Optional[str] = None
    src_port: Optional[int] = None
    dst_port: Optional[int] = None
    protocol: Optional[str] = None
    service: Optional[str] = None
    raw: Optional[dict] = None


class LogSearchRequest(BaseModel):
    query: Optional[str] = None
    log_source: Optional[str] = None
    log_type: Optional[str] = None
    severity: Optional[str] = None
    host: Optional[str] = None
    src_ip: Optional[str] = None
    dst_ip: Optional[str] = None
    port: Optional[int] = None
    protocol: Optional[str] = None
    service: Optional[str] = None
    date_from: Optional[datetime] = None
    date_to: Optional[datetime] = None
    page: int = 1
    page_size: int = 50


class LogSearchResponse(BaseModel):
    total: int
    page: int
    page_size: int
    logs: List[LogEntry]


class LogStatsResponse(BaseModel):
    total_today: int
    by_severity: dict
    by_source: dict
    by_type: dict
    timeline: List[dict]
