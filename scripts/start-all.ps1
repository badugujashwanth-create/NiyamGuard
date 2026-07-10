Write-Host "Start these modules in separate terminals:" -ForegroundColor Cyan
Write-Host "1. Voice/Form Assistant backend: cd backend; uvicorn app.main:app --port 8000"
Write-Host "2. Voice/Form Assistant frontend: cd frontend; npm run dev -- --port 5173"
Write-Host "3. Citizen Chatbot backend: uvicorn app.main:app --port 8001"
Write-Host "4. Government Policy backend: uvicorn app.main:app --port 8002"
Write-Host "Then run: ./scripts/check-health.ps1"
