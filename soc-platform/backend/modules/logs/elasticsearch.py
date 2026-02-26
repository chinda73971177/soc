from elasticsearch import AsyncElasticsearch
from typing import Optional
from datetime import datetime, timedelta


async def search_logs(es: AsyncElasticsearch, params: dict) -> dict:
    must_clauses = []
    filter_clauses = []

    if params.get("query"):
        must_clauses.append({"multi_match": {"query": params["query"], "fields": ["message", "host_name", "program", "service"]}})

    for field in ["log_source", "log_type", "severity", "protocol", "service"]:
        if params.get(field):
            filter_clauses.append({"term": {field: params[field]}})

    if params.get("host"):
        filter_clauses.append({"term": {"host_name": params["host"]}})

    for ip_field, param_key in [("src_ip", "src_ip"), ("dst_ip", "dst_ip")]:
        if params.get(param_key):
            filter_clauses.append({"term": {ip_field: params[param_key]}})

    if params.get("port"):
        filter_clauses.append({
            "bool": {
                "should": [
                    {"term": {"src_port": params["port"]}},
                    {"term": {"dst_port": params["port"]}}
                ]
            }
        })

    date_range = {}
    if params.get("date_from"):
        date_range["gte"] = params["date_from"].isoformat()
    if params.get("date_to"):
        date_range["lte"] = params["date_to"].isoformat()
    if date_range:
        filter_clauses.append({"range": {"@timestamp": date_range}})

    query = {"bool": {"must": must_clauses, "filter": filter_clauses}} if (must_clauses or filter_clauses) else {"match_all": {}}

    page = params.get("page", 1)
    page_size = params.get("page_size", 50)

    result = await es.search(
        index="soc-logs-*",
        body={
            "query": query,
            "sort": [{"@timestamp": {"order": "desc"}}],
            "from": (page - 1) * page_size,
            "size": page_size,
        }
    )

    return {
        "total": result["hits"]["total"]["value"],
        "hits": [{"id": h["_id"], **h["_source"]} for h in result["hits"]["hits"]]
    }


async def get_log_stats(es: AsyncElasticsearch) -> dict:
    now = datetime.utcnow()
    day_ago = now - timedelta(hours=24)

    result = await es.search(
        index="soc-logs-*",
        body={
            "query": {"range": {"@timestamp": {"gte": day_ago.isoformat(), "lte": now.isoformat()}}},
            "size": 0,
            "aggs": {
                "by_severity": {"terms": {"field": "severity", "size": 10}},
                "by_source": {"terms": {"field": "log_source", "size": 10}},
                "by_type": {"terms": {"field": "log_type", "size": 10}},
                "timeline": {
                    "date_histogram": {
                        "field": "@timestamp",
                        "calendar_interval": "1h",
                        "min_doc_count": 0,
                        "extended_bounds": {"min": day_ago.isoformat(), "max": now.isoformat()}
                    }
                }
            }
        }
    )

    def agg_to_dict(agg):
        return {b["key"]: b["doc_count"] for b in agg.get("buckets", [])}

    return {
        "total_today": result["hits"]["total"]["value"],
        "by_severity": agg_to_dict(result["aggregations"]["by_severity"]),
        "by_source": agg_to_dict(result["aggregations"]["by_source"]),
        "by_type": agg_to_dict(result["aggregations"]["by_type"]),
        "timeline": [
            {"time": b["key_as_string"], "count": b["doc_count"]}
            for b in result["aggregations"]["timeline"]["buckets"]
        ]
    }
