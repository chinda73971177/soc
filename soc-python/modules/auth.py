import bcrypt
import jwt
import datetime
from functools import wraps
from flask import request, jsonify, session
from modules.database import get_conn
from modules.config import load_config


def verify_password(plain: str, hashed: str) -> bool:
    return bcrypt.checkpw(plain.encode(), hashed.encode())


def hash_password(plain: str) -> str:
    return bcrypt.hashpw(plain.encode(), bcrypt.gensalt()).decode()


def generate_token(user_id: int, username: str, role: str) -> str:
    cfg = load_config()
    payload = {
        "sub": user_id,
        "username": username,
        "role": role,
        "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=8),
    }
    return jwt.encode(payload, cfg["secret_key"], algorithm="HS256")


def decode_token(token: str) -> dict | None:
    cfg = load_config()
    try:
        return jwt.decode(token, cfg["secret_key"], algorithms=["HS256"])
    except Exception:
        return None


def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        auth = request.headers.get("Authorization", "")
        if auth.startswith("Bearer "):
            token = auth[7:]
        if not token:
            token = session.get("token")
        if not token:
            if request.is_json:
                return jsonify({"error": "Unauthorized"}), 401
            from flask import redirect, url_for
            return redirect(url_for("ui.login_page"))
        payload = decode_token(token)
        if not payload:
            if request.is_json:
                return jsonify({"error": "Invalid token"}), 401
            from flask import redirect, url_for
            return redirect(url_for("ui.login_page"))
        request.current_user = payload
        return f(*args, **kwargs)
    return decorated


def get_user(username: str) -> dict | None:
    conn = get_conn()
    row = conn.execute("SELECT * FROM users WHERE username=?", (username,)).fetchone()
    conn.close()
    return dict(row) if row else None
