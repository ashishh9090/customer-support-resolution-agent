#!/usr/bin/env bash
while true; do
  echo "Connecting to pinggy tunnel..."
  ssh -o ServerAliveInterval=15 -o ServerAliveCountMax=4 -o StrictHostKeyChecking=no -p 443 -R0:localhost:5173 a.pinggy.io
  echo "Tunnel disconnected, reconnecting in 2s..."
  sleep 2
done
