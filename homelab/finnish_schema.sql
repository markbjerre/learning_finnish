-- Finnish Learning DB Schema
-- Run: PGPASSWORD=$FINNISH_DB_PASSWORD psql -h 127.0.0.1 -p 5433 -U learning_finnish -d learning_finnish -f finnish_schema.sql

-- Core vocabulary
CREATE TABLE IF NOT EXISTS words (
    id                SERIAL PRIMARY KEY,
    finnish           TEXT NOT NULL,
    danish            TEXT,
    english           TEXT,
    word_type         TEXT NOT NULL,
    grammatical_notes TEXT,
    tags              TEXT[],
    priority          FLOAT DEFAULT 1.0,
    times_served      INT DEFAULT 0,
    total_score       FLOAT DEFAULT 0.0,
    last_score        FLOAT,
    last_served       TIMESTAMPTZ,
    created_at        TIMESTAMPTZ DEFAULT NOW()
);

-- Finnish inflections (cases)
CREATE TABLE IF NOT EXISTS inflections (
    id            SERIAL PRIMARY KEY,
    word_id       INT REFERENCES words(id) ON DELETE CASCADE,
    case_name     TEXT NOT NULL,
    singular      TEXT,
    plural        TEXT,
    notes         TEXT,
    UNIQUE(word_id, case_name)
);

-- Verb conjugations
CREATE TABLE IF NOT EXISTS verb_forms (
    id            SERIAL PRIMARY KEY,
    word_id       INT REFERENCES words(id) ON DELETE CASCADE,
    form_name     TEXT NOT NULL,
    form_value    TEXT NOT NULL,
    tense         TEXT,
    notes         TEXT,
    UNIQUE(word_id, form_name, tense)
);

-- Grammatical concepts
CREATE TABLE IF NOT EXISTS concepts (
    id            SERIAL PRIMARY KEY,
    name          TEXT NOT NULL,
    description   TEXT,
    examples      JSONB,
    tags          TEXT[],
    priority      FLOAT DEFAULT 1.0,
    times_served  INT DEFAULT 0,
    total_score   FLOAT DEFAULT 0.0,
    last_score    FLOAT,
    last_served   TIMESTAMPTZ,
    created_at    TIMESTAMPTZ DEFAULT NOW()
);

-- Word to concept links
CREATE TABLE IF NOT EXISTS word_concepts (
    word_id       INT REFERENCES words(id) ON DELETE CASCADE,
    concept_id    INT REFERENCES concepts(id) ON DELETE CASCADE,
    PRIMARY KEY (word_id, concept_id)
);

-- Exercise history
CREATE TABLE IF NOT EXISTS exercise_log (
    id              SERIAL PRIMARY KEY,
    exercise_type   TEXT NOT NULL,
    level_used      INT,
    words_used      INT[],
    concepts_used   INT[],
    prompt_sent     TEXT,
    user_response   TEXT,
    ai_feedback     TEXT,
    word_scores     JSONB,
    concept_scores  JSONB,
    created_at      TIMESTAMPTZ DEFAULT NOW()
);

-- System settings
CREATE TABLE IF NOT EXISTS settings (
    key           TEXT PRIMARY KEY,
    value         JSONB NOT NULL
);

-- Initialize default settings
INSERT INTO settings (key, value) VALUES ('level', '15') ON CONFLICT (key) DO NOTHING;
INSERT INTO settings (key, value) VALUES ('exercise_word_count', '5') ON CONFLICT (key) DO NOTHING;
INSERT INTO settings (key, value) VALUES ('random_ratio', '0.25') ON CONFLICT (key) DO NOTHING;

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_words_priority ON words(priority DESC);
CREATE INDEX IF NOT EXISTS idx_words_finnish ON words(finnish);
CREATE INDEX IF NOT EXISTS idx_words_word_type ON words(word_type);
CREATE INDEX IF NOT EXISTS idx_inflections_word_id ON inflections(word_id);
CREATE INDEX IF NOT EXISTS idx_verb_forms_word_id ON verb_forms(word_id);
CREATE INDEX IF NOT EXISTS idx_concepts_priority ON concepts(priority DESC);
CREATE INDEX IF NOT EXISTS idx_exercise_log_created ON exercise_log(created_at DESC);

-- Verify
SELECT table_name FROM information_schema.tables WHERE table_schema = 'public' ORDER BY table_name;
