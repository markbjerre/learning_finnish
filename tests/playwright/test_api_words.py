"""
API tests for the words endpoints.

Tests GET /words, POST /words/search, POST /words/add
Does not require data to exist — tests structure and status codes.

Run:
  python test_api_words.py
  API_BASE_URL=http://dobbybrain:8001 python test_api_words.py
"""
import sys
import json
import urllib.request
import urllib.error

sys.path.insert(0, ".")
from conftest import API_BASE


def _post(path, body):
    url = f"{API_BASE}{path}"
    data = json.dumps(body).encode()
    req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            return resp.status, json.loads(resp.read())
    except urllib.error.HTTPError as e:
        return e.code, json.loads(e.read())


def _get(path):
    url = f"{API_BASE}{path}"
    try:
        with urllib.request.urlopen(url, timeout=10) as resp:
            return resp.status, json.loads(resp.read())
    except urllib.error.HTTPError as e:
        return e.code, json.loads(e.read())


def test_get_words():
    """GET /words returns 200 with a list."""
    status, data = _get("/words")
    assert status == 200, f"GET /words returned {status}: {data}"
    assert isinstance(data, list), f"Expected list, got {type(data)}"
    print(f"✓ test_get_words passed ({len(data)} words)")


def test_search_words():
    """POST /words/search returns 200 with results structure."""
    status, data = _post("/words/search", {"query": "talo", "limit": 5})
    assert status == 200, f"POST /words/search returned {status}: {data}"
    assert "results" in data or isinstance(data, list), f"Unexpected shape: {data}"
    print(f"✓ test_search_words passed")


def test_add_word_validation():
    """POST /words/add with missing fields returns 422 (validation error)."""
    status, data = _post("/words/add", {})
    assert status == 422, f"Expected 422 validation error, got {status}: {data}"
    print(f"✓ test_add_word_validation passed (got expected 422)")


if __name__ == "__main__":
    failures = 0
    for test in [test_get_words, test_search_words, test_add_word_validation]:
        try:
            test()
        except Exception as e:
            print(f"✗ {test.__name__} FAILED: {e}")
            failures += 1
    sys.exit(failures)
