#!/usr/bin/env bash
set -euo pipefail

check() {
  local name="$1"
  local url="$2"
  if curl --fail --silent --show-error --max-time 4 "$url"; then
    printf '\n%s: Online\n' "$name"
  else
    printf '\n%s: Offline - start the service locally to check\n' "$name"
  fi
}

check "Voice/Form Assistant" "http://127.0.0.1:8000/api/integration/health"
check "Citizen Chatbot" "http://127.0.0.1:8001/api/integration/health"
check "Government Policy Backend" "http://127.0.0.1:8002/api/integration/health"
