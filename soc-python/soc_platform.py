#!/usr/bin/env python3
import os
import argparse
from flask import Flask
from modules.database import init_db
from modules.config import load_config, BASE_DIR
from modules.routes import api
from modules.ui import ui


def create_app() -> Flask:
    app = Flask(__name__, template_folder="templates", static_folder="static")
    cfg = load_config()
    app.secret_key = cfg["secret_key"]
    app.register_blueprint(api)
    app.register_blueprint(ui)
    return app


def main():
    parser = argparse.ArgumentParser(description="SOC Platform")
    parser.add_argument("--host", default="0.0.0.0", help="Bind address")
    parser.add_argument("--port", type=int, default=5000, help="Port")
    parser.add_argument("--debug", action="store_true", help="Debug mode")
    args = parser.parse_args()

    print("=" * 50)
    print("  SOC PLATFORM — Python Edition")
    print("=" * 50)
    print(f"  Initialising database...")
    init_db()
    print(f"  Database ready: data/soc.db")
    print(f"  Starting web server on http://{args.host}:{args.port}")
    print(f"  Default login: admin / admin123")
    print("=" * 50)

    app = create_app()
    app.run(host=args.host, port=args.port, debug=args.debug, threaded=True)


if __name__ == "__main__":
    main()
