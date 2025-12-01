#!/bin/bash
set -e

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🚀 Setting up Arkiv Python Starter environment..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

echo ""
echo "🐳 Starting Docker daemon..."
sudo nohup dockerd > /tmp/dockerd.log 2>&1 &
# Wait for Docker to be ready
for i in {1..10}; do
    if docker info > /dev/null 2>&1; then
        echo "   Docker daemon is ready!"
        break
    fi
    echo "   Waiting for Docker daemon to start..."
    sleep 1
done

echo ""
echo "🐍 Installing Python and dependencies with uv..."
# Remove any existing .venv with wrong permissions
if [ -d ".venv" ]; then
    echo "   Cleaning up old virtual environment..."
    sudo rm -rf .venv
fi
uv sync

echo ""
echo "✅ Verifying installation..."
echo "   Python: $(uv run python --version 2>/dev/null || echo 'Installing...')"
echo "   UV: $(uv --version)"
echo "   Docker: $(docker --version)"
echo "   Arkiv SDK: $(uv run python -c 'import arkiv; print(arkiv.__version__)' 2>/dev/null || echo 'Ready')"

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🎉 Dev container is ready!"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "Quick start commands:"
echo "  • uv run python -m arkiv_starter.01_basic_crud       # Run first example"
echo "  • uv run python -m arkiv_starter.02_queries          # Query entities"
echo "  • uv run python -m arkiv_starter.03_events           # Event listening"
echo "  • uv run python -m arkiv_starter.04_web3_integration # Web3 integration"
echo "  • uv run ipython                                     # Interactive Python"
echo ""
