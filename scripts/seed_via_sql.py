#!/usr/bin/env python3
"""Seed DB via raw SQL (bypasses ORM schema issues). Run inside container: python /app/seed_via_sql.py"""

import asyncio
import os
import sys
from pathlib import Path

script_dir = Path(__file__).resolve().parent
project_root = script_dir.parent
backend_dir = project_root / "backend"
sys.path.insert(0, str(backend_dir))
os.chdir(backend_dir)

from dotenv import load_dotenv
load_dotenv(backend_dir / ".env")
load_dotenv(project_root / ".env")

async def main():
    from app.database import engine
    from sqlalchemy import text

    sql = """
    CREATE SCHEMA IF NOT EXISTS app;
    CREATE TABLE IF NOT EXISTS app.lessons (id VARCHAR PRIMARY KEY, title VARCHAR(255), description TEXT, difficulty VARCHAR, "order" INT, estimated_duration_minutes INT, created_at TIMESTAMPTZ DEFAULT NOW(), updated_at TIMESTAMPTZ);
    CREATE TABLE IF NOT EXISTS app.users (id VARCHAR PRIMARY KEY, email VARCHAR(255), username VARCHAR(255), created_at TIMESTAMPTZ DEFAULT NOW(), updated_at TIMESTAMPTZ);
    CREATE TABLE IF NOT EXISTS app.words (id VARCHAR PRIMARY KEY, finnish_word VARCHAR(255), english_translation VARCHAR(255), part_of_speech VARCHAR(100), grammatical_forms TEXT, example_sentences TEXT, ai_definition TEXT, ai_examples TEXT, created_at TIMESTAMPTZ DEFAULT NOW(), updated_at TIMESTAMPTZ);
    CREATE TABLE IF NOT EXISTS app.vocabulary_lists (id VARCHAR PRIMARY KEY, title VARCHAR(255), description TEXT, difficulty VARCHAR, lesson_id VARCHAR REFERENCES app.lessons(id), created_at TIMESTAMPTZ DEFAULT NOW());
    CREATE TABLE IF NOT EXISTS app.vocabulary_words (id VARCHAR PRIMARY KEY, finnish VARCHAR(255), english VARCHAR(255), part_of_speech VARCHAR(100), example_sentence TEXT, pronunciation VARCHAR(255), difficulty VARCHAR, vocabulary_list_id VARCHAR REFERENCES app.vocabulary_lists(id), created_at TIMESTAMPTZ DEFAULT NOW());
    CREATE TABLE IF NOT EXISTS app.exercises (id VARCHAR PRIMARY KEY, lesson_id VARCHAR REFERENCES app.lessons(id), type VARCHAR, question TEXT, options TEXT, correct_answer VARCHAR(255), explanation TEXT, difficulty VARCHAR, created_at TIMESTAMPTZ DEFAULT NOW());
    CREATE TABLE IF NOT EXISTS app.user_words (id VARCHAR PRIMARY KEY, user_id VARCHAR REFERENCES app.users(id), word_id VARCHAR REFERENCES app.words(id), status VARCHAR, proficiency INT DEFAULT 0, date_added TIMESTAMPTZ DEFAULT NOW(), last_reviewed TIMESTAMPTZ, review_count INT DEFAULT 0, created_at TIMESTAMPTZ DEFAULT NOW(), updated_at TIMESTAMPTZ);
    CREATE TABLE IF NOT EXISTS app.lesson_progress (id VARCHAR PRIMARY KEY, user_id VARCHAR REFERENCES app.users(id), lesson_id VARCHAR REFERENCES app.lessons(id), started_at TIMESTAMPTZ DEFAULT NOW(), completed_at TIMESTAMPTZ, exercises_completed INT DEFAULT 0, exercises_correct INT DEFAULT 0, time_spent_seconds INT DEFAULT 0, status VARCHAR(50) DEFAULT 'in_progress');
    CREATE TABLE IF NOT EXISTS app.exercise_results (id VARCHAR PRIMARY KEY, user_id VARCHAR REFERENCES app.users(id), exercise_id VARCHAR REFERENCES app.exercises(id), lesson_progress_id VARCHAR REFERENCES app.lesson_progress(id), correct BOOLEAN, user_answer TEXT, time_spent_seconds INT, submitted_at TIMESTAMPTZ DEFAULT NOW());
    """
    # Run each statement (psql-style would need splitting)
    async with engine.begin() as conn:
        for stmt in sql.strip().split(";"):
            stmt = stmt.strip()
            if stmt and not stmt.startswith("--"):
                try:
                    await conn.execute(text(stmt))
                except Exception as e:
                    if "already exists" not in str(e):
                        print(f"Note: {e}")

    # Insert data
    inserts = [
        ("app.lessons", ["('lesson-1','Greetings','Basic greetings','beginner',1,15)", "('lesson-2','Numbers','Learn numbers','beginner',2,20)", "('lesson-3','Colors','Colors','elementary',3,15)", "('lesson-4','Family','Family','elementary',4,25)", "('lesson-5','Food','Food','intermediate',5,30)"], "(id,title,description,difficulty,\"order\",estimated_duration_minutes)"),
        ("app.users", ["('user-1','anna@ex.com','anna')", "('user-2','mikko@ex.com','mikko')", "('user-3','liisa@ex.com','liisa')", "('user-4','jussi@ex.com','jussi')", "('user-5','sanna@ex.com','sanna')"], "(id,email,username)"),
        ("app.words", ["('word-1','kissa','cat','noun','{}')", "('word-2','koira','dog','noun','{}')", "('word-3','talo','house','noun','{}')", "('word-4','omena','apple','noun','{}')", "('word-5','vesi','water','noun','{}')"], "(id,finnish_word,english_translation,part_of_speech,grammatical_forms)"),
    ]
    async with engine.begin() as conn:
        for table, rows, cols in inserts:
            for row in rows:
                try:
                    await conn.execute(text(f"INSERT INTO {table} {cols} VALUES {row} ON CONFLICT (id) DO NOTHING"))
                except Exception as e:
                    print(f"  {table}: {e}")

    # More inserts with FKs
    more = [
        ("app.vocabulary_lists", "(id,title,description,difficulty,lesson_id)", ["('vl-1','Greetings','Basic','beginner','lesson-1')", "('vl-2','Numbers','1-10','beginner','lesson-2')", "('vl-3','Colors','Colors','elementary','lesson-3')", "('vl-4','Family','Family','elementary','lesson-4')", "('vl-5','Food','Food','intermediate','lesson-5')"]),
        ("app.vocabulary_words", "(id,finnish,english,part_of_speech,vocabulary_list_id)", ["('vw-1','hei','hello','interjection','vl-1')", "('vw-2','yksi','one','numeral','vl-2')", "('vw-3','punainen','red','adjective','vl-3')", "('vw-4','isä','father','noun','vl-4')", "('vw-5','leipä','bread','noun','vl-5')"]),
        ("app.exercises", "(id,lesson_id,type,question,options,correct_answer,difficulty)", ["('ex-1','lesson-1','multiple_choice','Hello?','[]','hei','beginner')", "('ex-2','lesson-2','fill_in_blank','Three?','[]','kolme','beginner')", "('ex-3','lesson-3','translation','sininen','[]','blue','elementary')", "('ex-4','lesson-4','multiple_choice','Mother?','[]','äiti','elementary')", "('ex-5','lesson-5','translation','maito','[]','milk','intermediate')"]),
        ("app.user_words", "(id,user_id,word_id,status,proficiency)", ["('uw-1','user-1','word-1','learning',50)", "('uw-2','user-1','word-2','recent',0)", "('uw-3','user-2','word-3','mastered',100)", "('uw-4','user-2','word-4','learning',30)", "('uw-5','user-3','word-5','recent',0)"]),
        ("app.lesson_progress", "(id,user_id,lesson_id,status,exercises_completed,exercises_correct)", ["('lp-1','user-1','lesson-1','completed',5,4)", "('lp-2','user-1','lesson-2','in_progress',2,2)", "('lp-3','user-2','lesson-1','completed',5,5)", "('lp-4','user-2','lesson-3','in_progress',1,1)", "('lp-5','user-3','lesson-1','in_progress',0,0)"]),
        ("app.exercise_results", "(id,user_id,exercise_id,lesson_progress_id,correct,user_answer,time_spent_seconds)", ["('er-1','user-1','ex-1','lp-1',true,'hei',5)", "('er-2','user-1','ex-2','lp-2',true,'kolme',8)", "('er-3','user-2','ex-1','lp-3',true,'hei',3)", "('er-4','user-2','ex-3','lp-4',false,'green',10)", "('er-5','user-3','ex-1','lp-5',false,'moi',12)"]),
    ]
    async with engine.begin() as conn2:
        for table, cols, rows in more:
            for row in rows:
                try:
                    await conn2.execute(text(f"INSERT INTO {table} {cols} VALUES {row} ON CONFLICT (id) DO NOTHING"))
                except Exception as e:
                    print(f"  {table}: {e}")

    print("Seed complete. 5 rows per table.")

if __name__ == "__main__":
    asyncio.run(main())
