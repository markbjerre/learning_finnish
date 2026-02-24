#!/usr/bin/env python3
"""
API tests for Learning Finnish /api/words endpoints.

Tests:
  1. GET /api/words returns 200 and array (can be empty)
  2. POST /api/words/add with {"finnish":"testi","english":"test"} creates a word
  3. GET /api/words after add returns the new word

Usage:
  # Against running backend (default: http://localhost:8001)
  python scripts/test_api_words.py

  # Custom base URL
  python scripts/test_api_words.py --base-url http://localhost:8000

  # In-process (no server needed, uses SQLite)
  python scripts/test_api_words.py --in-process

  # Production
  python scripts/test_api_words.py --base-url https://ai-vaerksted.cloud/finnish
"""

import argparse
import asyncio
import os
import sys
from pathlib import Path

# Add backend to path for in-process mode
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "backend"))


def _apply_sqlite_override():
    """Use SQLite for in-process tests (no PostgreSQL required)."""
    os.environ["USE_SQLITE"] = "1"


async def _run_against_server(base_url: str) -> bool:
    """Run tests via httpx against a running backend."""
    import httpx

    base = base_url.rstrip("/")
    all_ok = True

    async with httpx.AsyncClient(timeout=10.0) as client:
        # Test 1: GET /api/words returns 200 and array (can be empty)
        try:
            resp = await client.get(f"{base}/api/words")
            if resp.status_code != 200:
                print(f"  [FAIL] GET /api/words - status {resp.status_code}")
                all_ok = False
            else:
                data = resp.json()
                if not isinstance(data, list):
                    print(f"  [FAIL] GET /api/words - expected array, got {type(data).__name__}")
                    all_ok = False
                else:
                    print("  [OK] GET /api/words returns 200 and array")
        except Exception as e:
            print(f"  [FAIL] GET /api/words - {e}")
            all_ok = False
            return all_ok  # Cannot continue if backend unreachable

        # Test 2: POST /api/words/add with {"finnish":"testi","english":"test"} creates a word
        try:
            resp = await client.post(
                f"{base}/api/words/add",
                json={"finnish": "testi", "english": "test"},
            )
            if resp.status_code != 200:
                print(f"  [FAIL] POST /api/words/add - status {resp.status_code}: {resp.text[:200]}")
                all_ok = False
            else:
                data = resp.json()
                status = data.get("status")
                if status not in ("created", "exists"):
                    print(f"  [FAIL] POST /api/words/add - unexpected status: {data}")
                    all_ok = False
                elif "word_id" not in data and status == "created":
                    print(f"  [FAIL] POST /api/words/add - missing word_id: {data}")
                    all_ok = False
                else:
                    print("  [OK] POST /api/words/add creates word (status=%s)" % status)
        except Exception as e:
            print(f"  [FAIL] POST /api/words/add - {e}")
            all_ok = False

        # Test 3: GET /api/words after add returns the new word
        try:
            resp = await client.get(f"{base}/api/words", params={"search": "testi"})
            if resp.status_code != 200:
                print(f"  [FAIL] GET /api/words?search=testi - status {resp.status_code}")
                all_ok = False
            else:
                data = resp.json()
                if not isinstance(data, list):
                    print(f"  [FAIL] GET /api/words - expected array, got {type(data).__name__}")
                    all_ok = False
                else:
                    found = next((w for w in data if w.get("finnish", "").lower() == "testi"), None)
                    if found is None:
                        print(f"  [FAIL] GET /api/words - 'testi' not in response (got {len(data)} items)")
                        all_ok = False
                    else:
                        print("  [OK] GET /api/words returns the new word")
        except Exception as e:
            print(f"  [FAIL] GET /api/words?search=testi - {e}")
            all_ok = False

    return all_ok


async def _run_in_process() -> bool:
    """Run tests in-process using FastAPI TestClient (no server needed)."""
    from httpx import ASGITransport, AsyncClient
    from app.main import app

    all_ok = True
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as client:
        # Test 1: GET /api/words returns 200 and array (can be empty)
        try:
            resp = await client.get("/api/words")
            if resp.status_code != 200:
                print(f"  [FAIL] GET /api/words - status {resp.status_code}")
                all_ok = False
            else:
                data = resp.json()
                if not isinstance(data, list):
                    print(f"  [FAIL] GET /api/words - expected array, got {type(data).__name__}")
                    all_ok = False
                else:
                    print("  [OK] GET /api/words returns 200 and array")
        except Exception as e:
            print(f"  [FAIL] GET /api/words - {e}")
            all_ok = False
            return all_ok

        # Test 2: POST /api/words/add with {"finnish":"testi","english":"test"} creates a word
        try:
            resp = await client.post(
                "/api/words/add",
                json={"finnish": "testi", "english": "test"},
            )
            if resp.status_code != 200:
                print(f"  [FAIL] POST /api/words/add - status {resp.status_code}: {resp.text[:200]}")
                all_ok = False
            else:
                data = resp.json()
                status = data.get("status")
                if status not in ("created", "exists"):
                    print(f"  [FAIL] POST /api/words/add - unexpected status: {data}")
                    all_ok = False
                elif "word_id" not in data and status == "created":
                    print(f"  [FAIL] POST /api/words/add - missing word_id: {data}")
                    all_ok = False
                else:
                    print("  [OK] POST /api/words/add creates word (status=%s)" % status)
        except Exception as e:
            print(f"  [FAIL] POST /api/words/add - {e}")
            all_ok = False

        # Test 3: GET /api/words after add returns the new word
        try:
            resp = await client.get("/api/words", params={"search": "testi"})
            if resp.status_code != 200:
                print(f"  [FAIL] GET /api/words?search=testi - status {resp.status_code}")
                all_ok = False
            else:
                data = resp.json()
                if not isinstance(data, list):
                    print(f"  [FAIL] GET /api/words - expected array, got {type(data).__name__}")
                    all_ok = False
                else:
                    found = next((w for w in data if w.get("finnish", "").lower() == "testi"), None)
                    if found is None:
                        print(f"  [FAIL] GET /api/words - 'testi' not in response (got {len(data)} items)")
                        all_ok = False
                    else:
                        print("  [OK] GET /api/words returns the new word")
        except Exception as e:
            print(f"  [FAIL] GET /api/words?search=testi - {e}")
            all_ok = False

    return all_ok


def main() -> int:
    parser = argparse.ArgumentParser(description="Test Learning Finnish /api/words API")
    parser.add_argument(
        "--base-url",
        default=os.environ.get("FINNISH_API_URL", "http://localhost:8001"),
        help="API base URL (default: FINNISH_API_URL or http://localhost:8001)",
    )
    parser.add_argument(
        "--in-process",
        action="store_true",
        help="Run in-process (no server needed, uses SQLite)",
    )
    args = parser.parse_args()

    if args.in_process:
        _apply_sqlite_override()
        backend_dir = Path(__file__).resolve().parent.parent / "backend"
        os.chdir(backend_dir)
        from dotenv import load_dotenv
        load_dotenv(backend_dir / ".env")
        load_dotenv(Path(__file__).resolve().parent.parent / ".env")

    print("Learning Finnish - API Words Test")
    print("=" * 40)
    if args.in_process:
        print("Mode: in-process (SQLite)")
    else:
        print("Mode: against running backend at", args.base_url)
        print("(Start backend with: ./scripts/dev-finnish.sh or uvicorn app.main:app)")
    print()

    ok = asyncio.run(_run_in_process() if args.in_process else _run_against_server(args.base_url))

    print()
    print("=" * 40)
    if ok:
        print("All tests passed.")
        return 0
    print("Some tests failed.")
    return 1


if __name__ == "__main__":
    sys.exit(main())
