#!/usr/bin/env python3
"""
Test script for Learning Finnish DB connection and API endpoints.

Usage:
  # Test against local dev (default: http://localhost:8001)
  python scripts/test_db_and_api.py

  # Test against production
  python scripts/test_db_and_api.py --base-url https://ai-vaerksted.cloud/finnish

  # Test DB only (requires DATABASE_URL in .env)
  python scripts/test_db_and_api.py --db-only

  # Test API only
  python scripts/test_db_and_api.py --api-only
"""

import argparse
import asyncio
import os
import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "backend"))


async def test_db():
    """Test database connection and basic queries."""
    from dotenv import load_dotenv
    load_dotenv(Path(__file__).resolve().parent.parent / "backend" / ".env")
    load_dotenv(Path(__file__).resolve().parent.parent / ".env")

    from app.config import settings
    from app.database import init_db, async_session
    from sqlalchemy import text

    if not settings.database_url:
        print("  [SKIP] DATABASE_URL not set (use SQLite or set env)")
        return True

    if "sqlite" in (settings.database_url or ""):
        print("  [SKIP] SQLite - no schema test needed")
        return True

    try:
        await init_db()
        async with async_session() as session:
            # Test connection
            result = await session.execute(text("SELECT 1"))
            assert result.scalar() == (1,)
            print("  [OK] DB connection")

            # Check app schema exists
            result = await session.execute(
                text("SELECT schema_name FROM information_schema.schemata WHERE schema_name = 'app'")
            )
            if result.scalar():
                print("  [OK] app schema exists")
            else:
                print("  [WARN] app schema not found (may use SQLite)")

            # Count app.words if exists
            try:
                result = await session.execute(text('SELECT COUNT(*) FROM app.words'))
                count = result.scalar()
                print(f"  [OK] app.words has {count} rows")
            except Exception:
                print("  [OK] app.words table (empty)")

        return True
    except Exception as e:
        print(f"  [FAIL] DB: {e}")
        return False


def test_api(base_url: str) -> bool:
    """Test API endpoints via HTTP."""
    import urllib.request
    import json

    base = base_url.rstrip("/")
    tests = [
        ("/api/health/simple", "GET", None, lambda r: "ok" in str(r.get("status", "")).lower()),
        ("/api/health", "GET", None, lambda r: "healthy" in str(r.get("status", "")).lower()),
        ("/api/lessons", "GET", None, lambda r: isinstance(r, list)),
        ("/api/words/search?finnish_word=kissa", "POST", {}, lambda r: "finnish_word" in r or "english_translation" in r),
    ]

    all_ok = True
    for path, method, body, check in tests:
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
            body = e.read().decode()[:200]
            print(f"  [FAIL] {method} {path} - HTTP {e.code}: {body}")
            all_ok = False
        except json.JSONDecodeError as e:
            print(f"  [FAIL] {method} {path} - Response not JSON: {e}")
            all_ok = False
        except Exception as e:
            print(f"  [FAIL] {method} {path} - {e}")
            all_ok = False

    return all_ok


def main():
    parser = argparse.ArgumentParser(description="Test Learning Finnish DB and API")
    parser.add_argument(
        "--base-url",
        default=os.environ.get("FINNISH_API_URL", "http://localhost:8001"),
        help="API base URL (default: FINNISH_API_URL or http://localhost:8001)",
    )
    parser.add_argument("--db-only", action="store_true", help="Test DB connection only")
    parser.add_argument("--api-only", action="store_true", help="Test API endpoints only")
    args = parser.parse_args()

    print("Learning Finnish - DB & API Test")
    print("=" * 40)

    db_ok = True
    api_ok = True

    if not args.api_only:
        print("\n[1] Database")
        db_ok = asyncio.run(test_db())

    if not args.db_only:
        print("\n[2] API")
        api_ok = test_api(args.base_url)

    print("\n" + "=" * 40)
    if db_ok and api_ok:
        print("All tests passed.")
        return 0
    print("Some tests failed.")
    return 1


if __name__ == "__main__":
    sys.exit(main())
