"""
Seed script: Pre-populate 30 Finnish grammatical concepts and create 3 demo users
with randomized concept progress and word associations.

Usage:
    cd backend
    python scripts/seed_concepts_and_users.py
    python scripts/seed_concepts_and_users.py --use-sqlite
"""
import argparse
import asyncio
import json
import os
import random
import sys
import uuid

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

parser = argparse.ArgumentParser()
parser.add_argument("--use-sqlite", action="store_true", help="Use SQLite instead of PostgreSQL")
parser.add_argument("--force", action="store_true", help="Re-seed even if concepts already exist")
args, _ = parser.parse_known_args()

from dotenv import load_dotenv
load_dotenv(os.path.join(os.path.dirname(os.path.dirname(__file__)), ".env"))
if args.use_sqlite:
    os.environ["DATABASE_URL"] = ""

from sqlalchemy import select, func
from app.database import async_session, init_db
from app.models_db import Concept, User, UserWord, UserConceptProgress, Word

# (name, name_fi, description, frequency 1-5, difficulty 1-5, tags)
FINNISH_CONCEPTS = [
    # --- Cases (15) ---
    ("Nominative case", "Nominatiivi",
     "Basic/subject form: koira (dog). Used for subjects and predicatives.",
     5, 1, ["case", "basic"]),
    ("Genitive case", "Genetiivi",
     "Possession/ownership, -n ending: koiran (dog's). Also used with postpositions.",
     5, 2, ["case"]),
    ("Partitive case", "Partitiivi",
     "Partial quantity, negation, -a/-\u00e4/-ta/-t\u00e4: koiraa. One of the most-used cases.",
     5, 4, ["case", "core"]),
    ("Accusative case", "Akkusatiivi",
     "Total/definite object, resembles nominative or genitive depending on context.",
     4, 3, ["case"]),
    ("Inessive case", "Inessiivi",
     "Inside something, -ssa/-ss\u00e4: talossa (in the house).",
     4, 2, ["case", "locative"]),
    ("Elative case", "Elatiivi",
     "Out of something, -sta/-st\u00e4: talosta (from the house).",
     4, 2, ["case", "locative"]),
    ("Illative case", "Illatiivi",
     "Into something, -Vn/-seen/-hin: taloon (into the house). Complex stem changes.",
     4, 3, ["case", "locative"]),
    ("Adessive case", "Adessiivi",
     "On/at surface, possession, -lla/-ll\u00e4: p\u00f6yd\u00e4ll\u00e4 (on the table).",
     4, 2, ["case", "locative"]),
    ("Ablative case", "Ablatiivi",
     "From surface/possession, -lta/-lt\u00e4: p\u00f6yd\u00e4lt\u00e4 (from the table).",
     3, 3, ["case", "locative"]),
    ("Allative case", "Allatiivi",
     "Onto/towards, -lle: p\u00f6yd\u00e4lle (onto the table). Also for recipients.",
     4, 2, ["case", "locative"]),
    ("Essive case", "Essiivi",
     "State/role/time, -na/-n\u00e4: opettajana (as a teacher), maanantaina (on Monday).",
     3, 3, ["case"]),
    ("Translative case", "Translatiivi",
     "Becoming/changing into, -ksi: opettajaksi (becoming a teacher).",
     3, 3, ["case"]),
    ("Abessive case", "Abessiivi",
     "Without, -tta/-tt\u00e4: rahatta (without money). Rare in speech.",
     1, 4, ["case", "rare"]),
    ("Comitative case", "Komitatiivi",
     "Together with (plural only), -ine + possessive: lapsineen (with one's children).",
     1, 5, ["case", "rare"]),
    ("Instructive case", "Instruktiivi",
     "By means of (frozen expressions), -in: omin silmin (with one's own eyes).",
     1, 5, ["case", "rare"]),

    # --- Verb forms (8) ---
    ("Verb type classification", "Verbityyppi",
     "Six verb types based on infinitive ending (-aa, -da, -la/na/ra, -ta, -ita, -eta). Determines conjugation pattern.",
     5, 2, ["verb"]),
    ("Present tense", "Preesens",
     "Current/habitual actions: min\u00e4 puhun (I speak), sin\u00e4 puhut (you speak).",
     5, 1, ["verb", "tense"]),
    ("Past tense (imperfect)", "Imperfekti",
     "Simple past: min\u00e4 puhuin (I spoke). Uses -i- marker with stem changes.",
     5, 2, ["verb", "tense"]),
    ("Perfect tense", "Perfekti",
     "Completed past: olen puhunut (I have spoken). Uses olla + past participle.",
     4, 3, ["verb", "tense"]),
    ("Conditional mood", "Konditionaali",
     "Would/hypothetical: puhuisin (I would speak). Uses -isi- marker.",
     3, 3, ["verb", "mood"]),
    ("Passive voice", "Passiivi",
     "Impersonal: puhutaan (one speaks / it is spoken). Common in colloquial 'we' form.",
     4, 3, ["verb"]),
    ("Negative verb", "Kieltomuoto",
     "ei conjugates by person, main verb in stem form: en puhu, et puhu, ei puhu.",
     5, 2, ["verb"]),
    ("Imperative mood", "Imperatiivi",
     "Commands: puhu! (speak!), puhukaa! (speak! plural/formal).",
     3, 2, ["verb", "mood"]),

    # --- Other grammar (7) ---
    ("Consonant gradation", "Astevaihtelu",
     "Stem consonant alternation: pp\u2192p, tt\u2192t, kk\u2192k (strong\u2192weak). Affects nouns and verbs.",
     5, 4, ["phonology", "core"]),
    ("Vowel harmony", "Vokaaliharmonia",
     "Back vowels (a,o,u) and front vowels (\u00e4,\u00f6,y) cannot mix in suffixes. e,i are neutral.",
     5, 2, ["phonology"]),
    ("Possessive suffixes", "Omistusliitteet",
     "-ni (my), -si (your), -nsa (his/her): taloni (my house). Often replaces genitive pronoun.",
     3, 3, ["morphology"]),
    ("Sentence negation", "Kieltolause",
     "Negative auxiliary ei conjugates; main verb stays in stem form. Min\u00e4 en puhu suomea.",
     4, 2, ["syntax"]),
    ("Question formation", "Kysymyslause",
     "-ko/-k\u00f6 suffix on first element: Puhutko suomea? (Do you speak Finnish?)",
     4, 2, ["syntax"]),
    ("Postpositions", "Postpositiot",
     "Come after genitive noun: talon edess\u00e4 (in front of the house). More common than prepositions.",
     3, 3, ["syntax"]),
    ("Plural formation", "Monikon muodostaminen",
     "Nominative plural -t: koirat (dogs). Oblique plural stem differs from singular (complex rules).",
     5, 3, ["morphology", "core"]),
]

DEMO_USERS = [
    ("user-demo-1", "demo1@example.com", "Demo_Beginner"),
    ("user-demo-2", "demo2@example.com", "Demo_Intermediate"),
    ("user-demo-3", "demo3@example.com", "Demo_Advanced"),
]


async def seed():
    await init_db()

    async with async_session() as db:
        # --- Check existing concepts ---
        count_result = await db.execute(select(func.count(Concept.id)))
        existing_count = count_result.scalar() or 0

        if existing_count > 0 and not args.force:
            print(f"  Found {existing_count} existing concepts. Use --force to re-seed.")
        else:
            if existing_count > 0:
                print(f"  --force: deleting {existing_count} existing concepts...")
                from sqlalchemy import delete
                await db.execute(delete(UserConceptProgress))
                await db.execute(delete(Concept))
                await db.commit()

            # --- Seed concepts ---
            concept_ids = []
            for i, (name, name_fi, desc, freq, diff, tags) in enumerate(FINNISH_CONCEPTS, 1):
                cid = f"concept-{i:02d}"
                concept = Concept(
                    id=cid,
                    name=name,
                    name_fi=name_fi,
                    description=desc,
                    frequency=freq,
                    difficulty=diff,
                    tags=json.dumps(tags),
                    priority=1.0,
                )
                db.add(concept)
                concept_ids.append(cid)
            await db.commit()
            print(f"  [OK] Seeded {len(FINNISH_CONCEPTS)} grammatical concepts")

        # Fetch concept IDs for user progress seeding
        concept_result = await db.execute(select(Concept.id))
        all_concept_ids = [row[0] for row in concept_result.fetchall()]

        # --- Fetch existing words for UserWord associations ---
        word_result = await db.execute(select(Word.id))
        all_word_ids = [row[0] for row in word_result.fetchall()]
        print(f"  Found {len(all_word_ids)} words for user associations")

        # --- Seed demo users ---
        for user_id, email, username in DEMO_USERS:
            # Check if user exists
            existing = await db.execute(select(User).where(User.id == user_id))
            if existing.scalars().first():
                print(f"  User {username} already exists, skipping creation")
                continue

            user = User(id=user_id, email=email, username=username)
            db.add(user)

            # Randomized concept progress: 15-25 concepts
            n_concepts = random.randint(15, min(25, len(all_concept_ids)))
            chosen_concepts = random.sample(all_concept_ids, n_concepts)
            for cid in chosen_concepts:
                # Scale mastery by user "level"
                if username == "Demo_Beginner":
                    mastery = round(random.uniform(0.1, 3.0), 2)
                    ex_count = random.randint(2, 30)
                elif username == "Demo_Intermediate":
                    mastery = round(random.uniform(1.5, 6.5), 2)
                    ex_count = random.randint(15, 65)
                else:  # Advanced
                    mastery = round(random.uniform(4.0, 9.0), 2)
                    ex_count = random.randint(40, 90)

                progress = UserConceptProgress(
                    id=str(uuid.uuid4()),
                    user_id=user_id,
                    concept_id=cid,
                    mastery=mastery,
                    exercise_count=ex_count,
                )
                db.add(progress)

            # Randomized word associations
            if all_word_ids:
                if username == "Demo_Beginner":
                    n_words = random.randint(10, min(20, len(all_word_ids)))
                elif username == "Demo_Intermediate":
                    n_words = random.randint(25, min(40, len(all_word_ids)))
                else:
                    n_words = min(len(all_word_ids), random.randint(40, 60))

                chosen_words = random.sample(all_word_ids, n_words)
                for wid in chosen_words:
                    if username == "Demo_Beginner":
                        proficiency = random.randint(0, 30)
                    elif username == "Demo_Intermediate":
                        proficiency = random.randint(20, 65)
                    else:
                        proficiency = random.randint(50, 95)

                    uw = UserWord(
                        id=str(uuid.uuid4()),
                        user_id=user_id,
                        word_id=wid,
                        status="RECENT" if proficiency < 25 else ("LEARNING" if proficiency < 70 else "MASTERED"),
                        proficiency=proficiency,
                        review_count=random.randint(0, ex_count),
                    )
                    db.add(uw)

            print(f"  [OK] Created user {username} with {n_concepts} concept progress + {n_words if all_word_ids else 0} words")

        await db.commit()
        print("\nSeed complete.")


if __name__ == "__main__":
    asyncio.run(seed())
