import { Link } from 'react-router-dom'
import { useState } from 'react'

export default function ModernSaaSDesign() {
  const [searchText, setSearchText] = useState('hallo')
  const [selectedLanguage, setSelectedLanguage] = useState('finnish')

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-slate-50">
      {/* Hero Section */}
      <div className="relative pt-12 pb-24 overflow-hidden">
        <div className="absolute inset-0 bg-gradient-to-b from-blue-600 to-blue-700 opacity-90"></div>

        {/* Decorative elements */}
        <div className="absolute top-0 right-0 w-96 h-96 bg-blue-400/20 rounded-full blur-3xl -mr-48 -mt-48"></div>
        <div className="absolute bottom-0 left-0 w-80 h-80 bg-indigo-400/20 rounded-full blur-3xl -ml-40 -mb-40"></div>

        <div className="relative z-10 max-w-5xl mx-auto px-6">
          {/* Header */}
          <header className="flex items-center justify-between mb-12">
            <Link to="/" className="text-3xl font-bold text-white hover:text-blue-100 transition-colors">
              Learning Finnish
            </Link>
            <Link to="/" className="px-6 py-2 text-sm text-blue-100 border border-blue-200 rounded-lg hover:bg-white/10 transition-all">
              ← Back
            </Link>
          </header>

          {/* Hero Content */}
          <div className="text-center mb-12">
            <h1 className="text-5xl md:text-6xl font-bold text-white mb-6">
              {searchText}
            </h1>
            <p className="text-xl text-blue-100 mb-8">Discover the power of language learning</p>

            {/* Search Bar */}
            <div className="flex gap-3 max-w-xl mx-auto">
              <select
                value={selectedLanguage}
                onChange={(e) => setSelectedLanguage(e.target.value)}
                className="px-4 py-3 rounded-lg bg-white/20 border border-white/30 text-white font-semibold focus:outline-none focus:ring-2 focus:ring-white backdrop-blur"
              >
                <option value="finnish" className="text-slate-900">Finnish</option>
                <option value="english" className="text-slate-900">English</option>
                <option value="danish" className="text-slate-900">Danish</option>
              </select>
              <input
                type="text"
                value={searchText}
                onChange={(e) => setSearchText(e.target.value)}
                placeholder="Enter a word..."
                className="flex-1 px-4 py-3 rounded-lg bg-white/20 border border-white/30 text-white placeholder-white/60 font-semibold focus:outline-none focus:ring-2 focus:ring-white backdrop-blur"
              />
              <button className="px-8 py-3 bg-white text-blue-600 font-bold rounded-lg hover:bg-blue-50 transition-all shadow-lg">
                Search
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* Content Panels */}
      <div className="max-w-5xl mx-auto px-6 py-12">
        <div className="grid grid-cols-2 gap-8 mb-8">
          {/* Left Panel - Translation Details */}
          <div className="bg-white rounded-2xl p-8 shadow-lg border border-slate-200 hover:shadow-xl transition-shadow">
            <h2 className="text-sm font-bold text-blue-600 uppercase tracking-widest mb-6">
              Translation Details
            </h2>

            <div className="mb-8 pb-8 border-b border-slate-200">
              <span className="inline-block px-4 py-2 bg-blue-100 text-blue-700 text-sm font-semibold rounded-lg mb-4">
                noun
              </span>
              <p className="text-2xl text-slate-900 font-light">hello</p>
            </div>

            <h3 className="text-sm font-bold text-slate-700 uppercase tracking-widest mb-4">
              Grammatical Forms
            </h3>
            <div className="space-y-3">
              {[
                { case: 'Nominative', form: 'hallo' },
                { case: 'Genitive', form: 'hallon' },
                { case: 'Partitive', form: 'halloa' },
                { case: 'Inessive', form: 'hallossa' },
              ].map((item, idx) => (
                <div key={idx} className="flex items-center justify-between p-3 bg-slate-50 border border-slate-200 rounded-lg hover:bg-blue-50 transition-colors">
                  <p className="text-xs text-slate-600 font-semibold uppercase">{item.case}</p>
                  <p className="text-lg text-slate-900 font-semibold">{item.form}</p>
                </div>
              ))}
            </div>
          </div>

          {/* Right Panel - Examples & Wordbook */}
          <div className="space-y-6">
            {/* Examples */}
            <div className="bg-white rounded-2xl p-8 shadow-lg border border-slate-200 hover:shadow-xl transition-shadow">
              <h2 className="text-sm font-bold text-blue-600 uppercase tracking-widest mb-6">
                Example Sentences
              </h2>
              <div className="space-y-4">
                <div className="p-4 bg-slate-50 border border-slate-200 rounded-lg hover:border-blue-300 transition-colors">
                  <p className="text-slate-900 font-medium mb-1">"Hallo, kuinka voitte?"</p>
                  <p className="text-sm text-slate-600">How are you?</p>
                </div>
                <div className="p-4 bg-slate-50 border border-slate-200 rounded-lg hover:border-blue-300 transition-colors">
                  <p className="text-slate-900 font-medium mb-1">"Hallo maailma"</p>
                  <p className="text-sm text-slate-600">Hello world</p>
                </div>
              </div>
            </div>

            {/* Quick Stats */}
            <div className="bg-gradient-to-br from-blue-600 to-blue-700 text-white rounded-2xl p-8 shadow-lg">
              <h2 className="text-sm font-bold uppercase tracking-widest mb-4">Learning Progress</h2>
              <div className="flex gap-4">
                <div>
                  <p className="text-3xl font-bold">3</p>
                  <p className="text-sm text-blue-100">Saved Words</p>
                </div>
                <div className="pl-4 border-l border-blue-400">
                  <p className="text-3xl font-bold">72%</p>
                  <p className="text-sm text-blue-100">Progress</p>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Wordbook */}
        <div className="bg-white rounded-2xl p-8 shadow-lg border border-slate-200">
          <div className="flex items-center justify-between mb-6">
            <h2 className="text-sm font-bold text-blue-600 uppercase tracking-widest">
              My Wordbook
            </h2>
            <button className="text-sm text-blue-600 hover:text-blue-700 font-bold transition-colors">
              View All →
            </button>
          </div>

          <div className="grid grid-cols-3 gap-6">
            {[
              { finnish: 'hallo', english: 'hello', status: 'recent' },
              { finnish: 'kiitos', english: 'thank you', status: 'learning' },
              { finnish: 'terve', english: 'hi', status: 'mastered' },
            ].map((word, idx) => (
              <div key={idx} className="p-6 bg-slate-50 border border-slate-200 rounded-xl hover:border-blue-300 hover:shadow-md transition-all">
                <p className="text-xl font-bold text-slate-900 mb-1">{word.finnish}</p>
                <p className="text-sm text-slate-600 mb-4">{word.english}</p>
                <span className={`inline-block px-3 py-1 text-xs font-semibold rounded-lg ${
                  word.status === 'mastered' ? 'bg-green-100 text-green-700' :
                  word.status === 'learning' ? 'bg-yellow-100 text-yellow-700' :
                  'bg-blue-100 text-blue-700'
                }`}>
                  {word.status.charAt(0).toUpperCase() + word.status.slice(1)}
                </span>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  )
}
