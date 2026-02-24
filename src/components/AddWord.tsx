import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { wordAPI } from '../lib/api'

export default function AddWord() {
  const [finnish, setFinnish] = useState('')
  const [danish, setDanish] = useState('')
  const [english, setEnglish] = useState('')
  const [wordType, setWordType] = useState('noun')
  const [result, setResult] = useState<{ status: string; word_id?: string; finnish?: string; inflections_generated?: { inflections: number; verb_forms: number } } | null>(null)
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const wordId = result?.word_id
  const { data: inflections, isLoading: inflectionsLoading } = useQuery({
    queryKey: ['inflections', wordId],
    queryFn: () => wordAPI.getInflections(wordId!),
    enabled: !!wordId && result?.status === 'created',
  })

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!finnish.trim()) return

    setIsSubmitting(true)
    setError(null)
    setResult(null)

    try {
      const res = await wordAPI.addWord({
        finnish: finnish.trim(),
        danish: danish.trim() || undefined,
        english: english.trim() || undefined,
        word_type: wordType,
      })
      setResult(res)
      if (res.status === 'created') {
        setFinnish('')
        setDanish('')
        setEnglish('')
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to add word')
    } finally {
      setIsSubmitting(false)
    }
  }

  const inputClass = 'w-full px-4 py-2 bg-slate-800/50 border border-slate-600 rounded-lg text-white placeholder-slate-500 focus:ring-2 focus:ring-sky-500 focus:border-sky-500'
  const labelClass = 'block text-sm font-medium text-slate-300 mb-1'

  return (
    <div
      className="rounded-2xl p-8"
      style={{
        background: 'rgba(255, 255, 255, 0.03)',
        backdropFilter: 'blur(20px)',
        border: '1px solid rgba(255, 255, 255, 0.1)',
      }}
    >
      <h2 className="text-2xl font-bold text-white mb-6">Add Word (Spaced Repetition)</h2>
      <p className="text-slate-400 mb-6">
        Add a word directly to the vocabulary. Inflections are generated automatically when OpenAI is configured.
      </p>

      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <label className={labelClass}>Finnish *</label>
          <input
            type="text"
            value={finnish}
            onChange={(e) => setFinnish(e.target.value)}
            placeholder="talo"
            className={inputClass}
            required
          />
        </div>
        <div>
          <label className={labelClass}>Danish</label>
          <input
            type="text"
            value={danish}
            onChange={(e) => setDanish(e.target.value)}
            placeholder="hus"
            className={inputClass}
          />
        </div>
        <div>
          <label className={labelClass}>English</label>
          <input
            type="text"
            value={english}
            onChange={(e) => setEnglish(e.target.value)}
            placeholder="house"
            className={inputClass}
          />
        </div>
        <div>
          <label className={labelClass}>Type</label>
          <select
            value={wordType}
            onChange={(e) => setWordType(e.target.value)}
            className={inputClass}
          >
            <option value="noun">Noun</option>
            <option value="verb">Verb</option>
            <option value="adjective">Adjective</option>
            <option value="adverb">Adverb</option>
            <option value="phrase">Phrase</option>
            <option value="other">Other</option>
          </select>
        </div>
        <button
          type="submit"
          disabled={isSubmitting}
          className="px-6 py-3 bg-sky-600 text-white rounded-lg hover:bg-sky-500 disabled:opacity-50 transition-colors"
        >
          {isSubmitting ? 'Adding...' : 'Add Word'}
        </button>
      </form>

      {error && (
        <div className="mt-4 p-4 bg-red-900/30 border border-red-500/50 rounded-lg text-red-300">{error}</div>
      )}

      {result && (
        <div className="mt-6 p-4 bg-emerald-900/30 border border-emerald-500/50 rounded-lg text-emerald-300">
          {result.status === 'created' && (
            <p className="font-medium">Added &quot;{result.finnish}&quot;</p>
          )}
          {result.status === 'exists' && (
            <p className="text-amber-300">Word &quot;{result.finnish}&quot; already exists.</p>
          )}
          {result.inflections_generated && (
            <p className="text-sm mt-1 opacity-90">
              Generated {result.inflections_generated.inflections} inflections, {result.inflections_generated.verb_forms} verb forms
            </p>
          )}
        </div>
      )}

      {wordId && result?.status === 'created' && (
        <div className="mt-6">
          <h3 className="font-semibold text-white mb-3">Inflections</h3>
          {inflectionsLoading ? (
            <p className="text-slate-500">Loading inflections...</p>
          ) : inflections ? (
            <div className="space-y-4">
              {inflections.inflections?.length > 0 && (
                <div>
                  <h4 className="text-sm font-medium text-slate-400 mb-2">Cases</h4>
                  <div className="overflow-x-auto">
                    <table className="min-w-full text-sm">
                      <thead>
                        <tr className="border-b border-slate-600">
                          <th className="text-left py-2 text-slate-400">Case</th>
                          <th className="text-left py-2 text-slate-400">Singular</th>
                          <th className="text-left py-2 text-slate-400">Plural</th>
                        </tr>
                      </thead>
                      <tbody>
                        {inflections.inflections.map((i: { case_name: string; singular: string; plural: string }, idx: number) => (
                          <tr key={idx} className="border-b border-slate-700/50">
                            <td className="py-2 text-slate-300">{i.case_name}</td>
                            <td className="py-2 text-slate-300">{i.singular || '—'}</td>
                            <td className="py-2 text-slate-300">{i.plural || '—'}</td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                </div>
              )}
              {inflections.verb_forms?.length > 0 && (
                <div>
                  <h4 className="text-sm font-medium text-slate-400 mb-2">Verb Forms</h4>
                  <div className="overflow-x-auto">
                    <table className="min-w-full text-sm">
                      <thead>
                        <tr className="border-b border-slate-600">
                          <th className="text-left py-2 text-slate-400">Form</th>
                          <th className="text-left py-2 text-slate-400">Value</th>
                          <th className="text-left py-2 text-slate-400">Tense</th>
                        </tr>
                      </thead>
                      <tbody>
                        {inflections.verb_forms.map((v: { form_name: string; form_value: string; tense: string }, idx: number) => (
                          <tr key={idx} className="border-b border-slate-700/50">
                            <td className="py-2 text-slate-300">{v.form_name}</td>
                            <td className="py-2 text-slate-300">{v.form_value}</td>
                            <td className="py-2 text-slate-300">{v.tense || '—'}</td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                </div>
              )}
              {(!inflections.inflections?.length && !inflections.verb_forms?.length) && (
                <p className="text-slate-500">No inflections yet. Enable OpenAI for auto-generation.</p>
              )}
            </div>
          ) : null}
        </div>
      )}
    </div>
  )
}
