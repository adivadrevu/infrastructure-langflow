#!/bin/bash
# Start Langflow with AWS Infrastructure Composer components
# This script loads .env variables and starts Langflow

set -e

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Load .env file if it exists
if [ -f .env ]; then
    echo "📋 Loading .env file..."
    export $(grep -v '^#' .env | xargs)
    echo "✅ Environment variables loaded"
fi

# Activate virtual environment
if [ -d .venv ]; then
    echo "🐍 Activating virtual environment..."
    source .venv/bin/activate
else
    echo "⚠️  Virtual environment not found. Creating one..."
    uv venv
    source .venv/bin/activate
    uv pip install -r requirements.txt
fi

# Set components path if not already set
if [ -z "$LANGFLOW_COMPONENTS_PATH" ]; then
    export LANGFLOW_COMPONENTS_PATH="$SCRIPT_DIR/components"
    echo "📂 Set LANGFLOW_COMPONENTS_PATH=$LANGFLOW_COMPONENTS_PATH"
fi

# Verify components directory exists
if [ ! -d "$LANGFLOW_COMPONENTS_PATH" ]; then
    echo "❌ Error: Components directory not found: $LANGFLOW_COMPONENTS_PATH"
    exit 1
fi

echo ""
echo "🚀 Starting Langflow..."
echo "   Components path: $LANGFLOW_COMPONENTS_PATH"
echo "   Access UI at: http://localhost:7860"
echo ""

# Start Langflow
langflow run --components-path "$LANGFLOW_COMPONENTS_PATH"
