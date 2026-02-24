import { Link } from 'react-router-dom'

const base = import.meta.env.BASE_URL?.replace(/\/$/, '') || ''

export default function Home() {
  return (
    <div
      className="min-h-screen relative overflow-hidden"
      style={{
        background: 'linear-gradient(135deg, #0f172a 0%, #1e293b 50%, #334155 100%)',
      }}
    >
      {/* Animated background glow */}
      <div
        className="absolute inset-0 pointer-events-none"
        style={{
          width: '200%',
          height: '200%',
          background: 'radial-gradient(circle, rgba(37, 99, 235, 0.1) 0%, transparent 70%)',
          animation: 'pulse 8s ease-in-out infinite',
        }}
      />
      <style>{`
        @keyframes pulse {
          0%, 100% { transform: scale(1) translate(-25%, -25%); opacity: 0.3; }
          50% { transform: scale(1.1) translate(-25%, -25%); opacity: 0.5; }
        }
      `}</style>

      <div className="relative z-10 max-w-4xl mx-auto px-6 py-20 flex flex-col min-h-screen justify-center">
        <div className="text-center mb-12">
          <h1
            className="text-4xl sm:text-5xl md:text-6xl font-extrabold mb-3"
            style={{
              background: 'linear-gradient(135deg, #ffffff 0%, #94a3b8 100%)',
              WebkitBackgroundClip: 'text',
              WebkitTextFillColor: 'transparent',
              backgroundClip: 'text',
              letterSpacing: '-0.02em',
            }}
          >
            Learning Finnish
          </h1>
          <p className="text-lg sm:text-xl text-slate-400 font-light">
            Manage your vocabulary and grammatical concepts
          </p>
        </div>

        <div className="grid gap-6 sm:grid-cols-3">
          <Link
            to={`${base}/add-words`}
            className="block p-8 rounded-3xl text-center group transition-all duration-400 hover:-translate-y-3 relative overflow-hidden"
            style={{
              background: 'rgba(255, 255, 255, 0.03)',
              backdropFilter: 'blur(20px)',
              border: '1px solid rgba(255, 255, 255, 0.1)',
              boxShadow: 'none',
            }}
            onMouseEnter={(e) => {
              e.currentTarget.style.background = 'rgba(255, 255, 255, 0.06)'
              e.currentTarget.style.borderColor = 'rgba(255, 255, 255, 0.2)'
              e.currentTarget.style.boxShadow = '0 25px 50px -12px rgba(0, 0, 0, 0.5), 0 0 80px rgba(37, 99, 235, 0.15)'
            }}
            onMouseLeave={(e) => {
              e.currentTarget.style.background = 'rgba(255, 255, 255, 0.03)'
              e.currentTarget.style.borderColor = 'rgba(255, 255, 255, 0.1)'
              e.currentTarget.style.boxShadow = 'none'
            }}
          >
            <div className="absolute top-0 left-0 right-0 h-1 bg-gradient-to-r from-blue-600 to-sky-500 scale-x-0 group-hover:scale-x-100 transition-transform duration-400 origin-left" />
            <div className="text-4xl mb-4 text-sky-400 group-hover:scale-110 group-hover:rotate-6 transition-transform duration-400">
              <i className="bi bi-plus-circle" />
            </div>
            <h2 className="text-xl font-bold text-white mb-2">Enter Words</h2>
            <p className="text-slate-400 text-sm leading-relaxed mb-4">
              Add new Finnish words to the database with translations and inflections
            </p>
            <span className="inline-flex items-center gap-2 text-sky-400 font-semibold group-hover:gap-3 transition-all">
              Explore <i className="bi bi-arrow-right" />
            </span>
          </Link>

          <Link
            to={`${base}/words`}
            className="block p-8 rounded-3xl text-center group transition-all duration-400 hover:-translate-y-3 relative overflow-hidden"
            style={{
              background: 'rgba(255, 255, 255, 0.03)',
              backdropFilter: 'blur(20px)',
              border: '1px solid rgba(255, 255, 255, 0.1)',
              boxShadow: 'none',
            }}
            onMouseEnter={(e) => {
              e.currentTarget.style.background = 'rgba(255, 255, 255, 0.06)'
              e.currentTarget.style.borderColor = 'rgba(255, 255, 255, 0.2)'
              e.currentTarget.style.boxShadow = '0 25px 50px -12px rgba(0, 0, 0, 0.5), 0 0 80px rgba(37, 99, 235, 0.15)'
            }}
            onMouseLeave={(e) => {
              e.currentTarget.style.background = 'rgba(255, 255, 255, 0.03)'
              e.currentTarget.style.borderColor = 'rgba(255, 255, 255, 0.1)'
              e.currentTarget.style.boxShadow = 'none'
            }}
          >
            <div className="absolute top-0 left-0 right-0 h-1 bg-gradient-to-r from-blue-600 to-sky-500 scale-x-0 group-hover:scale-x-100 transition-transform duration-400 origin-left" />
            <div className="text-4xl mb-4 text-sky-400 group-hover:scale-110 group-hover:rotate-6 transition-transform duration-400">
              <i className="bi bi-book" />
            </div>
            <h2 className="text-xl font-bold text-white mb-2">See Words</h2>
            <p className="text-slate-400 text-sm leading-relaxed mb-4">
              Browse all words in the database with search and filters
            </p>
            <span className="inline-flex items-center gap-2 text-sky-400 font-semibold group-hover:gap-3 transition-all">
              Explore <i className="bi bi-arrow-right" />
            </span>
          </Link>

          <Link
            to={`${base}/concepts`}
            className="block p-8 rounded-3xl text-center group transition-all duration-400 hover:-translate-y-3 relative overflow-hidden"
            style={{
              background: 'rgba(255, 255, 255, 0.03)',
              backdropFilter: 'blur(20px)',
              border: '1px solid rgba(255, 255, 255, 0.1)',
              boxShadow: 'none',
            }}
            onMouseEnter={(e) => {
              e.currentTarget.style.background = 'rgba(255, 255, 255, 0.06)'
              e.currentTarget.style.borderColor = 'rgba(255, 255, 255, 0.2)'
              e.currentTarget.style.boxShadow = '0 25px 50px -12px rgba(0, 0, 0, 0.5), 0 0 80px rgba(37, 99, 235, 0.15)'
            }}
            onMouseLeave={(e) => {
              e.currentTarget.style.background = 'rgba(255, 255, 255, 0.03)'
              e.currentTarget.style.borderColor = 'rgba(255, 255, 255, 0.1)'
              e.currentTarget.style.boxShadow = 'none'
            }}
          >
            <div className="absolute top-0 left-0 right-0 h-1 bg-gradient-to-r from-blue-600 to-sky-500 scale-x-0 group-hover:scale-x-100 transition-transform duration-400 origin-left" />
            <div className="text-4xl mb-4 text-sky-400 group-hover:scale-110 group-hover:rotate-6 transition-transform duration-400">
              <i className="bi bi-journal-bookmark" />
            </div>
            <h2 className="text-xl font-bold text-white mb-2">See Concepts</h2>
            <p className="text-slate-400 text-sm leading-relaxed mb-4">
              View and manage grammatical concepts (e.g. Partitiivi, Verbityypit)
            </p>
            <span className="inline-flex items-center gap-2 text-sky-400 font-semibold group-hover:gap-3 transition-all">
              Explore <i className="bi bi-arrow-right" />
            </span>
          </Link>
        </div>
      </div>
    </div>
  )
}
