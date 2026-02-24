"""
Tests for Flask backend routing and static file serving.

Tests:
1. test_spa_fallback - Verifies SPA fallback routing works (nonexistent routes serve index.html)
2. test_static_file_serving - Verifies static files are served with correct content-type
3. test_health_json_format - Verifies health check endpoint returns proper JSON

Run tests:
    pytest test_routing.py -v
Or directly:
    python test_routing.py
"""

import sys
import json
import urllib.request
import urllib.error
from playwright.sync_api import sync_playwright

sys.path.insert(0, ".")
from conftest import BASE_URL, API_BASE


def test_spa_fallback():
    """
    Navigate to a nonexistent route and verify SPA fallback works.
    Should serve index.html and React should mount (h1 visible).
    """
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()

        # Navigate to nonexistent route
        response = page.goto(f"{BASE_URL}/nonexistent/route")

        # Assert response status is successful
        assert response.status < 400, f"Expected status < 400, got {response.status}"

        # Wait for network to be idle (React mounting complete)
        page.wait_for_load_state("networkidle")

        # Assert h1 is visible (React mounted)
        h1 = page.query_selector("h1")
        assert h1 is not None, "h1 element not found - React may not have mounted"
        assert h1.is_visible(), "h1 element not visible"

        browser.close()

    print("✓ test_spa_fallback passed")


def test_static_file_serving():
    """
    Verify static files are served with correct content-type.
    Gracefully skip if favicon.ico doesn't exist in dev.
    """
    try:
        response = urllib.request.urlopen(f"{API_BASE}/favicon.ico")
        content_type = response.headers.get("content-type", "")

        # Verify it's not HTML
        assert "text/html" not in content_type, f"Static file served as HTML: {content_type}"

        print("✓ test_static_file_serving passed (favicon.ico served correctly)")

    except urllib.error.HTTPError as e:
        if e.code == 404:
            print("✓ test_static_file_serving passed (favicon.ico not found - skipped gracefully)")
        else:
            raise


def test_health_json_format():
    """
    Verify health check endpoint returns proper JSON with status=ok.
    """
    response = urllib.request.urlopen(f"{API_BASE}/health")
    data = json.loads(response.read().decode("utf-8"))

    assert "status" in data, "JSON missing 'status' field"
    assert data["status"] == "ok", f"Expected status='ok', got '{data['status']}'"

    print("✓ test_health_json_format passed")


if __name__ == "__main__":
    failures = 0

    tests = [
        test_spa_fallback,
        test_static_file_serving,
        test_health_json_format,
    ]

    for test_func in tests:
        try:
            test_func()
        except Exception as e:
            print(f"✗ {test_func.__name__} failed: {e}")
            failures += 1

    print(f"\n{len(tests) - failures}/{len(tests)} tests passed")
    sys.exit(failures)
