from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


@dataclass
class CheckResult:
    name: str
    success: bool
    status: int | None
    detail: str


def request_json(base_url: str, method: str, path: str, payload: dict[str, Any] | None = None) -> tuple[int, dict[str, Any]]:
    body = json.dumps(payload).encode("utf-8") if payload is not None else None
    request = Request(
        f"{base_url.rstrip('/')}{path}",
        data=body,
        method=method,
        headers={"Content-Type": "application/json"},
    )
    with urlopen(request, timeout=20) as response:
        return response.status, json.loads(response.read().decode("utf-8"))


def run_check(name: str, base_url: str, method: str, path: str, payload: dict[str, Any] | None = None) -> CheckResult:
    try:
        status, data = request_json(base_url, method, path, payload)
        success = 200 <= status < 300 and data.get("success", True) is not False
        return CheckResult(name, success, status, _detail(data))
    except HTTPError as error:
        return CheckResult(name, False, error.code, error.read().decode("utf-8", errors="replace")[:300])
    except (URLError, TimeoutError, json.JSONDecodeError) as error:
        return CheckResult(name, False, None, str(error))


def _detail(data: dict[str, Any]) -> str:
    for key in ("status", "method", "pilot_status", "provider", "message"):
        if key in data:
            return str(data[key])
    if "indexed_chunks" in data:
        return f"{data['indexed_chunks']} chunks"
    if "services" in data:
        return f"{len(data['services'])} services"
    if "scenarios" in data:
        return f"{len(data['scenarios'])} scenarios"
    if "artifacts" in data:
        return str(data["artifacts"].get("certificate_number") or data["artifacts"].get("application_number"))
    return "ok"


def main() -> int:
    parser = argparse.ArgumentParser(description="Final NiyamGuard API smoke test.")
    parser.add_argument("--base-url", default="http://127.0.0.1:8000")
    args = parser.parse_args()

    checks = [
        ("health", "GET", "/api/health", None),
        ("ops_status", "GET", "/api/ops/status", None),
        ("search_status", "GET", "/api/search/status", None),
        ("ai_status", "GET", "/api/ai/status", None),
        ("dataset_status", "GET", "/api/dataset/status", None),
        ("portal_services", "GET", "/api/portal/services", None),
        ("hybrid_answer", "POST", "/api/hybrid/answer", {"question": "income certificate validity entha"}),
        ("virtual_gov_scenarios", "GET", "/api/virtual-gov/scenarios", None),
        (
            "virtual_gov_run",
            "POST",
            "/api/virtual-gov/run",
            {"scenario_id": "income_certificate_full_flow", "reset_before_run": True},
        ),
    ]
    results = [run_check(name, args.base_url, method, path, payload) for name, method, path, payload in checks]
    for result in results:
        mark = "PASS" if result.success else "FAIL"
        print(f"{mark} {result.name} [{result.status or 'no-status'}] {result.detail}")
    failed = [result for result in results if not result.success]
    print(json.dumps({"success": not failed, "failed": [result.name for result in failed]}, indent=2))
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
