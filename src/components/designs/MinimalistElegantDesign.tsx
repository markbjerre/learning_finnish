import { Link } from 'react-router-dom'
import { useState } from 'react'

export default function MinimalistElegantDesign() {
  const [searchText, setSearchText] = useState('hallo')
  const [selectedLanguage, setSelectedLanguage] = useState('finnish')

  return (
    <div className="min-h-screen bg-gradient-to-b from-amber-50 via-white to-amber-50 flex flex-col items-center py-20 px-4">
      {/* Navigation */}
      <header className="w-full text-center mb-20">
        <Link
          to="/"
          className="text-sm text-amber-700 hover:text-amber-900 font-semibold tracking-widest uppercase mb-8 inline-block transition-colors"
        >
          ← Back to Home
        </Link>
        <h1 className="text-5xl font-light text-amber-900 mb-4 serif">
          Learning Finnish
        </h1>
        <p className="text-sm text-amber-600 tracking-widest uppercase">
          Explore language with elegance
        </p>
      </header>

      {/* Main Content - Centered Narrow Column */}
      <main className="w-full max-w-2xl">
        {/* Search Section */}
        <section className="mb-24">
          <div className="flex flex-col gap-4 mb-8">
            <select
              value={selectedLanguage}
              onChange={(e) => setSelectedLanguage(e.target.value)}
              className="px-6 py-3 rounded-none border-b-2 border-amber-600 bg-transparent text-amber-900 font-light focus:outline-none focus:border-amber-800 transition-colors text-lg"
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
              className="px-6 py-3 rounded-none border-b-2 border-amber-600 bg-transparent text-amber-900 font-light placeholder-amber-400 focus:outline-none focus:border-amber-800 transition-colors text-lg"
            />
          </div>
        </section>

        {/* Word Display */}
        <section className="mb-20 pb-20 border-b border-amber-200">
          <h2 className="text-xs text-amber-600 tracking-widest uppercase font-semibold mb-12">
            Translation
          </h2>

          <div className="text-center mb-16">
            <h3 className="text-7xl font-light text-amber-900 mb-6 serif">
              {searchText}
            </h3>
            <p className="text-2xl text-amber-700 font-light">
              hello
            </p>
          </div>

          <div className="mb-16">
            <p className="text-xs text-amber-600 tracking-widest uppercase font-semibold mb-8">
              Part of Speech
            </p>
            <p className="text-lg text-amber-800 font-light">
              noun
            </p>
          </div>
        </section>

        {/* Grammatical Forms */}
        <section className="mb-20 pb-20 border-b border-amber-200">
          <h2 className="text-xs text-amber-600 tracking-widest uppercase font-semibold mb-12">
            Grammatical Forms
          </h2>

          <div className="space-y-10">
            {[
              { case: 'Nominative', form: 'hallo' },
              { case: 'Genitive', form: 'hallon' },
              { case: 'Partitive', form: 'halloa' },
              { case: 'Inessive', form: 'hallossa' },
            ].map((item, idx) => (
              <div key={idx} className="flex items-baseline justify-between pb-4 border-b border-amber-100 hover:border-amber-300 transition-colors group">
                <p className="text-xs text-amber-600 tracking-widest uppercase font-semibold group-hover:text-amber-800 transition-colors">
                  {item.case}
                </p>
                <p className="text-2xl text-amber-900 font-light group-hover:text-amber-700 transition-colors">
                  {item.form}
                </p>
              </div>
            ))}
          </div>
        </section>

        {/* Examples */}
        <section className="mb-20 pb-20 border-b border-amber-200">
          <h2 className="text-xs text-amber-600 tracking-widest uppercase font-semibold mb-12">
            Example Sentences
          </h2>

          <div className="space-y-12">
            <div>
              <p className="text-lg text-amber-900 font-light mb-4 italic">
                "Hallo, kuinka voitte?"
              </p>
              <p className="text-sm text-amber-600 font-light">
                How are you? (English)
              </p>
            </div>

            <div>
              <p className="text-lg text-amber-900 font-light mb-4 italic">
                "Hallo maailma"
              </p>
              <p className="text-sm text-amber-600 font-light">
                Hello world (English)
              </p>
            </div>
          </div>
        </section>

        {/* Wordbook */}
        <section>
          <div className="flex items-center justify-between mb-12">
            <h2 className="text-xs text-amber-600 tracking-widest uppercase font-semibold">
              My Wordbook
            </h2>
            <button className="text-xs text-amber-700 hover:text-amber-900 uppercase tracking-widest font-semibold transition-colors underline">
              View All
            </button>
          </div>

          <div className="space-y-12">
            {[
              { finnish: 'hallo', english: 'hello', status: 'recent' },
              { finnish: 'kiitos', english: 'thank you', status: 'learning' },
              { finnish: 'terve', english: 'hi', status: 'mastered' },
            ].map((word, idx) => (
              <div
                key={idx}
                className="flex items-baseline justify-between pb-8 border-b border-amber-100 hover:border-amber-300 transition-colors group last:border-0"
              >
                <div>
                  <p className="text-2xl text-amber-900 font-light group-hover:text-amber-700 transition-colors mb-2">
                    {word.finnish}
                  </p>
                  <p className="text-sm text-amber-600 font-light">
                    {word.english}
                  </p>
                </div>
                <div className="flex items-center gap-4">
                  <span className="text-xs text-amber-600 uppercase tracking-widest font-semibold">
                    {word.status === 'mastered' ? '✓ Mastered' : word.status === 'learning' ? '• Learning' : '○ Recent'}
                  </span>
                </div>
              </div>
            ))}
          </div>
        </section>
      </main>

      {/* Footer spacer */}
      <div className="mt-20"></div>
    </div>
  )
}
