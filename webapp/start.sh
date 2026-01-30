#!/bin/bash

# Avangrid APM Platform - Start Script

echo "⚡ Starting Avangrid APM Platform..."
echo ""

# Check if we're in the webapp directory
if [ ! -f "app.py" ]; then
    echo "❌ Error: app.py not found!"
    echo "Please run this script from the webapp directory"
    exit 1
fi

# Check if .env exists
if [ ! -f ".env" ]; then
    echo "⚠️  Warning: .env file not found!"
    echo "Please create .env with your OpenAI API key"
    exit 1
fi

# Create data directory if it doesn't exist
mkdir -p data

echo "✅ Environment OK"
echo ""
echo "🚀 Launching application..."
echo "📱 The app will open at: http://localhost:8501"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

# Run Streamlit
streamlit run app.py --server.port 8501 --server.headless true
