import { useState } from 'react'
import { useMutation, useQueryClient } from '@tanstack/react-query'
import { wordAPI } from '../lib/api'

const CSV_HELP = `Format: finnish,danish,english,word_type (one per line)
Example:
talo,hus,house,noun
kissa,kat,cat,noun
juosta,løbe,run,verb`

export default function BulkImport() {
  const queryClient = useQueryClient()
  const [csv, setCsv] = useState('')
  const [result, setResult] = useState<{ created: number; exists: number; errors: Array<{ row: number; word: string; error: string }> } | null>(null)

  const bulkMutation = useMutation({
    mutationFn: (rows: string[][]) => wordAPI.bulkAdd(rows),
    onSuccess: (data) => {
      setResult(data)
      queryClient.invalidateQueries({ queryKey: ['words'] })
      queryClient.invalidateQueries({ queryKey: ['stats'] })
    },
  })

  const parseCsv = (text: string): string[][] => {
    return text
      .trim()
      .split('\n')
      .map((line) => line.split(',').map((c) => c.trim()))
      .filter((row) => row.some((c) => c.length > 0))
  }

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    const rows = parseCsv(csv)
    if (rows.length === 0) return
    setResult(null)
    bulkMutation.mutate(rows)
  }

  return (
    <div className="bg-white rounded-lg shadow p-8">
      <h2 className="text-2xl font-bold text-gray-900 mb-6">Bulk Import</h2>
      <p className="text-gray-600 mb-4">
        Paste CSV data. Each line: finnish,danish,english,word_type. Header row is optional.
      </p>

      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">CSV Data</label>
          <textarea
            value={csv}
            onChange={(e) => setCsv(e.target.value)}
            placeholder={CSV_HELP}
            rows={12}
            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 font-mono text-sm"
          />
        </div>
        <button
          type="submit"
          disabled={bulkMutation.isPending || parseCsv(csv).length === 0}
          className="px-6 py-3 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 disabled:opacity-50"
        >
          {bulkMutation.isPending ? 'Importing...' : 'Import'}
        </button>
      </form>

      {result && (
        <div className="mt-6 p-4 bg-green-50 border border-green-200 rounded-lg">
          <p className="text-green-800 font-medium">
            Created: {result.created} | Already existed: {result.exists}
          </p>
          {result.errors.length > 0 && (
            <div className="mt-2 text-sm text-red-700">
              <p className="font-medium">Errors:</p>
              <ul className="list-disc list-inside mt-1">
                {result.errors.map((e, i) => (
                  <li key={i}>Row {e.row} ({e.word}): {e.error}</li>
                ))}
              </ul>
            </div>
          )}
        </div>
      )}

      {bulkMutation.isError && (
        <div className="mt-4 p-4 bg-red-50 border border-red-200 rounded-lg text-red-700">
          {String(bulkMutation.error)}
        </div>
      )}
    </div>
  )
}
