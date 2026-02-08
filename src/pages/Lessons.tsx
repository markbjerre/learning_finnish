import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { useNavigate } from 'react-router-dom'
import { lessonsAPI } from '../lib/api'
import { Lesson } from '../lib/types'
import LoadingSpinner from '../components/LoadingSpinner'

export default function Lessons() {
  const navigate = useNavigate()
  const [selectedDifficulty, setSelectedDifficulty] = useState<string | undefined>()

  const lessonsQuery = useQuery({
    queryKey: ['lessons', selectedDifficulty],
    queryFn: () => lessonsAPI.getAll(selectedDifficulty),
    staleTime: 5 * 60 * 1000,
  })

  const lessons = lessonsQuery.data || []

  const difficultyColors: Record<string, { bg: string; text: string; border: string }> = {
    beginner: { bg: 'bg-green-50', text: 'text-green-700', border: 'border-green-200' },
    intermediate: { bg: 'bg-yellow-50', text: 'text-yellow-700', border: 'border-yellow-200' },
    advanced: { bg: 'bg-red-50', text: 'text-red-700', border: 'border-red-200' },
  }

  if (lessonsQuery.isPending) {
    return <LoadingSpinner message="Loading lessons..." />
  }

  const handleStartLesson = (lesson: Lesson) => {
    navigate(`/lesson/${lesson.id}`)
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
      {/* Header */}
      <div className="bg-white shadow-sm">
        <div className="max-w-7xl mx-auto px-8 py-12">
          <h1 className="text-4xl font-bold text-gray-900 mb-2">Learn Finnish</h1>
          <p className="text-lg text-gray-600">Master the language step by step with flashcard tests</p>
        </div>
      </div>

      {/* Content */}
      <div className="max-w-7xl mx-auto px-8 py-8 pb-20">
        {/* Difficulty Filter */}
        <div className="mb-8">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">Filter by Difficulty</h2>
          <div className="flex gap-2 flex-wrap">
            <button
              onClick={() => setSelectedDifficulty(undefined)}
              className={`px-4 py-2 rounded-lg font-medium transition ${
                selectedDifficulty === undefined
                  ? 'bg-indigo-600 text-white'
                  : 'bg-white text-gray-700 border border-gray-300 hover:bg-gray-50'
              }`}
            >
              All Levels
            </button>
            {['beginner', 'intermediate', 'advanced'].map((difficulty) => (
              <button
                key={difficulty}
                onClick={() => setSelectedDifficulty(difficulty)}
                className={`px-4 py-2 rounded-lg font-medium transition capitalize ${
                  selectedDifficulty === difficulty
                    ? 'bg-indigo-600 text-white'
                    : 'bg-white text-gray-700 border border-gray-300 hover:bg-gray-50'
                }`}
              >
                {difficulty}
              </button>
            ))}
          </div>
        </div>

        {/* Lessons Grid */}
        {lessonsQuery.isError ? (
          <div className="bg-red-50 border border-red-200 rounded-lg p-6 text-center">
            <h2 className="text-2xl font-bold text-red-700 mb-2">Failed to Load Lessons</h2>
            <p className="text-red-600 mb-4">
              {lessonsQuery.error instanceof Error
                ? lessonsQuery.error.message
                : 'An error occurred while loading lessons'}
            </p>
            <button
              onClick={() => lessonsQuery.refetch()}
              className="px-6 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition"
            >
              Try Again
            </button>
          </div>
        ) : lessons.length === 0 ? (
          <div className="bg-white rounded-lg shadow p-12 text-center">
            <p className="text-gray-600 text-lg">No lessons found for the selected difficulty level.</p>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {lessons.map((lesson: Lesson) => {
              const colors = difficultyColors[lesson.difficulty] || difficultyColors.beginner
              return (
                <div
                  key={lesson.id}
                  className={`${colors.bg} border-2 ${colors.border} rounded-lg p-6 hover:shadow-lg transition cursor-pointer`}
                  onClick={() => handleStartLesson(lesson)}
                >
                  <div className="mb-4">
                    <h3 className="text-xl font-bold text-gray-900">{lesson.title}</h3>
                    <p className={`text-sm font-medium mt-2 ${colors.text} capitalize`}>{lesson.difficulty}</p>
                  </div>
                  <p className="text-gray-600 text-sm mb-4">{lesson.description}</p>
                  <div className="flex items-center justify-between">
                    <span className="text-sm text-gray-600">
                      ⏱ {lesson.estimated_duration_minutes} minutes
                    </span>
                    <button
                      className="px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition text-sm font-medium"
                      onClick={(e) => {
                        e.stopPropagation()
                        handleStartLesson(lesson)
                      }}
                    >
                      Start Test
                    </button>
                  </div>
                </div>
              )
            })}
          </div>
        )}
      </div>
    </div>
  )
}
