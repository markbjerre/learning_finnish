export interface Lesson {
  id: string
  title: string
  description: string
  difficulty: 'beginner' | 'intermediate' | 'advanced'
  estimated_duration_minutes: number
  order: number
}

export interface LessonPreview extends Lesson {
  vocabulary_count?: number
  exercise_count?: number
}

export interface VocabularyWord {
  id: string
  finnish: string
  english: string
  pronunciation: string
  example_sentence?: string
}

export interface VocabularyList {
  id: string
  lesson_id: string
  words: VocabularyWord[]
}

export interface Exercise {
  id: string
  lesson_id: string
  type: 'multiple_choice' | 'translation' | 'matching'
  question: string
  options?: string[]
  correct_answer: string
}

export interface UserProgress {
  user_id: string
  total_lessons_completed: number
  total_exercises_completed: number
  total_accuracy: number
  total_study_time_minutes: number
  current_difficulty?: string
  last_studied?: string
  streak_days?: number
}

export interface LessonProgress {
  user_id: string
  lesson_id: string
  started_at: string
  completed_at?: string
  accuracy_percentage?: number
}

export interface HealthResponse {
  status: string
  timestamp: string
}

// ============================================================================
// Word Lookup and Wordbook types
// ============================================================================

/**
 * Status levels for tracking user's learning progress with words
 * - Recent: Word was just added to the wordbook
 * - Learning: User is actively studying this word
 * - Mastered: User has mastered this word
 */
export type WordStatus = 'Recent' | 'Learning' | 'Mastered'

/**
 * Represents a grammatical form of a Finnish word
 * Includes case information and translations
 */
export interface GrammaticalForm {
  case: string       // e.g., nominative, genitive, partitive, inessive
  finnish: string    // The grammatical form of the word in Finnish
  english: string    // English translation of the grammatical form
}

/**
 * Example sentence with Finnish text and English translation
 * Used to demonstrate word usage in context
 */
export interface ExampleSentence {
  finnish: string    // Example sentence in Finnish
  english: string    // English translation of the sentence
}

/**
 * Complete word search result with all metadata
 * Returned from the word lookup API endpoint
 * Contains translations, grammatical forms, examples, and AI definition
 */
export interface WordSearchResult {
  id?: string                              // Unique word identifier
  finnish_word: string                     // The Finnish word
  english_translation: string              // English translation
  part_of_speech: string                   // Word category (noun, verb, adj, etc)
  grammatical_forms?: GrammaticalForm[]    // Array of grammatical cases
  example_sentences?: ExampleSentence[]    // Array of usage examples
  ai_definition?: string                   // AI-generated definition
  frequency?: number                       // Word frequency percentage (0-100)
}

/**
 * User's saved word with learning progress tracking
 * Includes status, proficiency level, and review information
 * Represents the relationship between a user and a word
 */
export interface UserWord {
  id: string              // Unique user-word relationship identifier
  user_id: string         // Reference to the user
  finnish_word: string    // The Finnish word (denormalized for convenience)
  english_translation: string  // English translation (denormalized for convenience)
  status: WordStatus      // Current learning status
  proficiency: number     // Proficiency level (0-100 scale)
  saved_at: string        // ISO timestamp when word was saved
  last_reviewed: string   // ISO timestamp of last review
}

/**
 * Request payload for saving a word to user's wordbook
 * Sent to POST /api/words/save endpoint
 */
export interface SaveWordRequest {
  user_id: string      // ID of the user saving the word
  finnish_word: string // The Finnish word to save
}

/**
 * Request payload for updating a word's learning status and proficiency
 * Sent to PUT /api/words/:wordId/status/:userId endpoint
 */
export interface UpdateWordStatusRequest {
  status: WordStatus       // New learning status
  proficiency?: number     // New proficiency level (0-100, optional)
}
