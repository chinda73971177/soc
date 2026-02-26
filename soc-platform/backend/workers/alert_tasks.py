import asyncio
from workers.celery_app import celery_app
from modules.ids.suricata import parse_eve_alerts
from modules.alerts.telegram import send_telegram_alert
import logging

logger = logging.getLogger(__name__)

_last_processed = set()


@celery_app.task(name="workers.alert_tasks.process_ids_alerts")
def process_ids_alerts():
    global _last_processed
    alerts = parse_eve_alerts(limit=50)
    new_alerts = [a for a in alerts if a.get("id") not in _last_processed and a.get("severity") in ["critical", "high"]]
    for alert in new_alerts:
        _last_processed.add(alert.get("id"))
        try:
            asyncio.run(send_telegram_alert(alert))
        except Exception as e:
            logger.error(f"Notification failed: {e}")
    if len(_last_processed) > 10000:
        _last_processed = set(list(_last_processed)[-5000:])
    return {"processed": len(new_alerts)}
