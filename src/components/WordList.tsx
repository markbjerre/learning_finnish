import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { wordAPI } from '../lib/api'
import { SpacedWord } from '../lib/types'
import LoadingSpinner from './LoadingSpinner'

const WORD_TYPES = ['noun', 'verb', 'adjective', 'adverb', 'phrase', 'other'] as const

function priorityColor(priority: number): string {
  if (priority <= 0.2) return 'bg-emerald-500/20 text-emerald-300'
  if (priority <= 0.5) return 'bg-amber-500/20 text-amber-300'
  return 'bg-red-500/20 text-red-300'
}

interface InflectionRow {
  case_name: string
  singular: string
  plural: string
  notes?: string
}

interface VerbFormRow {
  form_name: string
  form_value: string
  tense: string
  notes?: string
}

function WordRow({
  word,
  isExpanded,
  onToggle,
}: {
  word: SpacedWord
  isExpanded: boolean
  onToggle: () => void
}) {
  const { data: inflectionsData, isLoading: inflectionsLoading } = useQuery({
    queryKey: ['inflections', word.id],
    queryFn: () => wordAPI.getInflections(word.id),
    enabled: isExpanded,
  })

  const inflections = (inflectionsData?.inflections ?? []) as InflectionRow[]
  const verbForms = (inflectionsData?.verb_forms ?? []) as VerbFormRow[]

  return (
    <>
      <tr
        className="border-b border-slate-700/50 hover:bg-white/5 transition-colors cursor-pointer"
        onClick={onToggle}
      >
        <td className="py-3 w-8">
          <span className={`inline-block transition-transform ${isExpanded ? 'rotate-90' : ''}`}>
            <i className="bi bi-chevron-right text-slate-500" />
          </span>
        </td>
        <td className="py-3 font-medium text-white">{word.finnish}</td>
        <td className="py-3 text-slate-400">{word.danish || '—'}</td>
        <td className="py-3 text-slate-400">{word.english || '—'}</td>
        <td className="py-3 text-slate-400">{word.word_type}</td>
        <td className="py-3">
          <span className={`px-2 py-0.5 rounded text-xs font-medium ${priorityColor(word.priority ?? 1)}`}>
            {(word.priority ?? 1).toFixed(2)}
          </span>
        </td>
        <td className="py-3 text-slate-400">{word.times_served ?? 0}</td>
        <td className="py-3 text-slate-400">
          {word.last_score != null ? `${word.last_score}/10` : '—'}
        </td>
      </tr>
      {isExpanded && (
        <tr>
          <td colSpan={8} className="py-4 px-6 bg-slate-800/30">
            {inflectionsLoading ? (
              <p className="text-slate-500 text-sm">Loading inflections...</p>
            ) : inflections.length > 0 || verbForms.length > 0 ? (
              <div className="space-y-4">
                {inflections.length > 0 && (
                  <div>
                    <h4 className="text-sm font-medium text-slate-400 mb-2">Kasus (cases)</h4>
                    <div className="overflow-x-auto">
                      <table className="min-w-full text-sm">
                        <thead>
                          <tr className="border-b border-slate-600">
                            <th className="text-left py-2 text-slate-400">Case</th>
                            <th className="text-left py-2 text-slate-400">Singular</th>
                            <th className="text-left py-2 text-slate-400">Plural</th>
                          </tr>
                        </thead>
                        <tbody>
                          {inflections.map((i, idx) => (
                            <tr key={idx} className="border-b border-slate-700/50">
                              <td className="py-2 text-slate-300 capitalize">{i.case_name}</td>
                              <td className="py-2 text-white">{i.singular || '—'}</td>
                              <td className="py-2 text-white">{i.plural || '—'}</td>
                            </tr>
                          ))}
                        </tbody>
                      </table>
                    </div>
                  </div>
                )}
                {verbForms.length > 0 && (
                  <div>
                    <h4 className="text-sm font-medium text-slate-400 mb-2">Verb forms</h4>
                    <div className="overflow-x-auto">
                      <table className="min-w-full text-sm">
                        <thead>
                          <tr className="border-b border-slate-600">
                            <th className="text-left py-2 text-slate-400">Form</th>
                            <th className="text-left py-2 text-slate-400">Value</th>
                            <th className="text-left py-2 text-slate-400">Tense</th>
                          </tr>
                        </thead>
                        <tbody>
                          {verbForms.map((v, idx) => (
                            <tr key={idx} className="border-b border-slate-700/50">
                              <td className="py-2 text-slate-300">{v.form_name}</td>
                              <td className="py-2 text-white">{v.form_value}</td>
                              <td className="py-2 text-slate-300">{v.tense || '—'}</td>
                            </tr>
                          ))}
                        </tbody>
                      </table>
                    </div>
                  </div>
                )}
              </div>
            ) : (
              <p className="text-slate-500 text-sm">No inflections yet. Add word with OpenAI configured to generate.</p>
            )}
          </td>
        </tr>
      )}
    </>
  )
}

export default function WordList() {
  const [search, setSearch] = useState('')
  const [wordType, setWordType] = useState<string>('')
  const [sortBy, setSortBy] = useState<'priority' | 'finnish'>('priority')
  const [expandedWordId, setExpandedWordId] = useState<string | null>(null)

  const { data: words = [], isLoading, error, isError } = useQuery({
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

  if (isError) {
    return (
      <div
        className="rounded-2xl p-6"
        style={{
          background: 'rgba(255, 255, 255, 0.03)',
          backdropFilter: 'blur(20px)',
          border: '1px solid rgba(239, 68, 68, 0.5)',
        }}
      >
        <h2 className="text-xl font-bold text-red-400 mb-2">Error Loading Words</h2>
        <p className="text-red-300">
          {error instanceof Error ? error.message : 'Failed to load vocabulary words'}
        </p>
        <p className="text-slate-400 text-sm mt-2">
          Ensure the backend is running at http://localhost:8001
        </p>
      </div>
    )
  }

  const inputClass = 'px-4 py-2 bg-slate-800/50 border border-slate-600 rounded-lg text-white placeholder-slate-500 focus:ring-2 focus:ring-sky-500 min-w-[200px]'

  return (
    <div className="space-y-6">
      <div
        className="rounded-2xl p-6"
        style={{
          background: 'rgba(255, 255, 255, 0.03)',
          backdropFilter: 'blur(20px)',
          border: '1px solid rgba(255, 255, 255, 0.1)',
        }}
      >
        <h2 className="text-2xl font-bold text-white mb-4">Vocabulary</h2>
        <p className="text-slate-400 mb-4">
          All words in the spaced repetition system. Priority: green = mastered, red = needs work.
        </p>

        {/* Filters */}
        <div className="flex flex-wrap gap-4 mb-4">
          <input
            type="text"
            placeholder="Search Finnish, Danish, English..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className={inputClass}
          />
          <select
            value={wordType}
            onChange={(e) => setWordType(e.target.value)}
            className={inputClass}
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
            className={inputClass}
          >
            <option value="priority">Sort by priority</option>
            <option value="finnish">Sort by Finnish</option>
          </select>
        </div>

        {/* Table */}
        {sortedWords.length === 0 ? (
          <p className="text-slate-500 py-8 text-center">No words found. Add words via Enter Words.</p>
        ) : (
          <div className="overflow-x-auto">
            <table className="min-w-full text-sm">
              <thead>
                <tr className="border-b border-slate-600">
                  <th className="text-left py-3 font-medium text-slate-400 w-8" />
                  <th className="text-left py-3 font-medium text-slate-400">Finnish</th>
                  <th className="text-left py-3 font-medium text-slate-400">Danish</th>
                  <th className="text-left py-3 font-medium text-slate-400">English</th>
                  <th className="text-left py-3 font-medium text-slate-400">Type</th>
                  <th className="text-left py-3 font-medium text-slate-400">Priority</th>
                  <th className="text-left py-3 font-medium text-slate-400">Served</th>
                  <th className="text-left py-3 font-medium text-slate-400">Last</th>
                </tr>
              </thead>
              <tbody>
                {sortedWords.map((w: SpacedWord) => (
                  <WordRow
                    key={w.id}
                    word={w}
                    isExpanded={expandedWordId === w.id}
                    onToggle={() => setExpandedWordId((prev) => (prev === w.id ? null : w.id))}
                  />
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  )
}
