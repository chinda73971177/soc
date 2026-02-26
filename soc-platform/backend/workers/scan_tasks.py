import asyncio
from workers.celery_app import celery_app
from modules.network.scanner import run_scan
import logging

logger = logging.getLogger(__name__)


@celery_app.task(name="workers.scan_tasks.quick_scan")
def quick_scan(target: str = "192.168.1.0/24"):
    try:
        result = asyncio.run(run_scan(target, "quick"))
        logger.info(f"Quick scan completed: {len(result.get('hosts', []))} hosts found")
        return result
    except Exception as e:
        logger.error(f"Scan failed: {e}")
        return {"error": str(e)}
