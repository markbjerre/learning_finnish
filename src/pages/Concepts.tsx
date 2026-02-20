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

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-indigo-50">
      <div className="max-w-4xl mx-auto px-6 py-8">
        <div className="flex items-center justify-between mb-8">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">Grammatical Concepts</h1>
            <p className="text-gray-600 mt-1">Manage concepts for spaced repetition (e.g. Partitiivi, Verbityypit)</p>
          </div>
          <Link
            to={import.meta.env.BASE_URL?.replace(/\/$/, '') || '/'}
            className="text-indigo-600 hover:text-indigo-700 font-medium"
          >
            ← Back to Home
          </Link>
        </div>

        {/* Add form */}
        <div className="bg-white rounded-xl shadow-sm p-6 border border-gray-100 mb-8">
          <h2 className="font-semibold text-gray-900 mb-4">Add Concept</h2>
          <form onSubmit={handleCreate} className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Name *</label>
              <input
                type="text"
                value={name}
                onChange={(e) => setName(e.target.value)}
                placeholder="e.g. Partitiivi"
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500"
                required
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Description</label>
              <textarea
                value={description}
                onChange={(e) => setDescription(e.target.value)}
                placeholder="Brief explanation..."
                rows={2}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500"
              />
            </div>
            <button
              type="submit"
              disabled={createMutation.isPending}
              className="px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 disabled:opacity-50"
            >
              {createMutation.isPending ? 'Adding...' : 'Add Concept'}
            </button>
          </form>
          {createMutation.isError && (
            <p className="mt-2 text-sm text-red-600">{String(createMutation.error)}</p>
          )}
        </div>

        {/* List */}
        <div className="bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden">
          <h2 className="font-semibold text-gray-900 p-6 pb-0">Concepts ({concepts.length})</h2>
          {concepts.length === 0 ? (
            <div className="p-8 text-center text-gray-500">No concepts yet. Add one above.</div>
          ) : (
            <div className="divide-y divide-gray-100">
              {concepts.map((c) => (
                <div key={c.id} className="p-6 hover:bg-gray-50/50">
                  {editingId === c.id ? (
                    <div className="space-y-3">
                      <input
                        value={editName}
                        onChange={(e) => setEditName(e.target.value)}
                        className="w-full px-3 py-2 border rounded"
                      />
                      <textarea
                        value={editDesc}
                        onChange={(e) => setEditDesc(e.target.value)}
                        rows={2}
                        className="w-full px-3 py-2 border rounded"
                      />
                      <div className="flex gap-2">
                        <button
                          onClick={saveEdit}
                          disabled={updateMutation.isPending}
                          className="px-3 py-1 bg-indigo-600 text-white rounded text-sm"
                        >
                          Save
                        </button>
                        <button
                          onClick={() => setEditingId(null)}
                          className="px-3 py-1 bg-gray-200 rounded text-sm"
                        >
                          Cancel
                        </button>
                      </div>
                    </div>
                  ) : (
                    <div className="flex justify-between items-start">
                      <div>
                        <h3 className="font-medium text-gray-900">{c.name}</h3>
                        {c.description && (
                          <p className="text-sm text-gray-600 mt-1">{c.description}</p>
                        )}
                        <div className="flex gap-2 mt-2">
                          {c.tags?.map((t) => (
                            <span key={t} className="text-xs px-2 py-0.5 bg-gray-100 rounded">
                              {t}
                            </span>
                          ))}
                          {c.priority != null && (
                            <span className="text-xs text-gray-500">priority: {c.priority.toFixed(2)}</span>
                          )}
                        </div>
                      </div>
                      <div className="flex gap-2">
                        <button
                          onClick={() => startEdit(c)}
                          className="text-sm text-indigo-600 hover:text-indigo-700"
                        >
                          Edit
                        </button>
                        <button
                          onClick={() => deleteMutation.mutate(c.id)}
                          disabled={deleteMutation.isPending}
                          className="text-sm text-red-600 hover:text-red-700"
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
