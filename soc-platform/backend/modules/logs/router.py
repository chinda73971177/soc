from fastapi import APIRouter, Depends, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from modules.logs.schemas import LogSearchRequest, LogSearchResponse, LogStatsResponse, LogEntry
from modules.logs.elasticsearch import search_logs, get_log_stats

router = APIRouter()
security = HTTPBearer(auto_error=False)


@router.post("/search", response_model=LogSearchResponse)
async def search(request: Request, params: LogSearchRequest, credentials: HTTPAuthorizationCredentials = Depends(security)):
    es = request.app.state.es
    result = await search_logs(es, params.model_dump())
    logs = [LogEntry(id=h.get("id"), **{k: v for k, v in h.items() if k != "id"}) for h in result["hits"]]
    return LogSearchResponse(total=result["total"], page=params.page, page_size=params.page_size, logs=logs)


@router.get("/stats", response_model=LogStatsResponse)
async def stats(request: Request, credentials: HTTPAuthorizationCredentials = Depends(security)):
    es = request.app.state.es
    data = await get_log_stats(es)
    return LogStatsResponse(**data)


@router.get("/{log_id}")
async def get_log(log_id: str, request: Request, credentials: HTTPAuthorizationCredentials = Depends(security)):
    es = request.app.state.es
    result = await es.get(index="soc-logs-*", id=log_id)
    return {"id": result["_id"], **result["_source"]}
