#!/usr/bin/env bash
set -e
cd "$(dirname "$0")"

echo
echo "Starting Bellwether..."
export BELLWETHER_AI="${BELLWETHER_AI:-1}"
export BELLWETHER_AI_NUM_CTX="${BELLWETHER_AI_NUM_CTX:-4096}"
export BELLWETHER_AI_THREADS="${BELLWETHER_AI_THREADS:-$(getconf _NPROCESSORS_ONLN 2>/dev/null || nproc 2>/dev/null || echo 1)}"

echo "Bellwether automatically uses compatible models already installed in local Ollama."
echo "No model environment variables are required for normal play."
echo "LLM inference threads: ${BELLWETHER_AI_THREADS}"

if command -v ollama >/dev/null 2>&1; then
    echo "Installed Ollama models:"
    ollama list 2>/dev/null | sed -n '1,6p' || true
else
    echo "WARNING: Ollama command not found. Bellwether will use deterministic fallback simulation."
fi

echo
echo "Server will listen on all network interfaces."
LAN_IP="$(hostname -I 2>/dev/null | awk '{print $1}')"
echo "This computer: http://127.0.0.1:8000"
if [ -n "$LAN_IP" ]; then echo "Local WLAN:   http://${LAN_IP}:8000"; fi
echo
exec python -m uvicorn backend.app:app --host 0.0.0.0 --port 8000
