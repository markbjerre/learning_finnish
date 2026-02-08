import { Link } from 'react-router-dom'
import { useState } from 'react'

export default function DarkDesign() {
  const [searchText, setSearchText] = useState('hallo')
  const [selectedLanguage, setSelectedLanguage] = useState('finnish')

  return (
    <div className="min-h-screen bg-amber-50">
      {/* Header */}
      <header className="bg-amber-100 border-b border-amber-200 px-6 py-4">
        <div className="flex items-center justify-between">
          <Link to="/" className="text-2xl font-semibold text-amber-900 hover:text-amber-700 transition-colors">
            Learning Finnish
          </Link>
          <Link to="/" className="px-4 py-2 text-sm text-amber-900 border border-amber-900 rounded hover:bg-amber-200 transition-colors">
            ← Back
          </Link>
        </div>
      </header>

      <main className="max-w-7xl mx-auto p-6">
        <div className="grid grid-cols-12 gap-6">
          {/* Search Card - 8 columns */}
          <div className="col-span-12 lg:col-span-8 bg-white border border-amber-200 rounded-lg p-6 shadow-sm hover:shadow-md transition-shadow">
            <h2 className="text-sm font-semibold text-amber-900 mb-4 uppercase tracking-widest">Search Word</h2>
            <div className="flex gap-3">
              <select
                value={selectedLanguage}
                onChange={(e) => setSelectedLanguage(e.target.value)}
                className="px-4 py-3 border border-amber-200 rounded bg-white text-amber-900 focus:outline-none focus:ring-2 focus:ring-amber-700 transition-all"
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
                className="flex-1 px-4 py-3 border border-amber-200 rounded bg-white text-amber-900 placeholder-amber-400 focus:outline-none focus:ring-2 focus:ring-amber-700 transition-all"
              />
              <button className="px-6 py-3 bg-amber-700 hover:bg-amber-800 text-white font-semibold rounded transition-colors">
                Search
              </button>
            </div>
          </div>

          {/* Progress Card - 4 columns */}
          <div className="col-span-12 lg:col-span-4 bg-white border border-green-200 rounded-lg p-6 shadow-sm hover:shadow-md transition-shadow">
            <h2 className="text-sm font-semibold text-green-900 mb-4 uppercase tracking-widest">Progress</h2>
            <div className="space-y-3">
              <div>
                <p className="text-3xl font-bold text-green-700">3</p>
                <p className="text-sm text-green-600">Words Saved</p>
              </div>
              <div className="pt-3 border-t border-green-200">
                <p className="text-3xl font-bold text-green-700">72%</p>
                <p className="text-sm text-green-600">Learning Progress</p>
              </div>
            </div>
          </div>

          {/* Main Word - 6 columns */}
          <div className="col-span-12 lg:col-span-6 bg-white border border-amber-300 rounded-lg p-8 shadow-sm hover:shadow-md transition-shadow">
            <h2 className="text-sm font-semibold text-amber-900 mb-6 uppercase tracking-widest">Translation</h2>
            <div className="text-center">
              <h1 className="text-6xl font-bold text-amber-900 mb-3">{searchText}</h1>
              <span className="inline-block px-3 py-1 bg-amber-100 text-amber-800 text-sm font-semibold rounded mb-4">
                noun
              </span>
              <p className="text-xl text-amber-700">hello</p>
            </div>
          </div>

          {/* Grammatical Forms - 6 columns */}
          <div className="col-span-12 lg:col-span-6 bg-white border border-amber-200 rounded-lg p-6 shadow-sm hover:shadow-md transition-shadow">
            <h2 className="text-sm font-semibold text-amber-900 mb-4 uppercase tracking-widest">Grammatical Forms</h2>
            <div className="grid grid-cols-2 gap-3">
              {[
                { case: 'Nominative', form: 'hallo' },
                { case: 'Genitive', form: 'hallon' },
                { case: 'Partitive', form: 'halloa' },
                { case: 'Inessive', form: 'hallossa' },
              ].map((item, idx) => (
                <div
                  key={idx}
                  className="p-3 border border-amber-200 rounded bg-amber-50 hover:bg-amber-100 transition-colors"
                >
                  <p className="text-xs text-amber-600 uppercase tracking-wide mb-1 font-semibold">
                    {item.case}
                  </p>
                  <p className="text-lg text-amber-900 font-bold">{item.form}</p>
                </div>
              ))}
            </div>
          </div>

          {/* Examples - 12 columns */}
          <div className="col-span-12 bg-white border border-amber-200 rounded-lg p-6 shadow-sm hover:shadow-md transition-shadow">
            <h2 className="text-sm font-semibold text-amber-900 mb-4 uppercase tracking-widest">Example Sentences</h2>
            <div className="grid grid-cols-2 gap-4">
              {[
                { fi: '"Hallo, kuinka voitte?"', da: '"Hallo, hvordan går det?" (Danish)' },
                { fi: '"Hallo maailma"', da: '"Hallo verden" (Danish)' },
              ].map((ex, idx) => (
                <div key={idx} className="p-4 border border-amber-200 rounded bg-amber-50 hover:bg-amber-100 transition-colors">
                  <p className="text-amber-900 font-semibold mb-2">{ex.fi}</p>
                  <p className="text-sm text-amber-700">{ex.da}</p>
                </div>
              ))}
            </div>
          </div>

          {/* Wordbook - 12 columns */}
          <div className="col-span-12 bg-white border border-amber-200 rounded-lg p-6 shadow-sm hover:shadow-md transition-shadow">
            <h2 className="text-sm font-semibold text-amber-900 mb-4 uppercase tracking-widest">My Wordbook</h2>
            <div className="grid grid-cols-3 gap-4">
              {[
                { finnish: 'hallo', english: 'hello', status: 'recent' },
                { finnish: 'kiitos', english: 'thank you', status: 'learning' },
                { finnish: 'terve', english: 'hi', status: 'mastered' },
              ].map((word, idx) => (
                <div
                  key={idx}
                  className="p-4 border border-amber-200 rounded bg-amber-50 hover:bg-amber-100 hover:border-amber-300 transition-all"
                >
                  <p className="text-lg font-bold text-amber-900 mb-2">{word.finnish}</p>
                  <p className="text-sm text-amber-700 mb-3">{word.english}</p>
                  <span className={`inline-block px-3 py-1 text-xs font-semibold rounded ${
                    word.status === 'mastered' ? 'bg-green-100 text-green-700' :
                    word.status === 'learning' ? 'bg-yellow-100 text-yellow-700' :
                    'bg-amber-100 text-amber-700'
                  }`}>
                    {word.status.charAt(0).toUpperCase() + word.status.slice(1)}
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
