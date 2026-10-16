#!/usr/bin/env bash
# Script to launch a free public tunnel for the Customer Support Agent Portal
set -e

PORT=${1:-5173}

echo "=========================================================="
echo " Starting Free Public Tunnel for Port $PORT"
echo " (Proxies both React Frontend and FastAPI Backend)"
echo "=========================================================="

echo "Launching secure TLS tunnel via localhost.run..."
ssh -o StrictHostKeyChecking=no -R 80:localhost:${PORT} nokey@localhost.run
