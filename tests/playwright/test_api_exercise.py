"""
API tests for the exercise endpoints (used by OpenClaw).

Tests GET /exercise/next, POST /exercise/result, GET /exercise/history

Run:
  python test_api_exercise.py
  API_BASE_URL=http://dobbybrain:8001 python test_api_exercise.py
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


def test_exercise_next():
    """GET /exercise/next returns 200 with words, concepts, and level."""
    status, data = _get("/exercise/next")
    assert status == 200, f"GET /exercise/next returned {status}: {data}"
    assert "words" in data, f"Missing 'words' key: {data}"
    assert "level" in data, f"Missing 'level' key: {data}"
    print(f"✓ test_exercise_next passed (level={data.get('level')}, words={len(data.get('words', []))})")


def test_exercise_history():
    """GET /exercise/history returns 200 with a list."""
    status, data = _get("/exercise/history")
    assert status == 200, f"GET /exercise/history returned {status}: {data}"
    assert isinstance(data, list), f"Expected list, got {type(data)}"
    print(f"✓ test_exercise_history passed ({len(data)} entries)")


def test_exercise_result_validation():
    """POST /exercise/result with empty body returns 200 (graceful with defaults)."""
    status, data = _post("/exercise/result", {})
    assert status in (200, 422), f"Unexpected status {status}: {data}"
    print(f"✓ test_exercise_result_validation passed (status={status})")


if __name__ == "__main__":
    failures = 0
    for test in [test_exercise_next, test_exercise_history, test_exercise_result_validation]:
        try:
            test()
        except Exception as e:
            print(f"✗ {test.__name__} FAILED: {e}")
            failures += 1
    sys.exit(failures)
