#!/bin/bash

echo "🚀 Testing VoiceNews complete pipeline..."

# Check if .env has API keys
if grep -q "your_brave_api_key_here\|your_openai_api_key_here" .env; then
    echo "⚠️  Please add your actual API keys to .env file first!"
    echo "   1. Get Brave API key: https://api.search.brave.com/app/keys"
    echo "   2. Get OpenAI API key: https://platform.openai.com/api-keys"
    echo "   3. Edit .env file and replace placeholder values"
    exit 1
fi

# Activate virtual environment and load environment
source backend/venv/bin/activate
export $(cat .env | xargs)

# Start backend in background
echo "🔥 Starting backend server..."
cd backend
python main.py &
BACKEND_PID=$!
cd ..

# Wait for server to start
echo "⏳ Waiting for server to start..."
sleep 5

# Test the endpoints
echo "🧪 Testing news sources..."
curl -s http://localhost:8000/news/test | python3 -m json.tool

echo -e "\n🧪 Testing news pipeline (without audio)..."
curl -s "http://localhost:8000/news?limit=3&skip_audio=true" | python3 -m json.tool

# Cleanup
echo -e "\n🛑 Stopping server..."
kill $BACKEND_PID
echo "✅ Test completed!"