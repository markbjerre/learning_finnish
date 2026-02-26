"""
Migration script: Add 'degree' column to inflections table.
Supports adjective comparative/superlative inflections.

Usage:
    cd backend
    python scripts/migrate_inflection_degree.py

    # Use SQLite (for local testing without PostgreSQL):
    python scripts/migrate_inflection_degree.py --use-sqlite
"""
import argparse
import asyncio
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

parser = argparse.ArgumentParser()
parser.add_argument("--use-sqlite", action="store_true", help="Use SQLite instead of PostgreSQL")
args, _ = parser.parse_known_args()

from dotenv import load_dotenv
load_dotenv(os.path.join(os.path.dirname(os.path.dirname(__file__)), ".env"))
if args.use_sqlite:
    os.environ["DATABASE_URL"] = ""

from sqlalchemy import text
from app.database import engine, APP_SCHEMA
from app.config import settings

SCHEMA = APP_SCHEMA


async def migrate():
    async with engine.begin() as conn:
        is_postgres = "postgresql" in (settings.database_url or "")

        # 1. Add degree column to inflections
        try:
            if is_postgres:
                await conn.execute(
                    text(
                        f'ALTER TABLE "{SCHEMA}"."inflections" '
                        'ADD COLUMN IF NOT EXISTS "degree" VARCHAR(50)'
                    )
                )
            else:
                result = await conn.execute(text("PRAGMA table_info(inflections)"))
                cols = [row[1] for row in result.fetchall()]
                if "degree" not in cols:
                    await conn.execute(
                        text('ALTER TABLE inflections ADD COLUMN "degree" VARCHAR(50)')
                    )
            print("  [OK] Added column inflections.degree")
        except Exception as e:
            print(f"  - Column inflections.degree skipped: {e}")

        print("\nMigration complete.")


if __name__ == "__main__":
    asyncio.run(migrate())
