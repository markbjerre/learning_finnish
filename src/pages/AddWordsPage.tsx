import { useState } from 'react'
import { Link } from 'react-router-dom'
import { useMutation, useQueryClient } from '@tanstack/react-query'
import AddWord from '../components/AddWord'
import { conceptAPI } from '../lib/api'

const base = import.meta.env.BASE_URL?.replace(/\/$/, '') || ''

type EntryMode = 'word' | 'concept'

export default function AddWordsPage() {
  const [mode, setMode] = useState<EntryMode>('word')
  const [conceptName, setConceptName] = useState('')
  const [conceptDesc, setConceptDesc] = useState('')
  const queryClient = useQueryClient()

  const createConceptMutation = useMutation({
    mutationFn: (payload: { name: string; description?: string }) =>
      conceptAPI.create(payload),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['concepts'] })
      setConceptName('')
      setConceptDesc('')
    },
  })

  const handleAddConcept = (e: React.FormEvent) => {
    e.preventDefault()
    if (!conceptName.trim()) return
    createConceptMutation.mutate({
      name: conceptName.trim(),
      description: conceptDesc.trim() || undefined,
    })
  }

  const inputClass =
    'w-full px-4 py-2 bg-slate-800/50 border border-slate-600 rounded-lg text-white placeholder-slate-500 focus:ring-2 focus:ring-sky-500 focus:border-sky-500'
  const labelClass = 'block text-sm font-medium text-slate-300 mb-1'

  return (
    <div
      className="min-h-screen"
      style={{
        background: 'linear-gradient(135deg, #0f172a 0%, #1e293b 50%, #334155 100%)',
      }}
    >
      <div className="max-w-2xl mx-auto px-6 py-8">
        <div className="flex items-center justify-between mb-8">
          <h1 className="text-3xl font-bold text-white">Enter Words</h1>
          <Link
            to={base || '/'}
            className="text-sky-400 hover:text-sky-300 font-medium transition-colors"
          >
            <i className="bi bi-arrow-left mr-1" /> Back to Home
          </Link>
        </div>

        {/* Toggle: Word | Concept */}
        <div className="flex mb-6">
          <button
            type="button"
            onClick={() => setMode('word')}
            className={`flex-1 py-2.5 px-4 rounded-l-lg font-medium transition-colors ${
              mode === 'word'
                ? 'bg-sky-600 text-white'
                : 'bg-slate-700/50 text-slate-400 hover:bg-slate-700 hover:text-slate-300'
            }`}
          >
            Word
          </button>
          <button
            type="button"
            onClick={() => setMode('concept')}
            className={`flex-1 py-2.5 px-4 rounded-r-lg font-medium transition-colors ${
              mode === 'concept'
                ? 'bg-sky-600 text-white'
                : 'bg-slate-700/50 text-slate-400 hover:bg-slate-700 hover:text-slate-300'
            }`}
          >
            Concept
          </button>
        </div>

        {mode === 'word' ? (
          <AddWord />
        ) : (
          <div
            className="rounded-2xl p-8"
            style={{
              background: 'rgba(255, 255, 255, 0.03)',
              backdropFilter: 'blur(20px)',
              border: '1px solid rgba(255, 255, 255, 0.1)',
            }}
          >
            <h2 className="text-2xl font-bold text-white mb-6">Add Concept</h2>
            <p className="text-slate-400 mb-6">
              Add a grammatical concept for spaced repetition (e.g. Partitiivi, Verbityypit).
            </p>
            <form onSubmit={handleAddConcept} className="space-y-4">
              <div>
                <label className={labelClass}>Name *</label>
                <input
                  type="text"
                  value={conceptName}
                  onChange={(e) => setConceptName(e.target.value)}
                  placeholder="e.g. Partitiivi"
                  className={inputClass}
                  required
                />
              </div>
              <div>
                <label className={labelClass}>Description</label>
                <textarea
                  value={conceptDesc}
                  onChange={(e) => setConceptDesc(e.target.value)}
                  placeholder="Brief explanation..."
                  rows={3}
                  className={inputClass}
                />
              </div>
              <button
                type="submit"
                disabled={createConceptMutation.isPending}
                className="px-6 py-3 bg-sky-600 text-white rounded-lg hover:bg-sky-500 disabled:opacity-50 transition-colors"
              >
                {createConceptMutation.isPending ? 'Adding...' : 'Add Concept'}
              </button>
            </form>
            {createConceptMutation.isError && (
              <div className="mt-4 p-4 bg-red-900/30 border border-red-500/50 rounded-lg text-red-300">
                {String(createConceptMutation.error)}
              </div>
            )}
            {createConceptMutation.isSuccess && (
              <div className="mt-4 p-4 bg-emerald-900/30 border border-emerald-500/50 rounded-lg text-emerald-300">
                Concept added successfully.
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  )
}
