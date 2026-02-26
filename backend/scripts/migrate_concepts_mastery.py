"""
Migration: Add name_fi, frequency, difficulty to concepts table.
Create user_concept_progress table.

Usage:
    cd backend
    python scripts/migrate_concepts_mastery.py
    python scripts/migrate_concepts_mastery.py --use-sqlite
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

        # 1. Add name_fi column to concepts
        for col_name, col_type in [
            ("name_fi", "VARCHAR(255)"),
            ("frequency", "INTEGER"),
            ("difficulty", "INTEGER"),
        ]:
            try:
                if is_postgres:
                    await conn.execute(
                        text(
                            f'ALTER TABLE "{SCHEMA}"."concepts" '
                            f'ADD COLUMN IF NOT EXISTS "{col_name}" {col_type}'
                        )
                    )
                else:
                    result = await conn.execute(text("PRAGMA table_info(concepts)"))
                    cols = [row[1] for row in result.fetchall()]
                    if col_name not in cols:
                        await conn.execute(
                            text(f'ALTER TABLE concepts ADD COLUMN "{col_name}" {col_type}')
                        )
                print(f"  [OK] Added column concepts.{col_name}")
            except Exception as e:
                print(f"  - Column concepts.{col_name} skipped: {e}")

        # 2. Create user_concept_progress table
        try:
            if is_postgres:
                await conn.execute(text(f"""
                    CREATE TABLE IF NOT EXISTS "{SCHEMA}"."user_concept_progress" (
                        id VARCHAR PRIMARY KEY,
                        user_id VARCHAR NOT NULL REFERENCES "{SCHEMA}"."users"(id) ON DELETE CASCADE,
                        concept_id VARCHAR NOT NULL REFERENCES "{SCHEMA}"."concepts"(id) ON DELETE CASCADE,
                        mastery FLOAT DEFAULT 0.0,
                        exercise_count INTEGER DEFAULT 0,
                        last_exercised TIMESTAMPTZ,
                        created_at TIMESTAMPTZ DEFAULT NOW(),
                        CONSTRAINT uq_user_concept UNIQUE (user_id, concept_id)
                    )
                """))
                await conn.execute(text(
                    f'CREATE INDEX IF NOT EXISTS ix_ucp_user_id ON "{SCHEMA}"."user_concept_progress" (user_id)'
                ))
                await conn.execute(text(
                    f'CREATE INDEX IF NOT EXISTS ix_ucp_concept_id ON "{SCHEMA}"."user_concept_progress" (concept_id)'
                ))
            else:
                await conn.execute(text("""
                    CREATE TABLE IF NOT EXISTS user_concept_progress (
                        id VARCHAR PRIMARY KEY,
                        user_id VARCHAR NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                        concept_id VARCHAR NOT NULL REFERENCES concepts(id) ON DELETE CASCADE,
                        mastery FLOAT DEFAULT 0.0,
                        exercise_count INTEGER DEFAULT 0,
                        last_exercised TIMESTAMP,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        UNIQUE (user_id, concept_id)
                    )
                """))
            print("  [OK] Created table user_concept_progress")
        except Exception as e:
            print(f"  - Table user_concept_progress skipped: {e}")

        print("\nMigration complete.")


if __name__ == "__main__":
    asyncio.run(migrate())
