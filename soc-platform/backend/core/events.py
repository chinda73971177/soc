from elasticsearch import AsyncElasticsearch
from core.config import settings
import logging

logger = logging.getLogger(__name__)


async def create_es_indices(es: AsyncElasticsearch):
    index_template = {
        "mappings": {
            "properties": {
                "@timestamp": {"type": "date"},
                "message": {"type": "text"},
                "host_name": {"type": "keyword"},
                "log_source": {"type": "keyword"},
                "log_type": {"type": "keyword"},
                "severity": {"type": "keyword"},
                "src_ip": {"type": "ip"},
                "dst_ip": {"type": "ip"},
                "src_port": {"type": "integer"},
                "dst_port": {"type": "integer"},
                "protocol": {"type": "keyword"},
                "service": {"type": "keyword"},
            }
        }
    }
    try:
        exists = await es.indices.exists_index_template(name="soc-logs-template")
        if not exists:
            await es.indices.put_index_template(
                name="soc-logs-template",
                body={
                    "index_patterns": ["soc-logs-*"],
                    **index_template
                }
            )
            logger.info("Elasticsearch index template created")
    except Exception as e:
        logger.error(f"Failed to create ES index template: {e}")
