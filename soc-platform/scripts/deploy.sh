#!/bin/bash
set -e

echo "=== SOC Platform Deployment ==="

if [ ! -f .env ]; then
    echo "[*] Creating .env from template..."
    cp .env.example .env
    echo "[!] Edit .env with your configuration before proceeding"
    exit 1
fi

echo "[*] Pulling images..."
docker compose pull --quiet

echo "[*] Building services..."
docker compose build --no-cache

echo "[*] Starting infrastructure..."
docker compose up -d postgres redis zookeeper kafka elasticsearch

echo "[*] Waiting for services to be ready (60s)..."
sleep 60

echo "[*] Starting application..."
docker compose up -d logstash backend worker beat frontend nginx

echo "[*] Deployment complete."
echo ""
echo "  SOC Platform: http://localhost"
echo "  API Docs:      http://localhost/api/v1/docs"
echo "  Default creds: admin / admin"
echo ""
docker compose ps
