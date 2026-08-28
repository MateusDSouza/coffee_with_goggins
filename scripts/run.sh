#!/bin/bash

cd "$(dirname "$0")/.."

# Exit immediately if a command exits with a non-zero status
set -e

echo "🔍 Checking if Ollama server is running..."

# Check if Ollama API port 11434 is responding
if ! curl -s http://localhost:11434/ > /dev/null; then
    echo "🚀 Starting Ollama server in background..."
    ollama serve > /dev/null 2>&1 &

    # Wait until Ollama is fully initialized
    echo "⏳ Waiting for Ollama to accept connections..."
    while ! curl -s http://localhost:11434/ > /dev/null; do
        sleep 1
    done
    echo "✅ Ollama server is ready!"
else
    echo "✅ Ollama server is already running."
fi

# Activate virtual environment if present
if [ -d ".venv" ]; then
    echo "🐍 Activating Python virtual environment..."
    source .venv/bin/activate
fi

# Run the agent
echo "⚙️ Booting up HoLLyM Agent..."
python src/main.py
