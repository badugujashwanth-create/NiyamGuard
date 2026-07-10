from __future__ import annotations

import argparse
import json
from pathlib import Path
from urllib.request import Request, urlopen


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT = ROOT / "docs" / "recording-assets"


DEMO_PAGES = [
    ("/demo", "demo-dashboard"),
    ("/admin/readiness", "admin-readiness"),
    ("/admin/regulatory-ai", "regulatory-ai"),
    ("/virtual-gov", "virtual-government-sandbox"),
    ("/services", "service-portal"),
]


def write_manual_checklist(output_dir: Path, frontend_url: str) -> Path:
    output_dir.mkdir(parents=True, exist_ok=True)
    checklist = output_dir / "manual-recording-checklist.md"
    lines = [
        "# Manual Demo Recording Checklist",
        "",
        "Record a 3 to 5 minute walkthrough after backend and frontend are running.",
        "",
        "## Pages",
    ]
    for path, label in DEMO_PAGES:
        lines.append(f"- `{frontend_url.rstrip('/')}{path}` - {label}")
    lines.extend(
        [
            "",
            "## Flow",
            "",
            "1. Open `/demo` and show AI provider/search status.",
            "2. Open `/admin/readiness` and show all controls ready.",
            "3. Run the virtual government sandbox scenario.",
            "4. Open `/admin/regulatory-ai` and ask `Why is ORG-0029 high risk?`.",
            "5. Open `/services` and show the Income Certificate service.",
            "6. Open `/` and ask `income certificate validity entha`.",
            "",
            "Save the video in this folder as `niyamguard-final-demo.mp4`.",
        ]
    )
    checklist.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return checklist


def login_session(backend_url: str) -> dict | None:
    request = Request(
        f"{backend_url.rstrip('/')}/api/auth/login",
        data=json.dumps({"email": "admin@niyamguard.local", "password": "Admin@12345"}).encode("utf-8"),
        method="POST",
        headers={"Content-Type": "application/json"},
    )
    try:
        with urlopen(request, timeout=20) as response:
            return json.loads(response.read().decode("utf-8"))
    except Exception:
        return None


def try_playwright_capture(output_dir: Path, frontend_url: str, backend_url: str) -> list[Path]:
    try:
        from playwright.sync_api import sync_playwright
    except Exception:
        return []

    output_dir.mkdir(parents=True, exist_ok=True)
    screenshots: list[Path] = []
    session = login_session(backend_url)
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=True)
        context = browser.new_context(viewport={"width": 1440, "height": 1000}, record_video_dir=str(output_dir / "videos"))
        if session:
            browser_session = json.dumps(
                {
                    "accessToken": session.get("access_token", ""),
                    "refreshToken": session.get("refresh_token", ""),
                    "user": session.get("user") or {},
                }
            )
            context.add_init_script(
                f"""
                (() => {{
                  const session = {browser_session};
                  window.localStorage.setItem('niyamguard.access_token', session.accessToken);
                  window.localStorage.setItem('niyamguard.refresh_token', session.refreshToken);
                  window.localStorage.setItem('niyamguard.user', JSON.stringify(session.user));
                }})();
                """
            )
        page = context.new_page()
        for path, label in DEMO_PAGES:
            page.goto(f"{frontend_url.rstrip('/')}{path}", wait_until="networkidle", timeout=30000)
            screenshot = output_dir / f"{label}.png"
            page.screenshot(path=str(screenshot), full_page=True)
            screenshots.append(screenshot)
        context.close()
        browser.close()
    return screenshots


def main() -> None:
    parser = argparse.ArgumentParser(description="Capture NiyamGuard demo screenshots/video assets when Playwright is available.")
    parser.add_argument("--frontend-url", default="http://127.0.0.1:5173")
    parser.add_argument("--backend-url", default="http://127.0.0.1:8000")
    parser.add_argument("--output-dir", default=str(DEFAULT_OUTPUT))
    args = parser.parse_args()

    output_dir = Path(args.output_dir).resolve()
    screenshots = try_playwright_capture(output_dir, args.frontend_url, args.backend_url)
    checklist = write_manual_checklist(output_dir, args.frontend_url)
    if screenshots:
        print(f"Captured {len(screenshots)} screenshots under {output_dir}")
    else:
        print("Playwright is not installed or browser capture failed; wrote manual checklist instead.")
    print(checklist)


if __name__ == "__main__":
    main()
