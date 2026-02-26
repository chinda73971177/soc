import httpx
from modules.config import load_config

SEVERITY_ORDER = {"critical": 4, "high": 3, "medium": 2, "low": 1, "info": 0}


def _severity_meets_threshold(severity: str, threshold: str) -> bool:
    return SEVERITY_ORDER.get(severity, 0) >= SEVERITY_ORDER.get(threshold, 0)


def send_telegram(message: str) -> dict:
    cfg = load_config()
    token = cfg.get("telegram_token", "")
    chat_id = cfg.get("telegram_chat_id", "")
    if not token or not chat_id:
        return {"error": "Telegram not configured"}
    try:
        url = f"https://api.telegram.org/bot{token}/sendMessage"
        resp = httpx.post(url, json={"chat_id": chat_id, "text": message, "parse_mode": "HTML"}, timeout=10)
        return resp.json()
    except Exception as e:
        return {"error": str(e)}


def send_whatsapp(message: str) -> dict:
    cfg = load_config()
    sid = cfg.get("twilio_sid", "")
    token = cfg.get("twilio_token", "")
    from_n = cfg.get("twilio_from", "")
    to_n = cfg.get("twilio_to", "")
    if not all([sid, token, from_n, to_n]):
        return {"error": "WhatsApp/Twilio not configured"}
    try:
        url = f"https://api.twilio.com/2010-04-01/Accounts/{sid}/Messages.json"
        resp = httpx.post(url, data={"From": from_n, "To": to_n, "Body": message},
                          auth=(sid, token), timeout=10)
        return resp.json()
    except Exception as e:
        return {"error": str(e)}


def send_alert(title: str, severity: str, description: str):
    cfg = load_config()
    message = f"🚨 <b>SOC ALERT</b>\n<b>Severity:</b> {severity.upper()}\n<b>Title:</b> {title}\n<b>Details:</b> {description}"

    if cfg.get("telegram_token") and _severity_meets_threshold(severity, cfg.get("telegram_min_severity", "high")):
        send_telegram(message)

    plain = f"SOC ALERT | {severity.upper()} | {title} | {description}"
    if cfg.get("twilio_sid") and _severity_meets_threshold(severity, cfg.get("whatsapp_min_severity", "high")):
        send_whatsapp(plain)


def test_telegram() -> dict:
    return send_telegram("✅ SOC Platform — Telegram test message")


def test_whatsapp() -> dict:
    return send_whatsapp("SOC Platform — WhatsApp test message")
