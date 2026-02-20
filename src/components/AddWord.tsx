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

  return (
    <div className="bg-white rounded-lg shadow p-8">
      <h2 className="text-2xl font-bold text-gray-900 mb-6">Add Word (Spaced Repetition)</h2>
      <p className="text-gray-600 mb-6">
        Add a word directly to the vocabulary. Inflections are generated automatically when OpenAI is configured.
      </p>

      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">Finnish *</label>
          <input
            type="text"
            value={finnish}
            onChange={(e) => setFinnish(e.target.value)}
            placeholder="talo"
            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500"
            required
          />
        </div>
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">Danish</label>
          <input
            type="text"
            value={danish}
            onChange={(e) => setDanish(e.target.value)}
            placeholder="hus"
            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500"
          />
        </div>
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">English</label>
          <input
            type="text"
            value={english}
            onChange={(e) => setEnglish(e.target.value)}
            placeholder="house"
            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500"
          />
        </div>
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">Type</label>
          <select
            value={wordType}
            onChange={(e) => setWordType(e.target.value)}
            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500"
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
          className="px-6 py-3 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 disabled:opacity-50"
        >
          {isSubmitting ? 'Adding...' : 'Add Word'}
        </button>
      </form>

      {error && (
        <div className="mt-4 p-4 bg-red-50 border border-red-200 rounded-lg text-red-700">{error}</div>
      )}

      {result && (
        <div className="mt-6 p-4 bg-green-50 border border-green-200 rounded-lg">
          {result.status === 'created' && (
            <p className="text-green-800 font-medium">Added &quot;{result.finnish}&quot;</p>
          )}
          {result.status === 'exists' && (
            <p className="text-amber-800">Word &quot;{result.finnish}&quot; already exists.</p>
          )}
          {result.inflections_generated && (
            <p className="text-sm text-green-700 mt-1">
              Generated {result.inflections_generated.inflections} inflections, {result.inflections_generated.verb_forms} verb forms
            </p>
          )}
        </div>
      )}

      {wordId && result?.status === 'created' && (
        <div className="mt-6">
          <h3 className="font-semibold text-gray-900 mb-3">Inflections</h3>
          {inflectionsLoading ? (
            <p className="text-gray-500">Loading inflections...</p>
          ) : inflections ? (
            <div className="space-y-4">
              {inflections.inflections?.length > 0 && (
                <div>
                  <h4 className="text-sm font-medium text-gray-600 mb-2">Cases</h4>
                  <div className="overflow-x-auto">
                    <table className="min-w-full text-sm">
                      <thead>
                        <tr className="border-b">
                          <th className="text-left py-2">Case</th>
                          <th className="text-left py-2">Singular</th>
                          <th className="text-left py-2">Plural</th>
                        </tr>
                      </thead>
                      <tbody>
                        {inflections.inflections.map((i: { case_name: string; singular: string; plural: string }, idx: number) => (
                          <tr key={idx} className="border-b border-gray-100">
                            <td className="py-2">{i.case_name}</td>
                            <td className="py-2">{i.singular || '—'}</td>
                            <td className="py-2">{i.plural || '—'}</td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                </div>
              )}
              {inflections.verb_forms?.length > 0 && (
                <div>
                  <h4 className="text-sm font-medium text-gray-600 mb-2">Verb Forms</h4>
                  <div className="overflow-x-auto">
                    <table className="min-w-full text-sm">
                      <thead>
                        <tr className="border-b">
                          <th className="text-left py-2">Form</th>
                          <th className="text-left py-2">Value</th>
                          <th className="text-left py-2">Tense</th>
                        </tr>
                      </thead>
                      <tbody>
                        {inflections.verb_forms.map((v: { form_name: string; form_value: string; tense: string }, idx: number) => (
                          <tr key={idx} className="border-b border-gray-100">
                            <td className="py-2">{v.form_name}</td>
                            <td className="py-2">{v.form_value}</td>
                            <td className="py-2">{v.tense || '—'}</td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                </div>
              )}
              {(!inflections.inflections?.length && !inflections.verb_forms?.length) && (
                <p className="text-gray-500">No inflections yet. Enable OpenAI for auto-generation.</p>
              )}
            </div>
          ) : null}
        </div>
      )}
    </div>
  )
}
