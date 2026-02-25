"""
Smoke tests — verify the FastAPI backend is up and healthy.

Run:
  python test_smoke.py
  API_BASE_URL=http://dobbybrain:8001 python test_smoke.py
"""
import sys
import json
import urllib.request
import urllib.error

sys.path.insert(0, ".")
from conftest import API_BASE


def test_health():
    """GET /health returns 200 with status=healthy."""
    url = f"{API_BASE}/health"
    with urllib.request.urlopen(url, timeout=5) as resp:
        assert resp.status == 200, f"/health returned {resp.status}"
        data = json.loads(resp.read())
        assert data["status"] == "healthy", f"Unexpected status: {data}"
    print(f"✓ test_health passed — {url}")


def test_health_simple():
    """GET /health/simple returns 200 with status=ok."""
    url = f"{API_BASE}/health/simple"
    with urllib.request.urlopen(url, timeout=5) as resp:
        assert resp.status == 200, f"/health/simple returned {resp.status}"
        data = json.loads(resp.read())
        assert data["status"] == "ok", f"Unexpected status: {data}"
    print(f"✓ test_health_simple passed — {url}")


if __name__ == "__main__":
    failures = 0
    for test in [test_health, test_health_simple]:
        try:
            test()
        except Exception as e:
            print(f"✗ {test.__name__} FAILED: {e}")
            failures += 1
    sys.exit(failures)
