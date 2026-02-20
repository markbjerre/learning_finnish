"""
Migration script: Add spaced repetition columns and tables.
Run once after deploying the updated models.

Usage:
    cd backend
    python scripts/migrate_spaced_repetition.py

    # Use SQLite (for local testing without PostgreSQL):
    python scripts/migrate_spaced_repetition.py --use-sqlite
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
        # Add new columns to words table (IF NOT EXISTS for PostgreSQL)
        columns_to_add = [
            ("danish_translation", "VARCHAR(255)"),
            ("tags", "TEXT"),
            ("priority", "FLOAT DEFAULT 1.0"),
            ("times_served", "INTEGER DEFAULT 0"),
            ("total_score", "FLOAT DEFAULT 0.0"),
            ("last_score", "FLOAT"),
            ("last_served", "TIMESTAMPTZ"),
        ]

        is_postgres = "postgresql" in (settings.database_url or "")

        for col_name, col_type in columns_to_add:
            try:
                if is_postgres:
                    await conn.execute(
                        text(
                            f'ALTER TABLE "{SCHEMA}"."words" ADD COLUMN IF NOT EXISTS "{col_name}" {col_type}'
                        )
                    )
                else:
                    # SQLite: check if column exists
                    result = await conn.execute(
                        text("PRAGMA table_info(words)")
                    )
                    cols = [row[1] for row in result.fetchall()]
                    if col_name not in cols:
                        await conn.execute(
                            text(f'ALTER TABLE words ADD COLUMN "{col_name}" {col_type}')
                        )
                print(f"  [OK] Added column words.{col_name}")
            except Exception as e:
                print(f"  - Column words.{col_name} skipped: {e}")

        # Create index on priority
        try:
            if is_postgres:
                await conn.execute(
                    text(
                        f'CREATE INDEX IF NOT EXISTS idx_words_priority ON "{SCHEMA}"."words" (priority DESC)'
                    )
                )
            else:
                await conn.execute(
                    text("CREATE INDEX IF NOT EXISTS idx_words_priority ON words (priority DESC)")
                )
            print("  [OK] Created index idx_words_priority")
        except Exception as e:
            print(f"  - Index skipped: {e}")

        # Create app_settings table if not exists (for inserting defaults before init_db)
        try:
            if is_postgres:
                await conn.execute(
                    text(
                        f'CREATE TABLE IF NOT EXISTS "{SCHEMA}"."app_settings" '
                        '(key VARCHAR(255) PRIMARY KEY, value TEXT NOT NULL)'
                    )
                )
            else:
                await conn.execute(
                    text(
                        "CREATE TABLE IF NOT EXISTS app_settings "
                        "(key VARCHAR(255) PRIMARY KEY, value TEXT NOT NULL)"
                    )
                )
            print("  [OK] app_settings table ready")
        except Exception as e:
            print(f"  - app_settings table: {e}")

        # Insert default settings
        defaults = [
            ("level", "15"),
            ("exercise_word_count", "5"),
            ("random_ratio", "0.25"),
        ]
        for key, value in defaults:
            try:
                if is_postgres:
                    await conn.execute(
                        text(
                            f"""INSERT INTO "{SCHEMA}"."app_settings" (key, value)
                                VALUES (:key, :value)
                                ON CONFLICT (key) DO NOTHING"""
                        ),
                        {"key": key, "value": value},
                    )
                else:
                    await conn.execute(
                        text(
                            """INSERT OR IGNORE INTO app_settings (key, value)
                                VALUES (:key, :value)"""
                        ),
                        {"key": key, "value": value},
                    )
                print(f"  [OK] Setting {key} = {value}")
            except Exception as e:
                print(f"  - Setting {key} skipped: {e}")

        print("\nMigration complete. Start the app to create new tables via init_db().")


if __name__ == "__main__":
    asyncio.run(migrate())
