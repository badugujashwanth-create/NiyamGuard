$services = @(
  @{ Name = "Voice/Form Assistant"; Url = "http://127.0.0.1:8000/api/integration/health" },
  @{ Name = "Citizen Chatbot"; Url = "http://127.0.0.1:8001/api/integration/health" },
  @{ Name = "Government Policy Backend"; Url = "http://127.0.0.1:8002/api/integration/health" }
)

foreach ($service in $services) {
  try {
    $response = Invoke-RestMethod -Uri $service.Url -Method Get -TimeoutSec 4
    Write-Host "$($service.Name): Online" -ForegroundColor Green
    $response | ConvertTo-Json -Depth 8
  } catch {
    Write-Host "$($service.Name): Offline - start the service locally to check" -ForegroundColor Red
  }
}
