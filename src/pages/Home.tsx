import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { Link } from 'react-router-dom'
import { wordAPI } from '../lib/api'
import { UserWord } from '../lib/types'
import WordLookup from '../components/WordLookup'
import Wordbook from '../components/Wordbook'
import AddWord from '../components/AddWord'
import WordList from '../components/WordList'
import BulkImport from '../components/BulkImport'
import LoadingSpinner from '../components/LoadingSpinner'

export default function Home() {
  const userId = 'user-1'
  const [activeView, setActiveView] = useState<'lookup' | 'wordbook' | 'add' | 'vocabulary' | 'bulk'>('lookup')

  const { data: userWords = [], isLoading } = useQuery({
    queryKey: ['userWords', userId],
    queryFn: () => wordAPI.getUserWords(userId),
  })

  // Calculate word stats
  const stats = {
    total: userWords.length,
    recent: userWords.filter((w: UserWord) => w.status === 'Recent').length,
    learning: userWords.filter((w: UserWord) => w.status === 'Learning').length,
    mastered: userWords.filter((w: UserWord) => w.status === 'Mastered').length,
  }

  if (isLoading && activeView === 'wordbook' && userWords.length === 0) {
    return <LoadingSpinner message="Loading..." />
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
      {/* Header */}
      <div className="bg-white shadow-sm sticky top-0 z-10">
        <div className="max-w-7xl mx-auto px-8 py-6 flex justify-between items-center">
          <div>
            <h1 className="text-4xl font-bold text-gray-900 mb-2">Learn Finnish</h1>
            <p className="text-lg text-gray-600">Search words, build your wordbook, track progress</p>
          </div>
          <div className="flex gap-2">
            <Link
              to={`${import.meta.env.BASE_URL?.replace(/\/$/, '') || ''}/concepts`}
              className="px-4 py-2 text-indigo-600 hover:bg-indigo-50 rounded-lg font-medium"
            >
              Concepts
            </Link>
            <Link
              to={`${import.meta.env.BASE_URL?.replace(/\/$/, '') || ''}/dashboard`}
              className="px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 font-medium"
            >
              Dashboard
            </Link>
          </div>
        </div>
      </div>

      {/* Navigation Tabs */}
      <div className="bg-white border-b border-gray-200 sticky top-20 z-10">
        <div className="max-w-7xl mx-auto px-8">
          <div className="flex gap-0">
            <button
              onClick={() => setActiveView('lookup')}
              className={`px-6 py-4 font-medium border-b-2 transition ${
                activeView === 'lookup'
                  ? 'border-indigo-600 text-indigo-600'
                  : 'border-transparent text-gray-600 hover:text-gray-900'
              }`}
            >
              Word Lookup
            </button>
            <button
              onClick={() => setActiveView('wordbook')}
              className={`px-6 py-4 font-medium border-b-2 transition relative ${
                activeView === 'wordbook'
                  ? 'border-indigo-600 text-indigo-600'
                  : 'border-transparent text-gray-600 hover:text-gray-900'
              }`}
            >
              My Wordbook
              {stats.total > 0 && (
                <span className="absolute top-2 right-1 bg-indigo-600 text-white text-xs font-bold rounded-full w-5 h-5 flex items-center justify-center">
                  {stats.total}
                </span>
              )}
            </button>
            <button
              onClick={() => setActiveView('add')}
              className={`px-6 py-4 font-medium border-b-2 transition ${
                activeView === 'add'
                  ? 'border-indigo-600 text-indigo-600'
                  : 'border-transparent text-gray-600 hover:text-gray-900'
              }`}
            >
              Add Word
            </button>
            <button
              onClick={() => setActiveView('vocabulary')}
              className={`px-6 py-4 font-medium border-b-2 transition ${
                activeView === 'vocabulary'
                  ? 'border-indigo-600 text-indigo-600'
                  : 'border-transparent text-gray-600 hover:text-gray-900'
              }`}
            >
              Vocabulary
            </button>
            <button
              onClick={() => setActiveView('bulk')}
              className={`px-6 py-4 font-medium border-b-2 transition ${
                activeView === 'bulk'
                  ? 'border-indigo-600 text-indigo-600'
                  : 'border-transparent text-gray-600 hover:text-gray-900'
              }`}
            >
              Bulk Import
            </button>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="max-w-7xl mx-auto px-8 py-8 pb-20">
        {activeView === 'lookup' ? (
          <div className="space-y-8">
            <WordLookup userId={userId} />

            {/* Quick Stats */}
            {stats.total > 0 && (
              <div className="bg-white rounded-lg shadow p-6 border-t-4 border-indigo-600">
                <h3 className="text-lg font-semibold text-gray-900 mb-4">Your Progress</h3>
                <div className="grid grid-cols-3 gap-4">
                  <div className="text-center p-4 bg-blue-50 rounded-lg">
                    <p className="text-3xl font-bold text-blue-600">{stats.recent}</p>
                    <p className="text-sm text-gray-600 mt-1">Recent</p>
                  </div>
                  <div className="text-center p-4 bg-yellow-50 rounded-lg">
                    <p className="text-3xl font-bold text-yellow-600">{stats.learning}</p>
                    <p className="text-sm text-gray-600 mt-1">Learning</p>
                  </div>
                  <div className="text-center p-4 bg-green-50 rounded-lg">
                    <p className="text-3xl font-bold text-green-600">{stats.mastered}</p>
                    <p className="text-sm text-gray-600 mt-1">Mastered</p>
                  </div>
                </div>
              </div>
            )}
          </div>
        ) : activeView === 'wordbook' ? (
          <Wordbook userId={userId} />
        ) : activeView === 'add' ? (
          <AddWord />
        ) : activeView === 'vocabulary' ? (
          <WordList />
        ) : (
          <BulkImport />
        )}
      </div>
    </div>
  )
}
