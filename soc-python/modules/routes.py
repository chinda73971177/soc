import os
from flask import Blueprint, request, jsonify, session, redirect, url_for
from modules.auth import verify_password, generate_token, login_required, get_user
from modules.database import get_conn
from modules.config import load_config, save_config
from modules.log_analysis import process_upload, search_logs, get_log_stats
from modules.scanner import scan_async, get_status as scanner_status, scan_network
from modules.ids import (get_alerts, update_alert_status, get_alert_stats,
                          start_capture, stop_capture, capture_status, get_recent_packets)
from modules.assets import get_all_assets, get_asset, delete_asset, get_asset_stats
from modules.notifications import send_telegram, send_whatsapp, test_telegram, test_whatsapp
from modules.config import UPLOAD_DIR

api = Blueprint("api", __name__, url_prefix="/api")
ALLOWED_EXT = {".log", ".txt", ".json", ".csv"}


@api.route("/auth/login", methods=["POST"])
def login():
    data = request.json or {}
    user = get_user(data.get("username", ""))
    if not user or not verify_password(data.get("password", ""), user["password_hash"]):
        return jsonify({"error": "Invalid credentials"}), 401
    token = generate_token(user["id"], user["username"], user["role"])
    session["token"] = token
    return jsonify({"token": token, "username": user["username"], "role": user["role"]})


@api.route("/auth/logout", methods=["POST"])
def logout():
    session.clear()
    return jsonify({"status": "logged out"})


@api.route("/dashboard/stats")
@login_required
def dashboard_stats():
    log_s = get_log_stats()
    alert_s = get_alert_stats()
    asset_s = get_asset_stats()
    cap = capture_status()
    return jsonify({
        "logs": log_s,
        "alerts": alert_s,
        "assets": asset_s,
        "capture": cap,
    })


@api.route("/logs/upload", methods=["POST"])
@login_required
def upload_log():
    if "file" not in request.files:
        return jsonify({"error": "No file provided"}), 400
    f = request.files["file"]
    ext = os.path.splitext(f.filename or "")[1].lower()
    if ext not in ALLOWED_EXT:
        return jsonify({"error": f"Unsupported type '{ext}'"}), 400
    os.makedirs(UPLOAD_DIR, exist_ok=True)
    save_path = os.path.join(UPLOAD_DIR, f.filename)
    f.save(save_path)
    result = process_upload(save_path, f.filename)
    return jsonify({"filename": f.filename, **result})


@api.route("/logs/search")
@login_required
def logs_search():
    r = request.args
    result = search_logs(
        query=r.get("query", ""), severity=r.get("severity", ""),
        log_type=r.get("log_type", ""), src_ip=r.get("src_ip", ""),
        dst_ip=r.get("dst_ip", ""), protocol=r.get("protocol", ""),
        service=r.get("service", ""),
        page=int(r.get("page", 1)), page_size=int(r.get("page_size", 50)),
    )
    return jsonify(result)


@api.route("/logs/stats")
@login_required
def logs_stats():
    return jsonify(get_log_stats())


@api.route("/alerts")
@login_required
def alerts():
    r = request.args
    return jsonify(get_alerts(
        status=r.get("status"), severity=r.get("severity"),
        page=int(r.get("page", 1)), page_size=int(r.get("page_size", 50)),
    ))


@api.route("/alerts/<int:alert_id>/status", methods=["PUT"])
@login_required
def alert_status(alert_id):
    data = request.json or {}
    update_alert_status(alert_id, data.get("status", "open"))
    return jsonify({"status": "updated"})


@api.route("/alerts/stats")
@login_required
def alerts_stats():
    return jsonify(get_alert_stats())


@api.route("/network/scan", methods=["POST"])
@login_required
def network_scan():
    data = request.json or {}
    target = data.get("target")
    scan_type = data.get("scan_type", "standard")
    async_mode = data.get("async", True)
    if async_mode:
        scan_async(target, scan_type)
        return jsonify({"status": "scan started"})
    result = scan_network(target, scan_type)
    return jsonify(result)


@api.route("/network/scan/status")
@login_required
def network_scan_status():
    return jsonify(scanner_status())


@api.route("/capture/start", methods=["POST"])
@login_required
def capture_start():
    data = request.json or {}
    return jsonify(start_capture(interface=data.get("interface")))


@api.route("/capture/stop", methods=["POST"])
@login_required
def capture_stop():
    return jsonify(stop_capture())


@api.route("/capture/status")
@login_required
def capture_status_route():
    return jsonify(capture_status())


@api.route("/capture/packets")
@login_required
def packets():
    limit = int(request.args.get("limit", 100))
    return jsonify(get_recent_packets(limit))


@api.route("/assets")
@login_required
def assets_list():
    r = request.args
    return jsonify(get_all_assets(
        page=int(r.get("page", 1)), page_size=int(r.get("page_size", 50))
    ))


@api.route("/assets/<ip>")
@login_required
def asset_detail(ip):
    a = get_asset(ip)
    if not a:
        return jsonify({"error": "Not found"}), 404
    return jsonify(a)


@api.route("/assets/<ip>", methods=["DELETE"])
@login_required
def asset_delete(ip):
    delete_asset(ip)
    return jsonify({"status": "deleted"})


@api.route("/config", methods=["GET"])
@login_required
def config_get():
    cfg = load_config()
    safe = {k: v for k, v in cfg.items() if "token" not in k and "secret" not in k and "sid" not in k}
    return jsonify(safe)


@api.route("/config", methods=["PUT"])
@login_required
def config_put():
    data = request.json or {}
    cfg = load_config()
    cfg.update(data)
    save_config(cfg)
    return jsonify({"status": "saved"})


@api.route("/notifications/test/telegram", methods=["POST"])
@login_required
def notif_telegram():
    return jsonify(test_telegram())


@api.route("/notifications/test/whatsapp", methods=["POST"])
@login_required
def notif_whatsapp():
    return jsonify(test_whatsapp())


@api.route("/health")
def health():
    return jsonify({"status": "ok"})
