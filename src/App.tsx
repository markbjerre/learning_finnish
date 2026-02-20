import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom'
import { useParams } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
import Home from './pages/Home'
import Lessons from './pages/Lessons'
import Dashboard from './pages/Dashboard'
import Concepts from './pages/Concepts'
import FlashcardTest from './components/FlashcardTest'
import { lessonsAPI } from './lib/api'
import LoadingSpinner from './components/LoadingSpinner'

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 1000 * 60 * 5, // 5 minutes
      gcTime: 1000 * 60 * 10, // 10 minutes
      retry: 1,
    },
  },
})

// Lesson detail page component
function LessonDetailPage() {
  const { id } = useParams<{ id: string }>()
  const lessonQuery = useQuery({
    queryKey: ['lesson', id],
    queryFn: async () => {
      const lessons = await lessonsAPI.getAll()
      return lessons.find((l) => l.id === id)
    },
  })

  const handleTestComplete = () => {
    const base = import.meta.env.BASE_URL?.replace(/\/$/, '') || ''
    window.location.href = `${base}/lessons`
  }

  if (lessonQuery.isPending) {
    return <LoadingSpinner message="Loading lesson..." />
  }

  if (!lessonQuery.data) {
    return (
      <div className="min-h-screen bg-gray-100 flex items-center justify-center p-8">
        <div className="text-center">
          <h1 className="text-3xl font-bold text-gray-900 mb-4">Lesson not found</h1>
          <a href={`${import.meta.env.BASE_URL?.replace(/\/$/, '') || ''}/lessons`} className="text-indigo-600 hover:text-indigo-700">
            Back to lessons
          </a>
        </div>
      </div>
    )
  }

  return <FlashcardTest lesson={lessonQuery.data} onComplete={handleTestComplete} />
}

export default function App() {
  const basename = import.meta.env.BASE_URL?.replace(/\/$/, '') || ''
  return (
    <QueryClientProvider client={queryClient}>
      <Router basename={basename}>
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/dashboard" element={<Dashboard />} />
          <Route path="/concepts" element={<Concepts />} />
          <Route path="/lessons" element={<Lessons />} />
          <Route path="/lesson/:id" element={<LessonDetailPage />} />
        </Routes>
      </Router>
    </QueryClientProvider>
  )
}
