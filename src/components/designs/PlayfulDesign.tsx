import { Link } from 'react-router-dom'
import { useState } from 'react'

export default function PlayfulDesign() {
  const [searchText, setSearchText] = useState('hallo')
  const [selectedLanguage, setSelectedLanguage] = useState('finnish')

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900 p-4">
      {/* Header */}
      <header className="mb-8">
        <div className="flex items-center justify-between mb-6">
          <Link to="/" className="text-3xl font-bold text-white hover:scale-105 transition-transform">
            Learning Finnish
          </Link>
          <Link to="/" className="px-4 py-2 text-sm text-white bg-purple-600/50 hover:bg-purple-600 border border-purple-400 rounded-lg transition-all">
            ← Back
          </Link>
        </div>
      </header>

      <main className="grid grid-cols-12 gap-4 max-w-7xl mx-auto">
        {/* LEFT SIDEBAR - Controls */}
        <div className="col-span-12 md:col-span-3 space-y-4">
          {/* Search Input Card */}
          <div className="bg-gradient-to-br from-pink-500/20 to-cyan-500/20 backdrop-blur-md border border-pink-400/30 rounded-2xl p-6">
            <h3 className="text-sm font-bold text-pink-300 mb-4 uppercase tracking-wide">Search</h3>
            <input
              type="text"
              value={searchText}
              onChange={(e) => setSearchText(e.target.value)}
              placeholder="Type a word..."
              className="w-full px-4 py-2 rounded-lg bg-white/10 text-white placeholder-white/50 border border-pink-400/30 focus:outline-none focus:ring-2 focus:ring-pink-400 mb-3 font-semibold"
            />
            <select
              value={selectedLanguage}
              onChange={(e) => setSelectedLanguage(e.target.value)}
              className="w-full px-4 py-2 rounded-lg bg-white/10 text-white border border-pink-400/30 focus:outline-none focus:ring-2 focus:ring-pink-400 font-semibold"
            >
              <option value="finnish">Finnish</option>
              <option value="english">English</option>
              <option value="danish">Danish</option>
            </select>
          </div>

          {/* Stats Card */}
          <div className="bg-gradient-to-br from-lime-500/20 to-cyan-500/20 backdrop-blur-md border border-lime-400/30 rounded-2xl p-6">
            <h3 className="text-sm font-bold text-lime-300 mb-4 uppercase tracking-wide">Progress</h3>
            <div className="space-y-3">
              <div>
                <p className="text-white font-bold text-2xl">3</p>
                <p className="text-lime-200 text-xs uppercase tracking-wide">Words Saved</p>
              </div>
              <div className="pt-3 border-t border-lime-400/30">
                <p className="text-white font-bold text-2xl">72%</p>
                <p className="text-lime-200 text-xs uppercase tracking-wide">Learning Progress</p>
              </div>
            </div>
          </div>
        </div>

        {/* CENTER CONTENT - Main Translation */}
        <div className="col-span-12 md:col-span-6">
          {/* Main Word Card */}
          <div className="bg-gradient-to-br from-purple-600/40 to-pink-600/40 backdrop-blur-md border border-purple-400/50 rounded-2xl p-8 mb-4 text-center">
            <h2 className="text-sm font-bold text-purple-200 mb-6 uppercase tracking-widest">Translation</h2>
            <h1 className="text-7xl font-black bg-gradient-to-r from-pink-400 to-cyan-400 bg-clip-text text-transparent mb-4">
              {searchText}
            </h1>
            <div className="flex justify-center gap-2 mb-4">
              <span className="px-4 py-1 bg-pink-500/50 text-pink-200 text-sm font-bold rounded-full border border-pink-400/50">
                noun
              </span>
            </div>
            <p className="text-2xl text-white/80 font-light">hello</p>
          </div>

          {/* Grammatical Forms */}
          <div>
            <h3 className="text-sm font-bold text-white mb-3 uppercase tracking-widest">Forms</h3>
            <div className="grid grid-cols-2 gap-3">
              {[
                { case: 'Nominative', form: 'hallo' },
                { case: 'Genitive', form: 'hallon' },
                { case: 'Partitive', form: 'halloa' },
                { case: 'Inessive', form: 'hallossa' },
              ].map((item, idx) => (
                <div
                  key={idx}
                  className="bg-gradient-to-br from-cyan-500/30 to-blue-500/30 backdrop-blur-md border border-cyan-400/40 rounded-xl p-4 text-center hover:scale-105 transition-transform"
                >
                  <p className="text-xs text-cyan-200 uppercase tracking-wide mb-2 font-bold">
                    {item.case}
                  </p>
                  <p className="text-lg text-white font-black">{item.form}</p>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* RIGHT SIDEBAR - Examples */}
        <div className="col-span-12 md:col-span-3">
          {/* Examples Card */}
          <div className="bg-gradient-to-br from-amber-500/20 to-orange-500/20 backdrop-blur-md border border-amber-400/30 rounded-2xl p-6 mb-4">
            <h3 className="text-sm font-bold text-amber-300 mb-4 uppercase tracking-wide">Examples</h3>
            <div className="space-y-3">
              <div className="bg-white/5 backdrop-blur p-3 rounded-lg border border-amber-400/20">
                <p className="text-white font-semibold text-sm mb-1">"Hallo, kuinka voitte?"</p>
                <p className="text-amber-200 text-xs">How are you?</p>
              </div>
              <div className="bg-white/5 backdrop-blur p-3 rounded-lg border border-amber-400/20">
                <p className="text-white font-semibold text-sm mb-1">"Hallo maailma"</p>
                <p className="text-amber-200 text-xs">Hello world</p>
              </div>
            </div>
          </div>

          {/* Wordbook Preview */}
          <div className="bg-gradient-to-br from-purple-500/20 to-pink-500/20 backdrop-blur-md border border-purple-400/30 rounded-2xl p-6">
            <h3 className="text-sm font-bold text-purple-300 mb-4 uppercase tracking-wide">Wordbook</h3>
            <div className="space-y-3">
              {[
                { finnish: 'hallo', english: 'hello', status: 'recent' },
                { finnish: 'kiitos', english: 'thank you', status: 'learning' },
                { finnish: 'terve', english: 'hi', status: 'mastered' },
              ].map((word, idx) => (
                <div key={idx} className="bg-white/5 backdrop-blur p-3 rounded-lg border border-purple-400/20 hover:border-purple-400/50 transition-all">
                  <p className="text-white font-bold text-sm">{word.finnish}</p>
                  <p className="text-purple-200 text-xs mb-2">{word.english}</p>
                  <span className={`text-xs font-bold px-2 py-1 rounded-full inline-block ${
                    word.status === 'mastered' ? 'bg-green-500/50 text-green-200' :
                    word.status === 'learning' ? 'bg-yellow-500/50 text-yellow-200' :
                    'bg-pink-500/50 text-pink-200'
                  }`}>
                    {word.status}
                  </span>
                </div>
              ))}
            </div>
          </div>
        </div>
      </main>
    </div>
  )
}
