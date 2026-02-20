import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { Link } from 'react-router-dom'
import { statsAPI, exerciseAPI } from '../lib/api'
import LoadingSpinner from '../components/LoadingSpinner'

export default function Dashboard() {
  const queryClient = useQueryClient()

  const { data: stats, isLoading } = useQuery({
    queryKey: ['stats'],
    queryFn: () => statsAPI.getStats(),
  })

  const { data: history = [], isLoading: historyLoading } = useQuery({
    queryKey: ['exerciseHistory'],
    queryFn: () => exerciseAPI.getHistory(15, 0),
  })

  const { data: chartData = [] } = useQuery({
    queryKey: ['statsChart'],
    queryFn: () => statsAPI.getChartData(14),
  })

  const updateLevel = useMutation({
    mutationFn: (level: number) => statsAPI.updateSettings({ level }),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['stats'] }),
  })

  if (isLoading) {
    return <LoadingSpinner message="Loading dashboard..." />
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-indigo-50">
      <div className="max-w-5xl mx-auto px-6 py-8">
        <div className="flex items-center justify-between mb-8">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">Progress Dashboard</h1>
            <p className="text-gray-600 mt-1">Spaced repetition stats & exercise history</p>
          </div>
          <Link
            to={import.meta.env.BASE_URL?.replace(/\/$/, '') || '/'}
            className="text-indigo-600 hover:text-indigo-700 font-medium"
          >
            ← Back to Home
          </Link>
        </div>

        {/* Stats grid */}
        {stats && (
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8">
            <div className="bg-white rounded-xl shadow-sm p-5 border border-gray-100">
              <p className="text-sm text-gray-500 uppercase tracking-wide">Total Words</p>
              <p className="text-2xl font-bold text-gray-900 mt-1">{stats.total_words}</p>
            </div>
            <div className="bg-white rounded-xl shadow-sm p-5 border border-gray-100">
              <p className="text-sm text-gray-500 uppercase tracking-wide">Mastered</p>
              <p className="text-2xl font-bold text-green-600 mt-1">{stats.mastered}</p>
              <p className="text-xs text-gray-500 mt-1">{stats.mastery_percent}%</p>
            </div>
            <div className="bg-white rounded-xl shadow-sm p-5 border border-gray-100">
              <p className="text-sm text-gray-500 uppercase tracking-wide">Learning</p>
              <p className="text-2xl font-bold text-amber-600 mt-1">{stats.learning}</p>
            </div>
            <div className="bg-white rounded-xl shadow-sm p-5 border border-gray-100">
              <p className="text-sm text-gray-500 uppercase tracking-wide">Needs Work</p>
              <p className="text-2xl font-bold text-red-600 mt-1">{stats.needs_work}</p>
            </div>
            {stats.streak_days != null && stats.streak_days > 0 && (
              <div className="bg-white rounded-xl shadow-sm p-5 border border-gray-100">
                <p className="text-sm text-gray-500 uppercase tracking-wide">Streak</p>
                <p className="text-2xl font-bold text-amber-600 mt-1">{stats.streak_days} days</p>
              </div>
            )}
          </div>
        )}

        {/* Level + exercises */}
        {stats && (
          <div className="grid md:grid-cols-2 gap-6 mb-8">
            <div className="bg-white rounded-xl shadow-sm p-6 border border-gray-100">
              <h3 className="font-semibold text-gray-900 mb-3">Level</h3>
              <div className="flex items-center gap-4">
                <span className="text-4xl font-bold text-indigo-600">{stats.level}</span>
                <span className="text-gray-500">/ 100</span>
                <div className="flex gap-2">
                  <button
                    onClick={() => updateLevel.mutate(Math.max(1, stats.level - 1))}
                    className="px-3 py-1 text-sm bg-gray-100 hover:bg-gray-200 rounded"
                  >
                    −
                  </button>
                  <button
                    onClick={() => updateLevel.mutate(Math.min(100, stats.level + 1))}
                    className="px-3 py-1 text-sm bg-gray-100 hover:bg-gray-200 rounded"
                  >
                    +
                  </button>
                </div>
              </div>
              <p className="text-sm text-gray-500 mt-2">Adjust difficulty for OpenClaw exercises</p>
            </div>
            <div className="bg-white rounded-xl shadow-sm p-6 border border-gray-100">
              <h3 className="font-semibold text-gray-900 mb-3">Exercises</h3>
              <p className="text-2xl font-bold text-indigo-600">{stats.total_exercises}</p>
              <p className="text-sm text-gray-500 mt-1">Total completed</p>
              {stats.avg_score != null && (
                <p className="text-sm text-gray-600 mt-2">Avg score: {stats.avg_score.toFixed(1)}/10</p>
              )}
            </div>
          </div>
        )}

        {/* Progress chart */}
        {(chartData.length > 0 || stats?.total_exercises) && (
          <div className="bg-white rounded-xl shadow-sm p-6 border border-gray-100 mb-8">
            <h3 className="font-semibold text-gray-900 mb-4">Exercises per day (last 14 days)</h3>
            {chartData.length > 0 ? (
              <div className="flex items-end gap-1 h-24">
                {chartData.map((d) => {
                  const maxCount = Math.max(...chartData.map((x) => x.count), 1)
                  const h = (d.count / maxCount) * 100
                  return (
                    <div key={d.date} className="flex-1 flex flex-col items-center gap-1">
                      <div
                        className="w-full bg-indigo-500 rounded-t min-h-[4px]"
                        style={{ height: `${Math.max(h, 4)}%` }}
                        title={`${d.date}: ${d.count}`}
                      />
                      <span className="text-xs text-gray-500 truncate max-w-full">
                        {new Date(d.date).toLocaleDateString(undefined, { month: 'short', day: 'numeric' })}
                      </span>
                    </div>
                  )
                })}
              </div>
            ) : (
              <p className="text-gray-500 text-sm">Complete exercises to see your progress chart.</p>
            )}
          </div>
        )}

        {/* Exercise history */}
        <div className="bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden">
          <h3 className="font-semibold text-gray-900 p-6 pb-0">Recent Exercises</h3>
          {historyLoading ? (
            <div className="p-8 text-center text-gray-500">Loading...</div>
          ) : history.length === 0 ? (
            <div className="p-8 text-center text-gray-500">
              No exercises yet. Complete exercises via OpenClaw to see history here.
            </div>
          ) : (
            <div className="divide-y divide-gray-100">
              {history.map((entry) => (
                <div key={entry.id} className="p-6 hover:bg-gray-50/50">
                  <div className="flex justify-between items-start">
                    <div>
                      <p className="font-medium text-gray-900">
                        {entry.exercise_type} {entry.level_used != null && `(level ${entry.level_used})`}
                      </p>
                      {entry.prompt_sent && (
                        <p className="text-sm text-gray-600 mt-1">{entry.prompt_sent}</p>
                      )}
                      {entry.user_response && (
                        <p className="text-sm text-indigo-600 mt-1">Your reply: {entry.user_response}</p>
                      )}
                      {entry.ai_feedback && (
                        <p className="text-sm text-gray-500 mt-2 italic">{entry.ai_feedback}</p>
                      )}
                    </div>
                    <span className="text-xs text-gray-400">
                      {entry.created_at ? new Date(entry.created_at).toLocaleDateString() : ''}
                    </span>
                  </div>
                  {entry.word_scores?.length > 0 && (
                    <div className="flex flex-wrap gap-2 mt-3">
                      {entry.word_scores.map((ws, i) => (
                        <span
                          key={i}
                          className={`text-xs px-2 py-1 rounded ${
                            ws.score >= 7 ? 'bg-green-100 text-green-800' : ws.score >= 4 ? 'bg-amber-100 text-amber-800' : 'bg-red-100 text-red-800'
                          }`}
                        >
                          {ws.score}/10
                        </span>
                      ))}
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
