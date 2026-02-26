import httpx
from core.config import settings


async def send_whatsapp_alert(alert: dict) -> bool:
    if not all([settings.twilio_account_sid, settings.twilio_auth_token, settings.twilio_whatsapp_from, settings.whatsapp_to]):
        return False

    body = (
        f"[{alert.get('severity', '').upper()}] {alert.get('title', 'Alert')}\n"
        f"Type: {alert.get('alert_type', 'N/A')}\n"
        f"Source: {alert.get('source_ip', 'N/A')}:{alert.get('source_port', 'N/A')}\n"
        f"Target: {alert.get('destination_ip', 'N/A')}:{alert.get('destination_port', 'N/A')}\n"
        f"Service: {alert.get('service', 'N/A')}\n"
        f"Protocol: {alert.get('protocol', 'N/A')}\n"
        f"Time: {alert.get('timestamp', 'N/A')}"
    )

    url = f"https://api.twilio.com/2010-04-01/Accounts/{settings.twilio_account_sid}/Messages.json"
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            response = await client.post(
                url,
                auth=(settings.twilio_account_sid, settings.twilio_auth_token),
                data={"From": settings.twilio_whatsapp_from, "To": settings.whatsapp_to, "Body": body}
            )
            return response.status_code in [200, 201]
    except Exception:
        return False
