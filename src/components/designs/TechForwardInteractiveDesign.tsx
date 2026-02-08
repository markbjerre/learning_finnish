import { Link } from 'react-router-dom'
import { useState } from 'react'

export default function TechForwardInteractiveDesign() {
  const [searchText, setSearchText] = useState('hallo')
  const [selectedLanguage, setSelectedLanguage] = useState('finnish')
  const [hoveredCard, setHoveredCard] = useState<number | null>(null)

  return (
    <div className="min-h-screen bg-black text-white overflow-hidden relative">
      {/* Animated grid background */}
      <div className="fixed inset-0 pointer-events-none">
        <div className="absolute inset-0 bg-gradient-to-br from-cyan-500/10 via-transparent to-pink-500/10 opacity-50"></div>
        <div className="absolute top-1/3 left-1/4 w-96 h-96 bg-cyan-500/5 rounded-full blur-3xl animate-pulse"></div>
        <div className="absolute bottom-1/3 right-1/4 w-96 h-96 bg-pink-500/5 rounded-full blur-3xl" style={{ animation: 'pulse 4s cubic-bezier(0.4, 0, 0.6, 1) infinite 1s' }}></div>
      </div>

      <div className="relative z-10">
        {/* Header with glow */}
        <header className="border-b border-cyan-500/20 bg-black/80 backdrop-blur-xl sticky top-0 z-50">
          <div className="absolute inset-x-0 top-0 h-px bg-gradient-to-r from-transparent via-cyan-500 to-transparent"></div>
          <div className="max-w-full mx-auto px-6 py-6 flex items-center justify-between">
            <Link
              to="/"
              className="text-2xl font-black bg-gradient-to-r from-cyan-400 via-blue-400 to-pink-400 bg-clip-text text-transparent hover:from-cyan-300 hover:to-pink-300 transition-all duration-300"
            >
              Learning Finnish
            </Link>
            <Link
              to="/"
              className="px-4 py-2 text-sm font-bold text-cyan-300 border border-cyan-500/50 rounded-lg hover:border-cyan-400 hover:bg-cyan-500/10 transition-all duration-200 backdrop-blur"
            >
              ← Back
            </Link>
          </div>
        </header>

        {/* Main Content Grid */}
        <main className="p-6 max-w-7xl mx-auto">
          {/* Top Row - 2 Cards (Large) */}
          <div className="grid grid-cols-12 gap-4 mb-4">
            {/* Left Large Card - Search & Word */}
            <div className="col-span-12 lg:col-span-8 group/card">
              <div className="relative bg-gradient-to-br from-black via-slate-900 to-black border-2 border-cyan-500/30 hover:border-cyan-400/60 rounded-xl p-8 transition-all duration-300 hover:shadow-2xl hover:shadow-cyan-500/20 overflow-hidden h-full">
                {/* Glow effect on hover */}
                <div className="absolute inset-0 opacity-0 group-hover/card:opacity-100 transition-opacity duration-300">
                  <div className="absolute inset-0 bg-gradient-to-br from-cyan-500/5 to-pink-500/5 rounded-xl"></div>
                </div>

                <div className="relative z-10">
                  <h2 className="text-xs font-black text-cyan-400 uppercase tracking-widest mb-6">
                    Search Query
                  </h2>

                  {/* Input Section */}
                  <div className="space-y-4 mb-10 pb-10 border-b border-pink-500/20">
                    <input
                      type="text"
                      value={searchText}
                      onChange={(e) => setSearchText(e.target.value)}
                      placeholder="TYPE_WORD..."
                      className="w-full px-4 py-3 rounded-lg bg-black/50 border-2 border-cyan-500/30 text-cyan-300 placeholder-pink-500/50 font-mono text-sm focus:outline-none focus:border-cyan-400 transition-all"
                    />
                    <select
                      value={selectedLanguage}
                      onChange={(e) => setSelectedLanguage(e.target.value)}
                      className="w-full px-4 py-3 rounded-lg bg-black/50 border-2 border-pink-500/30 text-pink-300 font-mono text-sm focus:outline-none focus:border-pink-400 transition-all"
                    >
                      <option value="finnish">FINNISH</option>
                      <option value="english">ENGLISH</option>
                      <option value="danish">DANISH</option>
                    </select>
                  </div>

                  {/* Word Display */}
                  <div className="text-center">
                    <h3 className="text-6xl font-black bg-gradient-to-r from-cyan-400 to-pink-400 bg-clip-text text-transparent mb-4 font-mono">
                      {searchText.toUpperCase()}
                    </h3>
                    <p className="text-xl text-cyan-300 font-light mb-2">hello</p>
                    <span className="inline-block px-4 py-2 bg-cyan-500/20 text-cyan-300 text-xs font-black rounded-full border border-cyan-500/50 uppercase tracking-widest">
                      noun
                    </span>
                  </div>
                </div>
              </div>
            </div>

            {/* Right Card - Stats */}
            <div className="col-span-12 lg:col-span-4 group/card">
              <div className="relative bg-gradient-to-br from-black via-slate-900 to-black border-2 border-pink-500/30 hover:border-pink-400/60 rounded-xl p-8 transition-all duration-300 hover:shadow-2xl hover:shadow-pink-500/20 overflow-hidden h-full">
                <div className="absolute inset-0 opacity-0 group-hover/card:opacity-100 transition-opacity duration-300">
                  <div className="absolute inset-0 bg-gradient-to-br from-pink-500/5 to-purple-500/5 rounded-xl"></div>
                </div>

                <div className="relative z-10">
                  <h2 className="text-xs font-black text-pink-400 uppercase tracking-widest mb-8">
                    System Status
                  </h2>

                  <div className="space-y-6">
                    <div className="flex items-end gap-4">
                      <div>
                        <p className="text-4xl font-black text-pink-400 font-mono">3</p>
                        <p className="text-xs text-pink-300/60 uppercase tracking-widest font-bold">Words_Saved</p>
                      </div>
                      <div className="flex-1 h-1 bg-pink-500/20 rounded-full overflow-hidden">
                        <div className="h-full w-3/4 bg-gradient-to-r from-pink-500 to-purple-500 rounded-full shadow-lg shadow-pink-500/50"></div>
                      </div>
                    </div>

                    <div className="border-t border-pink-500/20 pt-6">
                      <p className="text-4xl font-black text-cyan-400 font-mono">72%</p>
                      <p className="text-xs text-cyan-300/60 uppercase tracking-widest font-bold">Learning_Progress</p>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>

          {/* Middle Row - 2 Cards */}
          <div className="grid grid-cols-12 gap-4 mb-4">
            {/* Grammatical Forms */}
            <div className="col-span-12 lg:col-span-6 group/card">
              <div className="relative bg-gradient-to-br from-black via-slate-900 to-black border-2 border-cyan-500/30 hover:border-cyan-400/60 rounded-xl p-8 transition-all duration-300 hover:shadow-2xl hover:shadow-cyan-500/20 overflow-hidden">
                <div className="absolute inset-0 opacity-0 group-hover/card:opacity-100 transition-opacity duration-300">
                  <div className="absolute inset-0 bg-gradient-to-br from-cyan-500/5 to-blue-500/5 rounded-xl"></div>
                </div>

                <div className="relative z-10">
                  <h2 className="text-xs font-black text-cyan-400 uppercase tracking-widest mb-6">
                    Grammatical_Forms
                  </h2>

                  <div className="grid grid-cols-2 gap-3">
                    {[
                      { case: 'Nominative', form: 'hallo' },
                      { case: 'Genitive', form: 'hallon' },
                      { case: 'Partitive', form: 'halloa' },
                      { case: 'Inessive', form: 'hallossa' },
                    ].map((item, idx) => (
                      <div
                        key={idx}
                        className="p-4 bg-black/50 border-2 border-cyan-500/20 hover:border-cyan-400/50 rounded-lg hover:shadow-lg hover:shadow-cyan-500/20 transition-all transform hover:scale-105 hover:bg-cyan-500/5"
                      >
                        <p className="text-xs text-cyan-300/70 uppercase font-bold tracking-wider mb-2">
                          {item.case}
                        </p>
                        <p className="text-xl text-cyan-300 font-black font-mono">
                          {item.form}
                        </p>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            </div>

            {/* Examples */}
            <div className="col-span-12 lg:col-span-6 group/card">
              <div className="relative bg-gradient-to-br from-black via-slate-900 to-black border-2 border-purple-500/30 hover:border-purple-400/60 rounded-xl p-8 transition-all duration-300 hover:shadow-2xl hover:shadow-purple-500/20 overflow-hidden">
                <div className="absolute inset-0 opacity-0 group-hover/card:opacity-100 transition-opacity duration-300">
                  <div className="absolute inset-0 bg-gradient-to-br from-purple-500/5 to-pink-500/5 rounded-xl"></div>
                </div>

                <div className="relative z-10">
                  <h2 className="text-xs font-black text-purple-400 uppercase tracking-widest mb-6">
                    Example_Sentences
                  </h2>

                  <div className="space-y-4">
                    {[
                      { finnish: '"Hallo, kuinka voitte?"', translation: 'How are you?' },
                      { finnish: '"Hallo maailma"', translation: 'Hello world' },
                    ].map((example, idx) => (
                      <div
                        key={idx}
                        className="p-4 bg-black/50 border-2 border-purple-500/20 hover:border-purple-400/50 rounded-lg hover:shadow-lg hover:shadow-purple-500/20 transition-all hover:bg-purple-500/5"
                      >
                        <p className="text-purple-300 font-mono text-sm mb-2">
                          {example.finnish}
                        </p>
                        <p className="text-xs text-purple-300/60 font-bold uppercase tracking-wider">
                          {example.translation}
                        </p>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            </div>
          </div>

          {/* Bottom Row - Wordbook (Full Width) */}
          <div className="group/card">
            <div className="relative bg-gradient-to-br from-black via-slate-900 to-black border-2 border-green-500/30 hover:border-green-400/60 rounded-xl p-8 transition-all duration-300 hover:shadow-2xl hover:shadow-green-500/20 overflow-hidden">
              <div className="absolute inset-0 opacity-0 group-hover/card:opacity-100 transition-opacity duration-300">
                <div className="absolute inset-0 bg-gradient-to-br from-green-500/5 to-cyan-500/5 rounded-xl"></div>
              </div>

              <div className="relative z-10">
                <h2 className="text-xs font-black text-green-400 uppercase tracking-widest mb-6">
                  My_Wordbook
                </h2>

                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  {[
                    { finnish: 'hallo', english: 'hello', status: 'recent', color: 'cyan' },
                    { finnish: 'kiitos', english: 'thank you', status: 'learning', color: 'yellow' },
                    { finnish: 'terve', english: 'hi', status: 'mastered', color: 'green' },
                  ].map((word, idx) => (
                    <div
                      key={idx}
                      onMouseEnter={() => setHoveredCard(idx)}
                      onMouseLeave={() => setHoveredCard(null)}
                      className={`p-6 bg-black/50 rounded-lg transition-all duration-300 transform cursor-pointer border-2 ${
                        hoveredCard === idx
                          ? 'border-green-400/60 bg-green-500/10 shadow-lg shadow-green-500/30 scale-105'
                          : 'border-green-500/20'
                      }`}
                    >
                      <p className="text-2xl font-black bg-gradient-to-r from-green-400 to-cyan-400 bg-clip-text text-transparent mb-2 font-mono">
                        {word.finnish.toUpperCase()}
                      </p>
                      <p className="text-xs text-green-300/70 font-bold uppercase tracking-wider mb-3">
                        {word.english}
                      </p>
                      <span className={`text-xs font-black px-3 py-1 rounded-full border-2 inline-block uppercase tracking-widest ${
                        word.status === 'mastered' ? 'bg-green-500/20 text-green-300 border-green-500/50' :
                        word.status === 'learning' ? 'bg-yellow-500/20 text-yellow-300 border-yellow-500/50' :
                        'bg-cyan-500/20 text-cyan-300 border-cyan-500/50'
                      }`}>
                        {word.status}
                      </span>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </div>
        </main>
      </div>
    </div>
  )
}
