import { Link } from 'react-router-dom'
import { useState } from 'react'

export default function MinimalistDesign() {
  const [searchText, setSearchText] = useState('hallo')
  const [selectedLanguage, setSelectedLanguage] = useState('finnish')

  return (
    <div className="min-h-screen bg-gradient-to-b from-sky-50 via-white to-sky-50 flex flex-col items-center py-16 px-4">
      {/* Header */}
      <header className="w-full mb-12">
        <div className="flex items-center justify-center mb-8">
          <Link to="/" className="text-4xl font-light text-slate-700 hover:text-slate-900 transition-colors">
            Learning Finnish
          </Link>
        </div>
        <div className="flex justify-center">
          <Link to="/" className="px-4 py-2 text-sm text-sky-600 hover:text-sky-700 transition-colors border border-sky-300 rounded-full">
            ← Back to Home
          </Link>
        </div>
      </header>

      <main className="w-full max-w-xl">
        {/* Search Card */}
        <div className="bg-white rounded-2xl p-8 shadow-sm border border-sky-100 mb-8 hover:shadow-md transition-shadow">
          <h2 className="text-lg font-medium text-slate-900 mb-6 text-center">
            Search Translation
          </h2>

          <div className="space-y-4">
            <select
              value={selectedLanguage}
              onChange={(e) => setSelectedLanguage(e.target.value)}
              className="w-full px-4 py-3 border border-sky-200 rounded-lg bg-white text-slate-900 font-medium focus:outline-none focus:ring-2 focus:ring-sky-400 focus:ring-offset-2 transition-all"
            >
              <option value="finnish">Finnish</option>
              <option value="english">English</option>
              <option value="danish">Danish</option>
            </select>

            <input
              type="text"
              value={searchText}
              onChange={(e) => setSearchText(e.target.value)}
              placeholder="Enter a word..."
              className="w-full px-4 py-3 border border-sky-200 rounded-lg bg-white text-slate-900 placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-sky-400 focus:ring-offset-2 transition-all"
            />

            <button className="w-full py-3 bg-gradient-to-r from-sky-400 to-sky-500 text-white font-semibold rounded-lg hover:from-sky-500 hover:to-sky-600 transition-all shadow-sm hover:shadow-md">
              Search
            </button>
          </div>
        </div>

        {/* Translation Card */}
        <div className="bg-white rounded-2xl p-8 shadow-sm border border-sky-100 mb-8 hover:shadow-md transition-shadow">
          <h2 className="text-center text-sm font-medium text-slate-600 uppercase tracking-widest mb-8">
            Translation Result
          </h2>

          {/* Word Display */}
          <div className="text-center mb-8 pb-8 border-b border-sky-100">
            <h3 className="text-6xl font-light text-slate-900 mb-3">{searchText}</h3>
            <div className="flex justify-center gap-2 mb-4">
              <span className="px-4 py-1 bg-sky-100 text-sky-700 text-sm font-medium rounded-full">
                noun
              </span>
            </div>
            <p className="text-xl text-slate-600 font-light">hello</p>
          </div>

          {/* Grammatical Forms - Stacked */}
          <div className="mb-8">
            <h4 className="text-sm font-semibold text-slate-700 mb-6 text-center uppercase tracking-wide">
              Grammatical Forms
            </h4>
            <div className="space-y-3">
              {[
                { case: 'Nominative', form: 'hallo' },
                { case: 'Genitive', form: 'hallon' },
                { case: 'Partitive', form: 'halloa' },
                { case: 'Inessive', form: 'hallossa' },
              ].map((item, idx) => (
                <div key={idx} className="p-4 bg-sky-50 border border-sky-100 rounded-lg hover:bg-sky-100 transition-colors text-center">
                  <p className="text-xs text-slate-600 uppercase tracking-wide mb-2 font-medium">
                    {item.case}
                  </p>
                  <p className="text-lg text-slate-900 font-semibold">{item.form}</p>
                </div>
              ))}
            </div>
          </div>

          {/* Examples - Stacked */}
          <div>
            <h4 className="text-sm font-semibold text-slate-700 mb-6 text-center uppercase tracking-wide">
              Example Sentences
            </h4>
            <div className="space-y-4">
              <div className="p-4 bg-sky-50 border border-sky-100 rounded-lg hover:bg-sky-100 transition-colors">
                <p className="text-slate-900 mb-2 font-light text-center">
                  "Hallo, kuinka voitte?"
                </p>
                <p className="text-sm text-slate-600 font-light text-center">
                  How are you? (English)
                </p>
              </div>
              <div className="p-4 bg-sky-50 border border-sky-100 rounded-lg hover:bg-sky-100 transition-colors">
                <p className="text-slate-900 mb-2 font-light text-center">
                  "Hallo maailma"
                </p>
                <p className="text-sm text-slate-600 font-light text-center">
                  Hello world (English)
                </p>
              </div>
            </div>
          </div>
        </div>

        {/* Wordbook Card */}
        <div className="bg-white rounded-2xl p-8 shadow-sm border border-sky-100 hover:shadow-md transition-shadow">
          <div className="flex items-center justify-between mb-8">
            <h2 className="text-lg font-medium text-slate-900">
              My Wordbook
            </h2>
            <button className="text-sm text-sky-600 hover:text-sky-700 font-medium transition-colors">
              View All →
            </button>
          </div>

          <div className="space-y-4">
            {[
              { finnish: 'hallo', english: 'hello', status: 'recent' },
              { finnish: 'kiitos', english: 'thank you', status: 'learning' },
              { finnish: 'terve', english: 'hi', status: 'mastered' },
            ].map((word, idx) => (
              <div key={idx} className="p-4 bg-sky-50 border border-sky-100 rounded-lg hover:bg-sky-100 transition-colors flex items-center justify-between">
                <div>
                  <p className="text-lg font-semibold text-slate-900">
                    {word.finnish}
                  </p>
                  <p className="text-sm text-slate-600">
                    {word.english}
                  </p>
                </div>
                <span className={`px-3 py-1 text-xs font-medium rounded-full ${
                  word.status === 'mastered' ? 'bg-emerald-100 text-emerald-700' :
                  word.status === 'learning' ? 'bg-amber-100 text-amber-700' :
                  'bg-sky-100 text-sky-700'
                }`}>
                  {word.status.charAt(0).toUpperCase() + word.status.slice(1)}
                </span>
              </div>
            ))}
          </div>
        </div>
      </main>
    </div>
  )
}
