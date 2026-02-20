import axios, { AxiosInstance } from 'axios'
import { Lesson, LessonPreview, VocabularyWord, VocabularyList, UserProgress, HealthResponse, WordSearchResult, UserWord, SaveWordRequest, UpdateWordStatusRequest, SpacedStats, ExerciseHistoryEntry, Concept, SpacedWord } from './types'

/**
 * Axios instance configured for the Learning Finnish API
 * Base URL: Direct backend URL for development, /api proxy for production
 * Default Content-Type: application/json
 * Used by all API modules (healthAPI, lessonsAPI, wordAPI, etc.)
 */
const basePath = import.meta.env.BASE_URL || '/'
const axiosInstance: AxiosInstance = axios.create({
  baseURL: import.meta.env.DEV ? 'http://localhost:8001/api' : `${basePath}api`,
  headers: {
    'Content-Type': 'application/json',
  },
})

export const healthAPI = {
  check: async (): Promise<HealthResponse> => {
    const response = await axiosInstance.get('/health/simple')
    return response.data
  },
}

export const lessonsAPI = {
  getAll: async (difficulty?: string): Promise<Lesson[]> => {
    const response = await axiosInstance.get('/lessons', {
      params: difficulty ? { difficulty } : {},
    })
    return response.data
  },

  getById: async (id: string): Promise<Lesson> => {
    const response = await axiosInstance.get(`/lessons/${id}`)
    return response.data
  },
}

export const vocabularyAPI = {
  getAll: async (difficulty?: string): Promise<VocabularyList[]> => {
    const response = await axiosInstance.get('/vocabulary', {
      params: difficulty ? { difficulty } : {},
    })
    return response.data
  },

  getByLesson: async (lessonId: string): Promise<VocabularyWord[]> => {
    const response = await axiosInstance.get(`/vocabulary/lesson/${lessonId}`)
    return response.data
  },
}

export const progressAPI = {
  getUserProgress: async (userId: string = 'user-1'): Promise<UserProgress> => {
    const response = await axiosInstance.get(`/progress/user/${userId}`)
    return response.data
  },

  startLesson: async (lessonId: string, userId: string = 'user-1'): Promise<void> => {
    await axiosInstance.post(`/progress/lessons/${lessonId}/start`, {
      user_id: userId,
    })
  },

  completeLesson: async (lessonId: string, userId: string = 'user-1'): Promise<void> => {
    await axiosInstance.post(`/progress/lessons/${lessonId}/complete`, {
      user_id: userId,
    })
  },
}

/**
 * Word Lookup and Management API
 * Provides methods for searching Finnish words, managing personal wordbooks,
 * and tracking learning progress with proficiency levels
 *
 * Methods:
 * - searchWord(): Search for a Finnish word with full metadata
 * - saveWord(): Add a word to user's personal wordbook
 * - getUserWords(): Retrieve all words saved by a user
 * - updateWordStatus(): Update a word's learning status and proficiency
 * - removeWord(): Remove a word from user's wordbook
 */
export const wordAPI = {
  /**
   * Search for a Finnish word
   * Returns complete word metadata including translations, grammatical forms, examples, and AI definition
   * Falls back to mock data if backend is unavailable
   *
   * @param finnish_word - The Finnish word to search for
   * @returns WordSearchResult with full word details
   * @example
   * const result = await wordAPI.searchWord('kissa')
   * console.log(result.english) // 'cat'
   */
  searchWord: async (finnish_word: string): Promise<WordSearchResult> => {
    const response = await axiosInstance.post('/words/search', null, {
      params: { finnish_word },
    })
    return response.data
  },

  /**
   * Save a word to user's personal wordbook
   * If the word doesn't exist in the database, it will be created
   * If the user already has the word saved, returns the existing entry
   *
   * @param userId - The user ID (typically 'user-1')
   * @param finnish_word - The Finnish word to save
   * @returns UserWord with initial status 'Recent' and proficiency 0
   * @example
   * const userWord = await wordAPI.saveWord('user-1', 'kissa')
   * console.log(userWord.status) // 'Recent'
   */
  saveWord: async (userId: string, finnish_word: string): Promise<UserWord> => {
    const payload: SaveWordRequest = {
      user_id: userId,
      finnish_word,
    }
    const response = await axiosInstance.post('/words/save', payload)
    return response.data
  },

  /**
   * Retrieve all words saved by a user
   * Can optionally filter by status (Recent, Learning, Mastered)
   *
   * @param userId - The user ID
   * @param status - Optional: filter by 'Recent', 'Learning', or 'Mastered'
   * @returns Array of UserWord objects
   * @example
   * const learning = await wordAPI.getUserWords('user-1', 'Learning')
   * const all = await wordAPI.getUserWords('user-1')
   */
  getUserWords: async (userId: string, status?: string): Promise<UserWord[]> => {
    const response = await axiosInstance.get(`/words/user-words/${userId}`, {
      params: status ? { status } : {},
    })
    return response.data
  },

  /**
   * Update a word's learning status and proficiency
   * Automatically updates the 'last_reviewed' timestamp
   * Proficiency is clamped to 0-100 range
   *
   * @param userId - The user ID
   * @param wordId - The word ID to update
   * @param status - New status: 'Recent', 'Learning', or 'Mastered'
   * @param proficiency - Optional: new proficiency level (0-100)
   * @returns Updated UserWord object
   * @example
   * const updated = await wordAPI.updateWordStatus('user-1', 'word-123', 'Learning', 65)
   */
  updateWordStatus: async (userId: string, wordId: string, status: string, proficiency?: number): Promise<UserWord> => {
    const payload: UpdateWordStatusRequest = {
      status: status as any,
      proficiency,
    }
    const response = await axiosInstance.put(`/words/${wordId}/status/${userId}`, payload)
    return response.data
  },

  /**
   * Remove a word from user's wordbook
   * The word itself remains in the database but the user's association is deleted
   *
   * @param userId - The user ID
   * @param wordId - The word ID to remove
   * @returns Promise that resolves when deletion is complete
   * @example
   * await wordAPI.removeWord('user-1', 'word-123')
   */
  removeWord: async (userId: string, wordId: string): Promise<void> => {
    await axiosInstance.delete(`/words/${wordId}/${userId}`)
  },

  /** Add word (spaced repetition, triggers inflection generation) */
  addWord: async (payload: { finnish: string; danish?: string; english?: string; word_type?: string; tags?: string[] }): Promise<{ status: string; word_id: string; finnish: string; inflections_generated?: { inflections: number; verb_forms: number } }> => {
    const response = await axiosInstance.post('/words/add', payload)
    return response.data
  },

  /** Get inflections for a word */
  getInflections: async (wordId: string) => {
    const response = await axiosInstance.get(`/words/${wordId}/inflections`)
    return response.data
  },

  /** List vocabulary words (spaced repetition) */
  listWords: async (params?: { limit?: number; offset?: number; word_type?: string; search?: string }): Promise<SpacedWord[]> => {
    const response = await axiosInstance.get('/words', { params })
    return response.data
  },

  /** Bulk add words from CSV rows */
  bulkAdd: async (rows: string[][]): Promise<{ created: number; exists: number; errors: Array<{ row: number; word: string; error: string }> }> => {
    const response = await axiosInstance.post('/words/bulk-add', { rows })
    return response.data
  },
}

/** Concepts API (grammatical concepts for spaced repetition) */
export const conceptAPI = {
  list: async (limit = 100, offset = 0): Promise<Concept[]> => {
    const response = await axiosInstance.get('/concepts', { params: { limit, offset } })
    return response.data
  },

  get: async (id: string) => {
    const response = await axiosInstance.get(`/concepts/${id}`)
    return response.data
  },

  create: async (payload: { name: string; description?: string; tags?: string[] }) => {
    const response = await axiosInstance.post('/concepts', payload)
    return response.data
  },

  update: async (id: string, payload: Partial<{ name: string; description: string; tags: string[] }>) => {
    const response = await axiosInstance.put(`/concepts/${id}`, payload)
    return response.data
  },

  delete: async (id: string) => {
    const response = await axiosInstance.delete(`/concepts/${id}`)
    return response.data
  },
}

/** Spaced repetition / exercise API */
export const exerciseAPI = {
  getNext: async () => {
    const response = await axiosInstance.get('/exercise/next')
    return response.data
  },

  getHistory: async (limit = 20, offset = 0): Promise<ExerciseHistoryEntry[]> => {
    const response = await axiosInstance.get('/exercise/history', { params: { limit, offset } })
    return response.data
  },
}

/** Stats and settings API */
export const statsAPI = {
  getStats: async (): Promise<SpacedStats> => {
    const response = await axiosInstance.get('/stats')
    return response.data
  },

  getSettings: async () => {
    const response = await axiosInstance.get('/settings')
    return response.data
  },

  updateSettings: async (updates: Record<string, unknown>) => {
    const response = await axiosInstance.put('/settings', updates)
    return response.data
  },

  getChartData: async (days = 14): Promise<Array<{ date: string; count: number }>> => {
    const response = await axiosInstance.get('/stats/chart', { params: { days } })
    return response.data
  },
}

export default axiosInstance
