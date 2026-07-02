#!/bin/bash
# HUMAN-POTENTIAL-GRAPH Quick Start Script
# Run this after extracting the zip to set up and run the app

set -e

echo "╔════════════════════════════════════════════════════════════════╗"
echo "║      HUMAN-POTENTIAL-GRAPH — Quick Start                       ║"
echo "║      Redrob Intelligent Candidate Discovery & Ranking          ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""

# Check Python
echo "🔍 Checking Python..."
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 not found. Please install Python 3.9 or later."
    exit 1
fi
PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
echo "✓ Found Python $PYTHON_VERSION"
echo ""

# Check if requirements already installed
echo "📦 Checking dependencies..."
if python3 -c "import flask" 2>/dev/null; then
    echo "✓ Flask already installed"
else
    echo "📥 Installing Flask..."
    pip install -q flask
    echo "✓ Flask installed"
fi
echo ""

# Check sample data
if [ ! -f "sample_candidates.json" ]; then
    echo "⚠️  sample_candidates.json not found in current directory"
fi

# Show options
echo "🎯 How would you like to run?"
echo ""
echo "  1) Web App (recommended — interactive UI in browser)"
echo "  2) CLI (headless ranking — faster, no browser)"
echo "  3) Try Demo (rank 50 sample candidates first)"
echo "  4) Docker (reproducible container environment)"
echo ""
read -p "Enter choice (1-4, default 1): " CHOICE
CHOICE=${CHOICE:-1}

case $CHOICE in
    1)
        echo ""
        echo "🚀 Starting web app..."
        echo ""
        echo "📍 Open your browser to:  http://localhost:5000"
        echo ""
        echo "💡 Tip: Click 'Try Sample (50 candidates)' for a quick demo"
        echo ""
        python3 app.py
        ;;
    2)
        echo ""
        read -p "📂 Enter path to candidates.jsonl: " INPUT_FILE
        if [ ! -f "$INPUT_FILE" ]; then
            echo "❌ File not found: $INPUT_FILE"
            exit 1
        fi
        read -p "💾 Enter output filename (default: submission.csv): " OUTPUT_FILE
        OUTPUT_FILE=${OUTPUT_FILE:-submission.csv}
        echo ""
        echo "🔄 Ranking $INPUT_FILE → $OUTPUT_FILE"
        python3 app.py rank "$INPUT_FILE" "$OUTPUT_FILE"
        echo ""
        echo "✓ Done! Output: $OUTPUT_FILE"
        echo ""
        if command -v head &> /dev/null; then
            echo "Preview:"
            head -5 "$OUTPUT_FILE"
        fi
        ;;
    3)
        echo ""
        echo "🚀 Starting web app (demo mode)..."
        echo ""
        echo "📍 Open your browser to:  http://localhost:5000"
        echo "🎬 Click: 'Try Sample (50 candidates)' button"
        echo ""
        python3 app.py &
        sleep 2
        if command -v open &> /dev/null; then
            open http://localhost:5000
        elif command -v xdg-open &> /dev/null; then
            xdg-open http://localhost:5000
        else
            echo "📌 Browser didn't auto-open. Visit http://localhost:5000 manually"
        fi
        wait
        ;;
    4)
        echo ""
        if ! command -v docker &> /dev/null; then
            echo "❌ Docker not found. Please install Docker Desktop."
            exit 1
        fi
        echo "🐳 Building Docker image..."
        docker build -t hpg-ranker .
        echo ""
        echo "🚀 Starting container..."
        echo "📍 Open your browser to:  http://localhost:7860"
        docker run -p 7860:7860 hpg-ranker
        ;;
    *)
        echo "❌ Invalid choice"
        exit 1
        ;;
esac
