import { useState, useEffect } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { wordAPI } from '../lib/api'
import { UserWord, WordStatus } from '../lib/types'
import LoadingSpinner from './LoadingSpinner'

interface WordbookProps {
  userId: string
}

const statusColors: Record<WordStatus, { bg: string; text: string; badge: string }> = {
  Recent: { bg: 'bg-blue-50', text: 'text-blue-700', badge: 'bg-blue-100 text-blue-800' },
  Learning: { bg: 'bg-yellow-50', text: 'text-yellow-700', badge: 'bg-yellow-100 text-yellow-800' },
  Mastered: { bg: 'bg-green-50', text: 'text-green-700', badge: 'bg-green-100 text-green-800' },
}

export default function Wordbook({ userId }: WordbookProps) {
  const [selectedStatus, setSelectedStatus] = useState<WordStatus | 'All'>('All')
  const queryClient = useQueryClient()

  const { data: allWords = [], isLoading, error } = useQuery({
    queryKey: ['userWords', userId],
    queryFn: () => wordAPI.getUserWords(userId),
  })

  // Filter words by selected status
  const filteredWords = selectedStatus === 'All' 
    ? allWords 
    : allWords.filter(w => w.status === selectedStatus)

  // Mutation for updating word status
  const updateStatusMutation = useMutation({
    mutationFn: ({ wordId, status, proficiency }: { wordId: string; status: WordStatus; proficiency?: number }) =>
      wordAPI.updateWordStatus(userId, wordId, status, proficiency),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['userWords', userId] })
    },
  })

  // Mutation for removing word
  const removeWordMutation = useMutation({
    mutationFn: (wordId: string) => wordAPI.removeWord(userId, wordId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['userWords', userId] })
    },
  })

  const getNextStatus = (currentStatus: WordStatus): WordStatus => {
    const statuses: WordStatus[] = ['Recent', 'Learning', 'Mastered']
    const currentIndex = statuses.indexOf(currentStatus)
    const nextIndex = (currentIndex + 1) % statuses.length
    return statuses[nextIndex]
  }

  if (isLoading) {
    return <LoadingSpinner message="Loading your wordbook..." />
  }

  if (error) {
    return (
      <div className="bg-red-50 border border-red-200 rounded-lg p-6">
        <p className="text-red-700">Failed to load wordbook</p>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Header and Stats */}
      <div className="bg-white rounded-lg shadow p-6">
        <h2 className="text-2xl font-bold text-gray-900 mb-4">My Wordbook</h2>
        <div className="grid grid-cols-3 gap-4">
          <div>
            <div className="text-3xl font-bold text-blue-600">{allWords.filter(w => w.status === 'Recent').length}</div>
            <p className="text-gray-600 text-sm mt-1">Recent</p>
          </div>
          <div>
            <div className="text-3xl font-bold text-yellow-600">{allWords.filter(w => w.status === 'Learning').length}</div>
            <p className="text-gray-600 text-sm mt-1">Learning</p>
          </div>
          <div>
            <div className="text-3xl font-bold text-green-600">{allWords.filter(w => w.status === 'Mastered').length}</div>
            <p className="text-gray-600 text-sm mt-1">Mastered</p>
          </div>
        </div>
      </div>

      {/* Filter Buttons */}
      <div className="flex gap-2 flex-wrap">
        {(['All', 'Recent', 'Learning', 'Mastered'] as const).map((status) => (
          <button
            key={status}
            onClick={() => setSelectedStatus(status)}
            className={`px-4 py-2 rounded-lg font-medium transition ${
              selectedStatus === status
                ? 'bg-indigo-600 text-white'
                : 'bg-white text-gray-700 border border-gray-300 hover:bg-gray-50'
            }`}
          >
            {status} ({status === 'All' ? allWords.length : allWords.filter(w => w.status === status).length})
          </button>
        ))}
      </div>

      {/* Words Grid */}
      {filteredWords.length === 0 ? (
        <div className="bg-white rounded-lg shadow p-12 text-center">
          <p className="text-gray-600 text-lg">
            {allWords.length === 0
              ? 'No words in your wordbook yet. Search for a word and add it!'
              : `No words with status "${selectedStatus}"`}
          </p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {filteredWords.map((word: UserWord) => {
            const colors = statusColors[word.status]
            return (
              <div
                key={word.id}
                className={`${colors.bg} rounded-lg p-6 border-l-4 ${
                  word.status === 'Recent'
                    ? 'border-blue-500'
                    : word.status === 'Learning'
                      ? 'border-yellow-500'
                      : 'border-green-500'
                }`}
              >
                {/* Word Header */}
                <div className="mb-4">
                  <h3 className="text-lg font-bold text-gray-900">{word.finnish_word}</h3>
                  <p className="text-gray-600">{word.english_translation}</p>
                  <span className={`inline-block mt-2 px-3 py-1 rounded-full text-xs font-semibold ${colors.badge}`}>
                    {word.status}
                  </span>
                </div>

                {/* Proficiency Bar */}
                <div className="mb-4">
                  <div className="flex justify-between text-sm text-gray-600 mb-1">
                    <span>Proficiency</span>
                    <span>{word.proficiency}%</span>
                  </div>
                  <div className="w-full bg-gray-300 rounded-full h-2">
                    <div
                      className={`h-2 rounded-full transition-all ${
                        word.status === 'Recent'
                          ? 'bg-blue-500'
                          : word.status === 'Learning'
                            ? 'bg-yellow-500'
                            : 'bg-green-500'
                      }`}
                      style={{ width: `${word.proficiency}%` }}
                    />
                  </div>
                </div>

                {/* Action Buttons */}
                <div className="flex gap-2">
                  <button
                    onClick={() => {
                      const nextStatus = getNextStatus(word.status)
                      const newProficiency =
                        word.status === 'Recent' ? 40 : word.status === 'Learning' ? 80 : word.proficiency
                      updateStatusMutation.mutate({
                        wordId: word.id,
                        status: nextStatus,
                        proficiency: newProficiency,
                      })
                    }}
                    disabled={updateStatusMutation.isPending}
                    className="flex-1 px-3 py-2 bg-indigo-600 text-white rounded text-sm hover:bg-indigo-700 transition disabled:opacity-50"
                  >
                    {updateStatusMutation.isPending ? '...' : 'Next'}
                  </button>
                  <button
                    onClick={() => removeWordMutation.mutate(word.id)}
                    disabled={removeWordMutation.isPending}
                    className="px-3 py-2 bg-red-600 text-white rounded text-sm hover:bg-red-700 transition disabled:opacity-50"
                  >
                    {removeWordMutation.isPending ? '...' : 'Remove'}
                  </button>
                </div>
              </div>
            )
          })}
        </div>
      )}
    </div>
  )
}
