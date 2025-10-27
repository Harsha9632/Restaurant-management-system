#!/usr/bin/env bash
set -euo pipefail

echo "Locating server.py..."
SERVER_PY=$(find . -maxdepth 5 -type f -name "server.py" | head -n 1 || true)
if [ -z "$SERVER_PY" ]; then
  echo "ERROR: server.py not found within 5 levels."
  exit 1
fi

echo "Found server.py at: $SERVER_PY"
DIR=$(dirname "$SERVER_PY")

MODULE=$(echo "$DIR" | sed 's|^\./||; s|/$||; s|/|.|g')

if [ -z "$MODULE" ] || [ "$MODULE" = "." ]; then
  APP="server:app"
else
  APP="${MODULE}.server:app"
fi

echo "Starting uvicorn with app: $APP"
python -m uvicorn "$APP" --host 0.0.0.0 --port "${PORT:-8000}"
