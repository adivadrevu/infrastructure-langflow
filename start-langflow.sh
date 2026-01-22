#!/bin/bash
# Start Langflow with AWS Infrastructure Composer components
# This script loads .env variables and starts Langflow
# PRIVACY: Automatically disables Langflow tracking/telemetry

set -e

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# ============================================================================
# PRIVACY: Disable Langflow tracking/telemetry
# ============================================================================
# Always set DO_NOT_TRACK to prevent Langflow from sending any data
# This is set BEFORE loading .env to ensure it cannot be overridden
export DO_NOT_TRACK=true
export LANGFLOW_DO_NOT_TRACK=true
export LANGFLOW_TELEMETRY=false

# Load .env file if it exists
if [ -f .env ]; then
    echo "📋 Loading .env file..."
    # Load .env but ensure tracking remains disabled
    export $(grep -v '^#' .env | xargs)
    echo "✅ Environment variables loaded"
    
    # Re-enforce tracking disable (in case .env tried to override)
    export DO_NOT_TRACK=true
    export LANGFLOW_DO_NOT_TRACK=true
    export LANGFLOW_TELEMETRY=false
else
    echo "📋 No .env file found, using defaults"
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
# Components are now in infrastructure_composer/interfaces/langflow/components
if [ -z "$LANGFLOW_COMPONENTS_PATH" ]; then
    export LANGFLOW_COMPONENTS_PATH="$SCRIPT_DIR/infrastructure_composer/interfaces/langflow/components"
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
echo "   Privacy: Tracking disabled (DO_NOT_TRACK=true)"
echo "   Access UI at: http://localhost:7860"
echo ""

# Start Langflow with tracking explicitly disabled
# Environment variables (set above) are the primary method to disable tracking
# Langflow respects DO_NOT_TRACK environment variable
langflow run --components-path "$LANGFLOW_COMPONENTS_PATH"
