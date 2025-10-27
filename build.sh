
set -euo pipefail

echo "Finding requirements.txt..."
REQ=$(find . -maxdepth 4 -type f -name "requirements.txt" | head -n 1 || true)
if [ -z "$REQ" ]; then
  echo "ERROR: requirements.txt not found within 4 levels."
  exit 1
fi

echo "Using requirements file: $REQ"
python -m pip install --upgrade pip
python -m pip install -r "$REQ"
echo "Dependencies installed."
