#!/usr/bin/env bash
cat <<'EOF'
Start these modules in separate terminals:
1. Voice/Form Assistant backend: cd backend && uvicorn app.main:app --port 8000
2. Voice/Form Assistant frontend: cd frontend && npm run dev -- --port 5173
3. Citizen Chatbot backend: uvicorn app.main:app --port 8001
4. Government Policy backend: uvicorn app.main:app --port 8002
Then run: ./scripts/check-health.sh
EOF
