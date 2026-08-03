#!/bin/bash
# start-models.sh — Start both local llama.cpp model servers
# Run this in git-bash (MSYS2) on Windows
# Each server uses ~1.1GB RAM, total ~2.5GB
#
# Usage:
#   ./start-models.sh              # start both
#   ./start-models.sh coder         # start only coder (:8080)
#   ./start-models.sh instruct      # start only instruct (:8081)
#   ./start-models.sh stop          # stop both
#   ./start-models.sh status        # check what's running

LLAMA_DIR="$(cd "$(dirname "$0")/local-llm/llama-cpp" && pwd)"
MODELS_DIR="$(cd "$(dirname "$0")/local-llm/models" && pwd)"
CODER_MODEL="$MODELS_DIR/qwen2.5-coder-1.5b-instruct-q4_k_m.gguf"
INSTRUCT_MODEL="$MODELS_DIR/qwen2.5-1.5b-instruct-q4_k_m.gguf"
SERVER="$LLAMA_DIR/llama-server.exe"

# CPU threading (adjust based on your CPU cores)
N_THREADS=8

start_server() {
    local port=$1
    local model=$2
    local name=$3

    if [ ! -f "$model" ]; then
        echo "ERROR: Model not found: $model"
        return 1
    fi

    # Check if already running
    if curl -s http://127.0.0.1:$port/v1/models > /dev/null 2>&1; then
        echo "✅ $name already running on :$port"
        return 0
    fi

    echo "Starting $name on :$port with $model"
    "$SERVER" \
        --model "$model" \
        --port $port \
        --host 127.0.0.1 \
        --threads $N_THREADS \
        --ctx-size 8192 \
        --batch-size 512 \
        --ubatch-size 256 \
        --mlock \
        --no-mmap \
        --temp 0.3 \
        --repeat-penalty 1.1 \
        > /dev/null 2>&1 &
    echo "PID: $!"
    sleep 5

    # Verify
    if curl -s http://127.0.0.1:$port/v1/models > /dev/null 2>&1; then
        echo "✅ $name is ready on :$port"
    else
        echo "⚠️  $name may not be ready yet — check logs"
    fi
}

stop_server() {
    local port=$1
    local name=$2
    local pid=$(netstat -ano 2>/dev/null | grep ":$port " | grep LISTENING | awk '{print $5}' | head -1)
    if [ -n "$pid" ]; then
        kill "$pid" 2>/dev/null
        echo "Stopped $name (:$port)"
    else
        echo "$name not running"
    fi
}

case "${1:-all}" in
    coder)
        start_server 8080 "$CODER_MODEL" "Coder"
        ;;
    instruct)
        start_server 8081 "$INSTRUCT_MODEL" "Instruct"
        ;;
    all)
        start_server 8080 "$CODER_MODEL" "Coder"
        start_server 8081 "$INSTRUCT_MODEL" "Instruct"
        ;;
    stop)
        stop_server 8080 "Coder"
        stop_server 8081 "Instruct"
        echo "Both servers stopped"
        ;;
    status)
        echo "=== Local Model Servers ==="
        for port in 8080 8081; do
            if curl -s http://127.0.0.1:$port/v1/models > /dev/null 2>&1; then
                name=$(curl -s http://127.0.0.1:$port/v1/models 2>/dev/null | python -c "import json,sys; d=json.load(sys.stdin); print(d.get('data',[{}])[0].get('id','unknown'))" 2>/dev/null || echo "unknown")
                echo "✅ :$port — $name"
            else
                echo "❌ :$port — not running"
            fi
        done
        ;;
    *)
        echo "Usage: $0 {all|coder|instruct|stop|status}"
        exit 1
        ;;
esac