import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { wordAPI } from '../lib/api'
import { SpacedWord } from '../lib/types'
import LoadingSpinner from './LoadingSpinner'

const WORD_TYPES = ['noun', 'verb', 'adjective', 'adverb', 'phrase', 'other'] as const

function priorityColor(priority: number): string {
  if (priority <= 0.2) return 'bg-green-100 text-green-800'
  if (priority <= 0.5) return 'bg-amber-100 text-amber-800'
  return 'bg-red-100 text-red-800'
}

export default function WordList() {
  const [search, setSearch] = useState('')
  const [wordType, setWordType] = useState<string>('')
  const [sortBy, setSortBy] = useState<'priority' | 'finnish'>('priority')

  const { data: words = [], isLoading } = useQuery({
    queryKey: ['words', search, wordType],
    queryFn: () =>
      wordAPI.listWords({
        limit: 200,
        search: search.trim() || undefined,
        word_type: wordType || undefined,
      }),
  })

  const sortedWords = [...words].sort((a, b) => {
    if (sortBy === 'priority') return (b.priority ?? 0) - (a.priority ?? 0)
    return (a.finnish || '').localeCompare(b.finnish || '')
  })

  if (isLoading) {
    return <LoadingSpinner message="Loading vocabulary..." />
  }

  return (
    <div className="space-y-6">
      <div className="bg-white rounded-lg shadow p-6">
        <h2 className="text-2xl font-bold text-gray-900 mb-4">Vocabulary</h2>
        <p className="text-gray-600 mb-4">
          All words in the spaced repetition system. Priority: green = mastered, red = needs work.
        </p>

        {/* Filters */}
        <div className="flex flex-wrap gap-4 mb-4">
          <input
            type="text"
            placeholder="Search Finnish, Danish, English..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 min-w-[200px]"
          />
          <select
            value={wordType}
            onChange={(e) => setWordType(e.target.value)}
            className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500"
          >
            <option value="">All types</option>
            {WORD_TYPES.map((t) => (
              <option key={t} value={t}>
                {t}
              </option>
            ))}
          </select>
          <select
            value={sortBy}
            onChange={(e) => setSortBy(e.target.value as 'priority' | 'finnish')}
            className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500"
          >
            <option value="priority">Sort by priority</option>
            <option value="finnish">Sort by Finnish</option>
          </select>
        </div>

        {/* Table */}
        {sortedWords.length === 0 ? (
          <p className="text-gray-500 py-8 text-center">No words found. Add words via the Add Word tab.</p>
        ) : (
          <div className="overflow-x-auto">
            <table className="min-w-full text-sm">
              <thead>
                <tr className="border-b border-gray-200">
                  <th className="text-left py-3 font-medium text-gray-700">Finnish</th>
                  <th className="text-left py-3 font-medium text-gray-700">Danish</th>
                  <th className="text-left py-3 font-medium text-gray-700">English</th>
                  <th className="text-left py-3 font-medium text-gray-700">Type</th>
                  <th className="text-left py-3 font-medium text-gray-700">Priority</th>
                  <th className="text-left py-3 font-medium text-gray-700">Served</th>
                  <th className="text-left py-3 font-medium text-gray-700">Last</th>
                </tr>
              </thead>
              <tbody>
                {sortedWords.map((w: SpacedWord) => (
                  <tr key={w.id} className="border-b border-gray-100 hover:bg-gray-50">
                    <td className="py-3 font-medium text-gray-900">{w.finnish}</td>
                    <td className="py-3 text-gray-600">{w.danish || '—'}</td>
                    <td className="py-3 text-gray-600">{w.english || '—'}</td>
                    <td className="py-3 text-gray-600">{w.word_type}</td>
                    <td className="py-3">
                      <span className={`px-2 py-0.5 rounded text-xs font-medium ${priorityColor(w.priority ?? 1)}`}>
                        {(w.priority ?? 1).toFixed(2)}
                      </span>
                    </td>
                    <td className="py-3 text-gray-600">{w.times_served ?? 0}</td>
                    <td className="py-3 text-gray-600">
                      {w.last_score != null ? `${w.last_score}/10` : '—'}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  )
}
