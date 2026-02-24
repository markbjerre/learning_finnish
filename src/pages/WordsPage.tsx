import { Link } from 'react-router-dom'
import WordList from '../components/WordList'

const base = import.meta.env.BASE_URL?.replace(/\/$/, '') || ''

export default function WordsPage() {
  return (
    <div
      className="min-h-screen"
      style={{
        background: 'linear-gradient(135deg, #0f172a 0%, #1e293b 50%, #334155 100%)',
      }}
    >
      <div className="max-w-6xl mx-auto px-6 py-8">
        <div className="flex items-center justify-between mb-8">
          <h1 className="text-3xl font-bold text-white">See Words</h1>
          <Link
            to={base || '/'}
            className="text-sky-400 hover:text-sky-300 font-medium transition-colors"
          >
            <i className="bi bi-arrow-left mr-1" /> Back to Home
          </Link>
        </div>
        <WordList />
      </div>
    </div>
  )
}
