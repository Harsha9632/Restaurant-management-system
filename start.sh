
set -euxo pipefail

echo "🚀 Starting FastAPI server..."
cd backend
python -m uvicorn server:app --host 0.0.0.0 --port $PORT

