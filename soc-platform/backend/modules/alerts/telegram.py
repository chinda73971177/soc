import httpx
from core.config import settings


async def send_telegram_alert(alert: dict) -> bool:
    if not settings.telegram_bot_token or not settings.telegram_chat_id:
        return False

    severity_emoji = {"critical": "🔴", "high": "🟠", "medium": "🟡", "low": "🔵", "info": "⚪"}
    emoji = severity_emoji.get(alert.get("severity", "info"), "⚪")

    text = f"""{emoji} [{alert.get('severity', '').upper()}] {alert.get('title', 'Alert')}

⏱ {alert.get('timestamp', 'N/A')}
📋 Type     : {alert.get('alert_type', 'N/A')}
🌐 Source   : {alert.get('source_ip', 'N/A')}:{alert.get('source_port', 'N/A')}
🎯 Cible    : {alert.get('destination_ip', 'N/A')}:{alert.get('destination_port', 'N/A')}
📡 Service  : {alert.get('service', 'N/A')}
⚡ Protocole: {alert.get('protocol', 'N/A')}
🔑 Règle    : {alert.get('rule_id', 'N/A')}

{alert.get('description', '')}"""

    url = f"https://api.telegram.org/bot{settings.telegram_bot_token}/sendMessage"
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            response = await client.post(url, json={"chat_id": settings.telegram_chat_id, "text": text, "parse_mode": "HTML"})
            return response.status_code == 200
    except Exception:
        return False
