/**
 * API Service for Finnish Learning App
 * Uses relative paths - will work whether served from / or /finnish/
 */

const API_BASE_URL = '';

export interface WordData {
  word: string;
  translation: string;
  pronunciation: string;
  partOfSpeech: string;
  forms: {
    nominative: string;
    genitive: string;
    partitive: string;
    illative: string;
  };
  example: string;
  wordHints?: Array<{ word: string; translation: string }>;
  memoryAid: string;
  category: string;
}

export interface TranslationRequest {
  text: string;
  source_lang?: string;
  target_lang?: string;
}

export interface TranslationResponse {
  original: string;
  translation: string;
  source_lang: string;
  target_lang: string;
}

/**
 * Get word details from API
 */
export async function getWord(
  word: string,
  sourceLang: string = 'fi',
  targetLang: string = 'da'
): Promise<WordData> {
  const response = await fetch(
    `${API_BASE_URL}/api/word/${encodeURIComponent(word)}?source_lang=${sourceLang}&target_lang=${targetLang}`
  );
  
  if (!response.ok) {
    throw new Error(`API error: ${response.status} ${response.statusText}`);
  }
  
  return response.json();
}

/**
 * Translate text using AI
 */
export async function translateText(
  request: TranslationRequest
): Promise<TranslationResponse> {
  const response = await fetch(`${API_BASE_URL}/api/translate`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(request),
  });
  
  if (!response.ok) {
    throw new Error(`API error: ${response.status} ${response.statusText}`);
  }
  
  return response.json();
}

/**
 * Health check
 */
export async function checkHealth(): Promise<{ status: string }> {
  const response = await fetch(`${API_BASE_URL}/health`);
  return response.json();
}
