import { useState } from 'react'
import { wordAPI } from '../lib/api'
import { WordSearchResult, ExampleSentence, GrammaticalForm } from '../lib/types'
import LoadingSpinner from './LoadingSpinner'

interface WordLookupProps {
  userId: string
}

export default function WordLookup({ userId }: WordLookupProps) {
  const [searchQuery, setSearchQuery] = useState('')
  const [searchResult, setSearchResult] = useState<WordSearchResult | null>(null)
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [isSaving, setIsSaving] = useState(false)
  const [saveSuccess, setSaveSuccess] = useState(false)

  const handleSearch = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!searchQuery.trim()) return

    setIsLoading(true)
    setError(null)
    setSaveSuccess(false)

    try {
      const result = await wordAPI.searchWord(searchQuery)
      setSearchResult(result)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to search word')
      setSearchResult(null)
    } finally {
      setIsLoading(false)
    }
  }

  const handleSaveWord = async () => {
    if (!searchResult?.finnish_word) return

    setIsSaving(true)
    setError(null)

    try {
      await wordAPI.saveWord(userId, searchResult.finnish_word)
      setSaveSuccess(true)
      setTimeout(() => setSaveSuccess(false), 3000)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to save word')
    } finally {
      setIsSaving(false)
    }
  }

  return (
    <div className="space-y-8">
      {/* Search Section */}
      <div className="bg-white rounded-lg shadow p-8">
        <h2 className="text-2xl font-bold text-gray-900 mb-6">Word Lookup</h2>

        <form onSubmit={handleSearch} className="space-y-4">
          <div className="flex gap-3">
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="Enter a Finnish word..."
              className="flex-1 px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500"
            />
            <button
              type="submit"
              disabled={isLoading}
              className="px-6 py-3 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition disabled:opacity-50"
            >
              {isLoading ? 'Searching...' : 'Search'}
            </button>
          </div>
        </form>

        {error && (
          <div className="mt-4 p-4 bg-red-50 border border-red-200 rounded-lg">
            <p className="text-red-700">{error}</p>
          </div>
        )}

        {saveSuccess && (
          <div className="mt-4 p-4 bg-green-50 border border-green-200 rounded-lg">
            <p className="text-green-700">✓ Word saved to your wordbook!</p>
          </div>
        )}
      </div>

      {/* Results Section */}
      {isLoading && <LoadingSpinner message="Searching for word..." />}

      {searchResult && !isLoading && (
        <div className="bg-white rounded-lg shadow p-8 space-y-6">
          {/* Word Header */}
          <div className="border-b pb-6">
            <div className="flex items-start justify-between mb-4">
              <div>
                <h3 className="text-4xl font-bold text-gray-900">{searchResult.finnish_word}</h3>
                <p className="text-lg text-indigo-600 mt-2 font-medium">{searchResult.part_of_speech}</p>
              </div>
              <button
                onClick={handleSaveWord}
                disabled={isSaving}
                className="px-6 py-3 bg-green-600 text-white rounded-lg hover:bg-green-700 transition disabled:opacity-50"
              >
                {isSaving ? 'Saving...' : '+ Add to Wordbook'}
              </button>
            </div>
            <p className="text-2xl text-gray-600">{searchResult.english_translation}</p>
          </div>

          {/* Grammatical Forms */}
          {searchResult.grammatical_forms && searchResult.grammatical_forms.length > 0 && (
            <div>
              <h4 className="text-lg font-semibold text-gray-900 mb-4">Grammatical Forms</h4>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                {searchResult.grammatical_forms.map((form: GrammaticalForm, idx: number) => (
                  <div key={idx} className="p-4 bg-gray-50 rounded-lg border border-gray-200">
                    <p className="text-sm text-gray-600 font-medium">{form.case}</p>
                    <p className="text-lg text-gray-900 font-semibold">{form.finnish}</p>
                    <p className="text-sm text-gray-600">{form.english}</p>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Example Sentences */}
          {searchResult.example_sentences && searchResult.example_sentences.length > 0 && (
            <div>
              <h4 className="text-lg font-semibold text-gray-900 mb-4">Example Sentences</h4>
              <div className="space-y-4">
                {searchResult.example_sentences.map((example: ExampleSentence, idx: number) => (
                  <div key={idx} className="p-4 bg-blue-50 border border-blue-200 rounded-lg">
                    <p className="text-gray-900 font-semibold mb-2">{example.finnish}</p>
                    <p className="text-gray-600 italic">{example.english}</p>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* AI Definition */}
          {searchResult.ai_definition && (
            <div>
              <h4 className="text-lg font-semibold text-gray-900 mb-3">Definition</h4>
              <div className="p-4 bg-purple-50 border border-purple-200 rounded-lg">
                <p className="text-gray-800">{searchResult.ai_definition}</p>
              </div>
            </div>
          )}
        </div>
      )}

      {/* Empty State */}
      {!isLoading && !searchResult && !error && (
        <div className="bg-white rounded-lg shadow p-12 text-center">
          <p className="text-gray-600 text-lg">Search for a Finnish word to get started</p>
        </div>
      )}
    </div>
  )
}
