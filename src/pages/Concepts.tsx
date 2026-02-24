import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { Link } from 'react-router-dom'
import { conceptAPI } from '../lib/api'
import { Concept } from '../lib/types'
import LoadingSpinner from '../components/LoadingSpinner'

export default function Concepts() {
  const queryClient = useQueryClient()
  const [name, setName] = useState('')
  const [description, setDescription] = useState('')
  const [editingId, setEditingId] = useState<string | null>(null)
  const [editName, setEditName] = useState('')
  const [editDesc, setEditDesc] = useState('')

  const { data: concepts = [], isLoading } = useQuery({
    queryKey: ['concepts'],
    queryFn: () => conceptAPI.list(),
  })

  const createMutation = useMutation({
    mutationFn: (payload: { name: string; description?: string }) =>
      conceptAPI.create(payload),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['concepts'] })
      setName('')
      setDescription('')
    },
  })

  const updateMutation = useMutation({
    mutationFn: ({ id, payload }: { id: string; payload: { name?: string; description?: string } }) =>
      conceptAPI.update(id, payload),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['concepts'] })
      setEditingId(null)
    },
  })

  const deleteMutation = useMutation({
    mutationFn: (id: string) => conceptAPI.delete(id),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['concepts'] }),
  })

  const handleCreate = (e: React.FormEvent) => {
    e.preventDefault()
    if (!name.trim()) return
    createMutation.mutate({ name: name.trim(), description: description.trim() || undefined })
  }

  const startEdit = (c: Concept) => {
    setEditingId(c.id)
    setEditName(c.name)
    setEditDesc(c.description || '')
  }

  const saveEdit = () => {
    if (!editingId) return
    updateMutation.mutate({ id: editingId, payload: { name: editName, description: editDesc } })
  }

  if (isLoading) {
    return <LoadingSpinner message="Loading concepts..." />
  }

  const base = import.meta.env.BASE_URL?.replace(/\/$/, '') || ''

  return (
    <div
      className="min-h-screen"
      style={{
        background: 'linear-gradient(135deg, #0f172a 0%, #1e293b 50%, #334155 100%)',
      }}
    >
      <div className="max-w-4xl mx-auto px-6 py-8">
        <div className="flex items-center justify-between mb-8">
          <div>
            <h1 className="text-3xl font-bold text-white">Grammatical Concepts</h1>
            <p className="text-slate-400 mt-1">Manage concepts for spaced repetition (e.g. Partitiivi, Verbityypit)</p>
          </div>
          <Link
            to={base || '/'}
            className="text-sky-400 hover:text-sky-300 font-medium transition-colors"
          >
            <i className="bi bi-arrow-left mr-1" /> Back to Home
          </Link>
        </div>

        {/* Add form */}
        <div
          className="rounded-2xl p-6 mb-8"
          style={{
            background: 'rgba(255, 255, 255, 0.03)',
            backdropFilter: 'blur(20px)',
            border: '1px solid rgba(255, 255, 255, 0.1)',
          }}
        >
          <h2 className="font-semibold text-white mb-4">Add Concept</h2>
          <form onSubmit={handleCreate} className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-slate-300 mb-1">Name *</label>
              <input
                type="text"
                value={name}
                onChange={(e) => setName(e.target.value)}
                placeholder="e.g. Partitiivi"
                className="w-full px-4 py-2 bg-slate-800/50 border border-slate-600 rounded-lg text-white placeholder-slate-500 focus:ring-2 focus:ring-sky-500 focus:border-sky-500"
                required
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-slate-300 mb-1">Description</label>
              <textarea
                value={description}
                onChange={(e) => setDescription(e.target.value)}
                placeholder="Brief explanation..."
                rows={2}
                className="w-full px-4 py-2 bg-slate-800/50 border border-slate-600 rounded-lg text-white placeholder-slate-500 focus:ring-2 focus:ring-sky-500 focus:border-sky-500"
              />
            </div>
            <button
              type="submit"
              disabled={createMutation.isPending}
              className="px-4 py-2 bg-sky-600 text-white rounded-lg hover:bg-sky-500 disabled:opacity-50 transition-colors"
            >
              {createMutation.isPending ? 'Adding...' : 'Add Concept'}
            </button>
          </form>
          {createMutation.isError && (
            <p className="mt-2 text-sm text-red-400">{String(createMutation.error)}</p>
          )}
        </div>

        {/* List */}
        <div
          className="rounded-2xl overflow-hidden"
          style={{
            background: 'rgba(255, 255, 255, 0.03)',
            backdropFilter: 'blur(20px)',
            border: '1px solid rgba(255, 255, 255, 0.1)',
          }}
        >
          <h2 className="font-semibold text-white p-6 pb-0">Concepts ({concepts.length})</h2>
          {concepts.length === 0 ? (
            <div className="p-8 text-center text-slate-500">No concepts yet. Add one above.</div>
          ) : (
            <div className="divide-y divide-slate-700/50">
              {concepts.map((c) => (
                <div key={c.id} className="p-6 hover:bg-white/5 transition-colors">
                  {editingId === c.id ? (
                    <div className="space-y-3">
                      <input
                        value={editName}
                        onChange={(e) => setEditName(e.target.value)}
                        className="w-full px-3 py-2 bg-slate-800/50 border border-slate-600 rounded text-white"
                      />
                      <textarea
                        value={editDesc}
                        onChange={(e) => setEditDesc(e.target.value)}
                        rows={2}
                        className="w-full px-3 py-2 bg-slate-800/50 border border-slate-600 rounded text-white"
                      />
                      <div className="flex gap-2">
                        <button
                          onClick={saveEdit}
                          disabled={updateMutation.isPending}
                          className="px-3 py-1 bg-sky-600 text-white rounded text-sm hover:bg-sky-500"
                        >
                          Save
                        </button>
                        <button
                          onClick={() => setEditingId(null)}
                          className="px-3 py-1 bg-slate-600 text-white rounded text-sm hover:bg-slate-500"
                        >
                          Cancel
                        </button>
                      </div>
                    </div>
                  ) : (
                    <div className="flex justify-between items-start">
                      <div>
                        <h3 className="font-medium text-white">{c.name}</h3>
                        {c.description && (
                          <p className="text-sm text-slate-400 mt-1">{c.description}</p>
                        )}
                        <div className="flex gap-2 mt-2">
                          {c.tags?.map((t) => (
                            <span key={t} className="text-xs px-2 py-0.5 bg-slate-700/50 text-slate-300 rounded">
                              {t}
                            </span>
                          ))}
                          {c.priority != null && (
                            <span className="text-xs text-slate-500">priority: {c.priority.toFixed(2)}</span>
                          )}
                        </div>
                      </div>
                      <div className="flex gap-2">
                        <button
                          onClick={() => startEdit(c)}
                          className="text-sm text-sky-400 hover:text-sky-300"
                        >
                          Edit
                        </button>
                        <button
                          onClick={() => deleteMutation.mutate(c.id)}
                          disabled={deleteMutation.isPending}
                          className="text-sm text-red-400 hover:text-red-300"
                        >
                          Delete
                        </button>
                      </div>
                    </div>
                  )}
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
