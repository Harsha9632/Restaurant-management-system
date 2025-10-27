
set -euxo pipefail

echo "🔧 Installing backend dependencies..."
pip install -r backend/requirements.txt

echo "📦 Building frontend..."
cd frontend
npm install
npm run build

echo "📂 Copying React build into backend/static..."
rm -rf ../backend/static/*
cp -r build/* ../backend/static/

echo "✅ Build completed successfully!"

