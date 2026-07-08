#!/usr/bin/env bash
set -e

cd "$(dirname "$0")"

echo
echo "Starting Bellwether using the active Conda environment..."
export BELLWETHER_AI="${BELLWETHER_AI:-1}"
export BELLWETHER_AI_MODEL="${BELLWETHER_AI_MODEL:-qwen3:1.7b}"
export BELLWETHER_AI_THREADS="${BELLWETHER_AI_THREADS:-$(getconf _NPROCESSORS_ONLN 2>/dev/null || nproc 2>/dev/null || echo 1)}"
echo "AI Directors: enabled by default (${BELLWETHER_AI_MODEL})"
echo "LLM inference threads: ${BELLWETHER_AI_THREADS}"
echo "Optional thread benchmark: python3 tools/benchmark_llm_threads.py"
echo "Bellwether will ask the local model to choose a season while the server starts."
echo "The selected season will be printed below before the game is ready."

if command -v ollama >/dev/null 2>&1; then
    if ! ollama list 2>/dev/null | awk '{print $1}' | grep -qx "${BELLWETHER_AI_MODEL}"; then
        echo "WARNING: ${BELLWETHER_AI_MODEL} is not installed in Ollama."
        echo "Install once with: ollama pull ${BELLWETHER_AI_MODEL}"
    fi
else
    echo "WARNING: Ollama command not found. Bellwether will use baseline simulation."
fi


echo "Server will listen on all network interfaces."
echo

LAN_IP="$(hostname -I 2>/dev/null | awk '{print $1}')"

echo "This computer: http://127.0.0.1:8000"
if [ -n "$LAN_IP" ]; then
    echo "Local WLAN:   http://${LAN_IP}:8000"
fi
echo

exec python -m uvicorn backend.app:app --host 0.0.0.0 --port 8000
