"""
Backfill inflections for existing words that have none.

Usage:
    cd backend
    python scripts/backfill_inflections.py
    python scripts/backfill_inflections.py --word-type verb
    python scripts/backfill_inflections.py --dry-run
    python scripts/backfill_inflections.py --limit 10
    python scripts/backfill_inflections.py --use-sqlite
"""
import argparse
import asyncio
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

parser = argparse.ArgumentParser(description="Backfill inflections for words missing them")
parser.add_argument("--use-sqlite", action="store_true", help="Use SQLite instead of PostgreSQL")
parser.add_argument("--word-type", type=str, default=None, help="Only process words of this type (e.g. verb, noun, adjective)")
parser.add_argument("--dry-run", action="store_true", help="Show what would be done without making changes")
parser.add_argument("--limit", type=int, default=None, help="Max number of words to process")
parser.add_argument("--delay", type=float, default=1.0, help="Seconds between LLM calls (default: 1.0)")
args = parser.parse_args()

from dotenv import load_dotenv
load_dotenv(os.path.join(os.path.dirname(os.path.dirname(__file__)), ".env"))
if args.use_sqlite:
    os.environ["DATABASE_URL"] = ""

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import async_session, engine
from app.models_db import Word, Inflection, VerbForm
from app.services.inflection_service import generate_and_store_inflections


async def get_words_without_inflections(db: AsyncSession, word_type: str | None, limit: int | None) -> list[Word]:
    """Find words that have no inflections and no verb forms."""
    has_inflections = select(Inflection.word_id).distinct()
    has_verb_forms = select(VerbForm.word_id).distinct()

    stmt = (
        select(Word)
        .where(Word.id.notin_(has_inflections))
        .where(Word.id.notin_(has_verb_forms))
        .order_by(Word.finnish_word)
    )

    if word_type:
        stmt = stmt.where(func.lower(Word.part_of_speech) == word_type.lower())

    if limit:
        stmt = stmt.limit(limit)

    result = await db.execute(stmt)
    return list(result.scalars().all())


async def backfill():
    async with async_session() as db:
        words = await get_words_without_inflections(db, args.word_type, args.limit)

        total = len(words)
        if total == 0:
            print("No words need backfilling.")
            return

        type_filter = f" (type: {args.word_type})" if args.word_type else ""
        mode = " [DRY RUN]" if args.dry_run else ""
        print(f"Found {total} words without inflections{type_filter}{mode}\n")

        generated = 0
        skipped = 0
        errors = 0

        for i, word in enumerate(words, 1):
            pos = (word.part_of_speech or "unknown").lower()
            prefix = f"[{i}/{total}]"

            if args.dry_run:
                print(f"{prefix} Would generate inflections for \"{word.finnish_word}\" ({pos})")
                continue

            try:
                result = await generate_and_store_inflections(db, word)

                n_infl = result.get("inflections", 0)
                n_verb = result.get("verb_forms", 0)

                if n_infl + n_verb > 0:
                    print(f"{prefix} Generated {n_infl} inflections + {n_verb} verb forms for \"{word.finnish_word}\" ({pos})")
                    generated += 1
                else:
                    print(f"{prefix} Skipped \"{word.finnish_word}\" ({pos}) — non-inflecting or no AI configured")
                    skipped += 1

                if i < total:
                    await asyncio.sleep(args.delay)

            except Exception as e:
                print(f"{prefix} ERROR for \"{word.finnish_word}\": {e}")
                errors += 1

        print(f"\nDone. Generated: {generated}, Skipped: {skipped}, Errors: {errors}")


if __name__ == "__main__":
    asyncio.run(backfill())
