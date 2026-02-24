"""
Performance sanity tests for the Finnish learning application.

Tests basic performance metrics with generous thresholds (not benchmarks):
1. Page load time < 5.0 seconds
2. Health endpoint response < 1.0 seconds
3. No single asset exceeds 5MB

Run with: python tests/playwright/test_performance.py
Or via pytest: pytest tests/playwright/test_performance.py
"""

import sys
import time
import urllib.request
from playwright.sync_api import sync_playwright

sys.path.insert(0, ".")
from conftest import BASE_URL, API_BASE


def test_page_load_time():
    """Measure page load time from navigation to networkidle state."""
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()

        start_time = time.time()
        page.goto(BASE_URL)
        page.wait_for_load_state("networkidle")
        elapsed_ms = (time.time() - start_time) * 1000
        elapsed_sec = elapsed_ms / 1000

        browser.close()

        assert elapsed_sec < 5.0, f"Page load took {elapsed_sec:.2f}s, expected < 5.0s"
        print(f"✓ test_page_load_time passed ({elapsed_ms:.0f}ms)")


def test_health_response_time():
    """Measure health endpoint response time."""
    health_url = f"{API_BASE}/health"

    start_time = time.time()
    try:
        with urllib.request.urlopen(health_url, timeout=5) as response:
            response.read()
    except Exception as e:
        raise AssertionError(f"Health endpoint request failed: {e}")

    elapsed_ms = (time.time() - start_time) * 1000
    elapsed_sec = elapsed_ms / 1000

    assert elapsed_sec < 1.0, f"Health response took {elapsed_sec:.2f}s, expected < 1.0s"
    print(f"✓ test_health_response_time passed ({elapsed_ms:.0f}ms)")


def test_no_large_assets():
    """Verify no single asset exceeds 5MB during page load."""
    max_asset_size = 5_000_000  # 5MB in bytes
    assets = []

    def handle_response(response):
        """Callback to track response headers."""
        content_length = response.headers.get("content-length")
        if content_length:
            try:
                size = int(content_length)
                assets.append({
                    "url": response.url,
                    "status": response.status,
                    "size": size
                })
            except ValueError:
                pass

    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        page.on("response", handle_response)

        start_time = time.time()
        page.goto(BASE_URL)
        page.wait_for_load_state("networkidle")
        elapsed_ms = (time.time() - start_time) * 1000

        browser.close()

    # Check for oversized assets
    oversized = [a for a in assets if a["size"] > max_asset_size]
    assert not oversized, (
        f"Found {len(oversized)} asset(s) exceeding 5MB: "
        f"{[a['url'] for a in oversized]}"
    )

    print(f"✓ test_no_large_assets passed ({elapsed_ms:.0f}ms, {len(assets)} assets tracked)")


if __name__ == "__main__":
    failures = 0

    tests = [
        test_page_load_time,
        test_health_response_time,
        test_no_large_assets,
    ]

    for test_func in tests:
        try:
            test_func()
        except Exception as e:
            print(f"✗ {test_func.__name__} failed: {e}")
            failures += 1

    print(f"\nResults: {len(tests) - failures}/{len(tests)} passed")
    sys.exit(failures)
