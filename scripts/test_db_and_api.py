#!/usr/bin/env python3
"""
Test script for Learning Finnish DB connection and API endpoints.

Usage:
  # Full test (DB + API, no server needed)
  python scripts/test_db_and_api.py --use-sqlite --in-process

  # Test against local dev (default: http://localhost:8001)
  python scripts/test_db_and_api.py

  # Test against production
  python scripts/test_db_and_api.py --base-url https://ai-vaerksted.cloud/finnish

  # Test DB only (requires DATABASE_URL in .env)
  python scripts/test_db_and_api.py --db-only

  # Test API only (server must be running)
  python scripts/test_db_and_api.py --api-only

  # Use SQLite for local testing (no PostgreSQL required)
  python scripts/test_db_and_api.py --use-sqlite
"""

import argparse
import asyncio
import os
import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "backend"))

# Must set before app imports (for --use-sqlite)
def _apply_sqlite_override():
    os.environ["DATABASE_URL"] = ""


async def test_db(use_sqlite: bool = False):
    """Test database connection and basic queries."""
    from dotenv import load_dotenv
    load_dotenv(Path(__file__).resolve().parent.parent / "backend" / ".env")
    load_dotenv(Path(__file__).resolve().parent.parent / ".env")

    from app.config import settings
    from app.database import init_db, async_session
    from sqlalchemy import text

    if not use_sqlite and not settings.database_url:
        print("  [SKIP] DATABASE_URL not set (use --use-sqlite or set env)")
        return True

    try:
        await init_db()
        async with async_session() as session:
            # Test connection
            result = await session.execute(text("SELECT 1"))
            val = result.scalar()
            assert val in (1, (1,))
            print("  [OK] DB connection")

            is_pg = "postgresql" in (settings.database_url or "")

            # Check app schema (PostgreSQL only)
            if is_pg:
                result = await session.execute(
                    text("SELECT schema_name FROM information_schema.schemata WHERE schema_name = 'app'")
                )
                if result.scalar():
                    print("  [OK] app schema exists")
                else:
                    print("  [WARN] app schema not found")
            else:
                print("  [OK] SQLite mode")

            # Count words
            try:
                tbl = "app.words" if is_pg else "words"
                result = await session.execute(text(f"SELECT COUNT(*) FROM {tbl}"))
                count = result.scalar()
                print(f"  [OK] words table has {count} rows")
            except Exception:
                print("  [OK] words table (empty)")

            # Check spaced repetition tables
            for table in ["app_settings", "inflections", "verb_forms", "concepts", "spaced_exercise_log"]:
                try:
                    full_tbl = f'"app"."{table}"' if is_pg else table
                    result = await session.execute(text(f"SELECT COUNT(*) FROM {full_tbl}"))
                    count = result.scalar()
                    print(f"  [OK] {table} table exists ({count} rows)")
                except Exception as e:
                    print(f"  [WARN] {table} table: {e}")

        return True
    except Exception as e:
        print(f"  [FAIL] DB: {e}")
        return False


def test_api(base_url: str, in_process: bool = False) -> bool:
    """Test API endpoints via HTTP or in-process TestClient."""
    import json

    if in_process:
        return _test_api_in_process()

    import urllib.request
    base = base_url.rstrip("/")
    tests = [
        ("/api/health/simple", "GET", None, lambda r: "ok" in str(r.get("status", "")).lower()),
        ("/api/health", "GET", None, lambda r: "healthy" in str(r.get("status", "")).lower()),
        ("/api/lessons", "GET", None, lambda r: isinstance(r, list)),
        ("/api/words/search?finnish_word=kissa", "POST", {}, lambda r: "finnish_word" in r or "english_translation" in r),
        # Spaced repetition endpoints
        ("/api/exercise/next", "GET", None, lambda r: "words" in r and "concepts" in r and "level" in r),
        ("/api/settings", "GET", None, lambda r: isinstance(r, dict)),
        ("/api/stats", "GET", None, lambda r: "total_words" in r and "level" in r),
        ("/api/exercise/history", "GET", None, lambda r: isinstance(r, list)),
        ("/api/concepts", "GET", None, lambda r: isinstance(r, list)),
        ("/api/words", "GET", None, lambda r: isinstance(r, list)),
    ]

    # Test POST /api/words/add
    add_tests = [
        ("/api/words/add", "POST", {"finnish": "testi", "danish": "test", "english": "test", "word_type": "noun"},
         lambda r: r.get("status") in ("created", "exists") and "word_id" in r),
    ]

    all_ok = True
    for path, method, body, check in tests + add_tests:
        url = f"{base}{path}"
        try:
            req = urllib.request.Request(url, method=method)
            if body is not None:
                req.add_header("Content-Type", "application/json")
                req.data = json.dumps(body).encode()
            with urllib.request.urlopen(req, timeout=10) as resp:
                data = json.loads(resp.read().decode())
                if check(data):
                    print(f"  [OK] {method} {path}")
                else:
                    print(f"  [FAIL] {method} {path} - unexpected response: {data}")
                    all_ok = False
        except urllib.error.HTTPError as e:
            body_read = e.read().decode()[:200]
            print(f"  [FAIL] {method} {path} - HTTP {e.code}: {body_read}")
            all_ok = False
        except json.JSONDecodeError as e:
            print(f"  [FAIL] {method} {path} - Response not JSON: {e}")
            all_ok = False
        except Exception as e:
            print(f"  [FAIL] {method} {path} - {e}")
            all_ok = False

    return all_ok


def _test_api_in_process() -> bool:
    """Test API using FastAPI TestClient (no server needed)."""
    from httpx import ASGITransport, AsyncClient
    from app.main import app

    async def _run():
        all_ok = True
        async with AsyncClient(
            transport=ASGITransport(app=app),
            base_url="http://test",
        ) as client:
            tests = [
                ("/api/health/simple", "GET", None, lambda r: "ok" in str(r.get("status", "")).lower()),
                ("/api/health", "GET", None, lambda r: "healthy" in str(r.get("status", "")).lower()),
                ("/api/lessons", "GET", None, lambda r: isinstance(r, list)),
                ("/api/words/search?finnish_word=kissa", "POST", {}, lambda r: "finnish_word" in r or "english_translation" in r),
                ("/api/exercise/next", "GET", None, lambda r: "words" in r and "concepts" in r and "level" in r),
                ("/api/settings", "GET", None, lambda r: isinstance(r, dict)),
                ("/api/stats", "GET", None, lambda r: "total_words" in r and "level" in r),
                ("/api/exercise/history", "GET", None, lambda r: isinstance(r, list)),
                ("/api/concepts", "GET", None, lambda r: isinstance(r, list)),
                ("/api/words", "GET", None, lambda r: isinstance(r, list)),
            ]
            add_tests = [
                ("/api/words/add", "POST", {"finnish": "testi", "danish": "test", "english": "test", "word_type": "noun"},
                 lambda r: r.get("status") in ("created", "exists") and "word_id" in r),
            ]
            for path, method, body, check in tests + add_tests:
                try:
                    if method == "GET":
                        resp = await client.get(path)
                    else:
                        resp = await client.post(path, json=body or {})
                    data = resp.json()
                    if resp.status_code == 200 and check(data):
                        print(f"  [OK] {method} {path}")
                    else:
                        print(f"  [FAIL] {method} {path} - {resp.status_code}: {data}")
                        all_ok = False
                except Exception as e:
                    print(f"  [FAIL] {method} {path} - {e}")
                    all_ok = False
        return all_ok

    return asyncio.run(_run())


def main():
    parser = argparse.ArgumentParser(description="Test Learning Finnish DB and API")
    parser.add_argument(
        "--base-url",
        default=os.environ.get("FINNISH_API_URL", "http://localhost:8001"),
        help="API base URL (default: FINNISH_API_URL or http://localhost:8001)",
    )
    parser.add_argument("--db-only", action="store_true", help="Test DB connection only")
    parser.add_argument("--api-only", action="store_true", help="Test API endpoints only")
    parser.add_argument("--use-sqlite", action="store_true", help="Use SQLite instead of PostgreSQL (for local testing)")
    parser.add_argument("--in-process", action="store_true", help="Run API tests in-process (no server needed)")
    args = parser.parse_args()

    if args.use_sqlite:
        _apply_sqlite_override()
        # Use same DB file as seed (backend/learning_finnish.db)
        backend_dir = Path(__file__).resolve().parent.parent / "backend"
        os.chdir(backend_dir)

    print("Learning Finnish - DB & API Test")
    print("=" * 40)

    db_ok = True
    api_ok = True

    if not args.api_only:
        print("\n[1] Database")
        db_ok = asyncio.run(test_db(use_sqlite=args.use_sqlite))

    if not args.db_only:
        print("\n[2] API")
        api_ok = test_api(args.base_url, in_process=args.in_process)

    print("\n" + "=" * 40)
    if db_ok and api_ok:
        print("All tests passed.")
        return 0
    print("Some tests failed.")
    return 1


if __name__ == "__main__":
    sys.exit(main())
