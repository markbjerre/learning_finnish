-- Seed app schema with example data (min 5 rows per table)
-- Run: PGPASSWORD=... psql -h dobbybrain -p 5433 -U learning_finnish -d learning_finnish -f seed_data_raw.sql

-- Ensure app schema exists
CREATE SCHEMA IF NOT EXISTS app;

-- 1. Lessons
INSERT INTO app.lessons (id, title, description, difficulty, "order", estimated_duration_minutes) VALUES
('lesson-1', 'Greetings', 'Basic greetings in Finnish', 'beginner', 1, 15),
('lesson-2', 'Numbers 1-10', 'Learn numbers', 'beginner', 2, 20),
('lesson-3', 'Colors', 'Common colors', 'elementary', 3, 15),
('lesson-4', 'Family', 'Family members', 'elementary', 4, 25),
('lesson-5', 'Food & Drink', 'Common food vocabulary', 'intermediate', 5, 30)
ON CONFLICT (id) DO NOTHING;

-- 2. Users
INSERT INTO app.users (id, email, username) VALUES
('user-1', 'anna@example.com', 'anna'),
('user-2', 'mikko@example.com', 'mikko'),
('user-3', 'liisa@example.com', 'liisa'),
('user-4', 'jussi@example.com', 'jussi'),
('user-5', 'sanna@example.com', 'sanna')
ON CONFLICT (id) DO NOTHING;

-- 3. Words (app.words - dictionary)
INSERT INTO app.words (id, finnish_word, english_translation, part_of_speech, grammatical_forms) VALUES
('word-1', 'kissa', 'cat', 'noun', '{"nominative":"kissa"}'),
('word-2', 'koira', 'dog', 'noun', '{"nominative":"koira"}'),
('word-3', 'talo', 'house', 'noun', '{"nominative":"talo"}'),
('word-4', 'omena', 'apple', 'noun', '{"nominative":"omena"}'),
('word-5', 'vesi', 'water', 'noun', '{"nominative":"vesi"}')
ON CONFLICT (id) DO NOTHING;

-- 4. Vocabulary lists (need lessons to exist)
INSERT INTO app.vocabulary_lists (id, title, description, difficulty, lesson_id) VALUES
('vl-1', 'Greetings vocab', 'Basic words', 'beginner', 'lesson-1'),
('vl-2', 'Numbers vocab', '1-10', 'beginner', 'lesson-2'),
('vl-3', 'Colors vocab', 'Colors', 'elementary', 'lesson-3'),
('vl-4', 'Family vocab', 'Family', 'elementary', 'lesson-4'),
('vl-5', 'Food vocab', 'Food', 'intermediate', 'lesson-5')
ON CONFLICT (id) DO NOTHING;

-- 5. Vocabulary words
INSERT INTO app.vocabulary_words (id, finnish, english, part_of_speech, vocabulary_list_id) VALUES
('vw-1', 'hei', 'hello', 'interjection', 'vl-1'),
('vw-2', 'yksi', 'one', 'numeral', 'vl-2'),
('vw-3', 'punainen', 'red', 'adjective', 'vl-3'),
('vw-4', 'isä', 'father', 'noun', 'vl-4'),
('vw-5', 'leipä', 'bread', 'noun', 'vl-5')
ON CONFLICT (id) DO NOTHING;

-- 6. Exercises
INSERT INTO app.exercises (id, lesson_id, type, question, options, correct_answer, difficulty) VALUES
('ex-1', 'lesson-1', 'multiple_choice', 'How do you say hello?', '["hei","moi","terve"]', 'hei', 'beginner'),
('ex-2', 'lesson-2', 'fill_in_blank', 'Three in Finnish is ___', '[]', 'kolme', 'beginner'),
('ex-3', 'lesson-3', 'translation', 'Translate: sininen', '[]', 'blue', 'elementary'),
('ex-4', 'lesson-4', 'multiple_choice', 'Mother in Finnish?', '["äiti","isä","sisko"]', 'äiti', 'elementary'),
('ex-5', 'lesson-5', 'translation', 'Translate: maito', '[]', 'milk', 'intermediate')
ON CONFLICT (id) DO NOTHING;

-- 7. User words
INSERT INTO app.user_words (id, user_id, word_id, status, proficiency) VALUES
('uw-1', 'user-1', 'word-1', 'learning', 50),
('uw-2', 'user-1', 'word-2', 'recent', 0),
('uw-3', 'user-2', 'word-3', 'mastered', 100),
('uw-4', 'user-2', 'word-4', 'learning', 30),
('uw-5', 'user-3', 'word-5', 'recent', 0)
ON CONFLICT (id) DO NOTHING;

-- 8. Lesson progress
INSERT INTO app.lesson_progress (id, user_id, lesson_id, status, exercises_completed, exercises_correct) VALUES
('lp-1', 'user-1', 'lesson-1', 'completed', 5, 4),
('lp-2', 'user-1', 'lesson-2', 'in_progress', 2, 2),
('lp-3', 'user-2', 'lesson-1', 'completed', 5, 5),
('lp-4', 'user-2', 'lesson-3', 'in_progress', 1, 1),
('lp-5', 'user-3', 'lesson-1', 'in_progress', 0, 0)
ON CONFLICT (id) DO NOTHING;

-- 9. Exercise results
INSERT INTO app.exercise_results (id, user_id, exercise_id, lesson_progress_id, correct, user_answer, time_spent_seconds) VALUES
('er-1', 'user-1', 'ex-1', 'lp-1', true, 'hei', 5),
('er-2', 'user-1', 'ex-2', 'lp-2', true, 'kolme', 8),
('er-3', 'user-2', 'ex-1', 'lp-3', true, 'hei', 3),
('er-4', 'user-2', 'ex-3', 'lp-4', false, 'green', 10),
('er-5', 'user-3', 'ex-1', 'lp-5', false, 'moi', 12)
ON CONFLICT (id) DO NOTHING;

SELECT 'Seed complete' AS status;
