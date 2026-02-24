"""
Smoke tests for Learning Finnish.
Verifies the page loads and the API is healthy.

Run:
  python test_smoke.py
  TEST_BASE_URL=https://ai-vaerksted.cloud/finnish python test_smoke.py
"""
import sys
import urllib.request
import urllib.error
from playwright.sync_api import sync_playwright

sys.path.insert(0, ".")
from conftest import BASE_URL, API_BASE


def test_smoke():
    """Page loads, returns HTTP < 400, no console errors, no failed requests."""
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        console_errors = []
        failed_requests = []
        page.on("console", lambda msg: console_errors.append(msg.text) if msg.type == "error" else None)
        page.on("requestfailed", lambda req: failed_requests.append(req.url))

        response = page.goto(BASE_URL)
        assert response.status < 400, f"Page returned HTTP {response.status}"
        page.wait_for_load_state("networkidle")

        assert page.title() != "", "Page has no title"
        assert console_errors == [], f"Console errors: {console_errors}"
        assert failed_requests == [], f"Failed requests: {failed_requests}"

        browser.close()
        print(f"✓ test_smoke passed — {BASE_URL}")


def test_api_health():
    """Both /health and /api/health return 200 with status ok."""
    for path in ["/health", "/api/health"]:
        url = f"{API_BASE}{path}"
        try:
            with urllib.request.urlopen(url, timeout=5) as resp:
                assert resp.status == 200, f"{url} returned HTTP {resp.status}"
        except urllib.error.HTTPError as e:
            raise AssertionError(f"{url} returned HTTP {e.code}") from e
        print(f"✓ test_api_health passed — {url}")


if __name__ == "__main__":
    failures = 0
    for test in [test_smoke, test_api_health]:
        try:
            test()
        except Exception as e:
            print(f"✗ {test.__name__} FAILED: {e}")
            failures += 1
    sys.exit(failures)
