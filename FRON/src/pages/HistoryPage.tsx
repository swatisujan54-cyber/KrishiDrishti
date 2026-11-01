import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { scansApi } from '../api/scans'
import type { ScanListItem } from '../api/types'
import Button from '../components/ui/Button'
import Spinner from '../components/ui/Spinner'
import Alert from '../components/ui/Alert'

const STATUS_BADGE: Record<string, string> = {
  completed:   'bg-brand-100 text-brand-700',
  uncertain:   'bg-harvest-400/15 text-harvest-600',
  unsupported: 'bg-cream-200  text-earth-500',
  failed:      'bg-red-100   text-red-700',
  pending:     'bg-cream-100  text-earth-400',
}

const STATUS_LABEL: Record<string, string> = {
  completed:   'Identified',
  uncertain:   'Uncertain',
  unsupported: 'Not supported',
  failed:      'Failed',
  pending:     'Pending',
}

export default function HistoryPage() {
  const [scans,   setScans]   = useState<ScanListItem[]>([])
  const [loading, setLoading] = useState(true)
  const [error,   setError]   = useState('')
  const [page,    setPage]    = useState(1)
  const [total,   setTotal]   = useState(0)

  useEffect(() => { fetchPage(page) }, [page])

  async function fetchPage(p: number) {
    setLoading(true)
    setError('')
    try {
      const data = await scansApi.list(p, 10)
      setScans(data.items)
      setTotal(data.meta.total)
    } catch {
      setError('Could not load your scans. Please try again.')
    } finally {
      setLoading(false)
    }
  }

  async function handleDelete(id: number) {
    if (!confirm('Delete this scan? This cannot be undone.')) return
    try {
      await scansApi.delete(id)
      fetchPage(page)
    } catch {
      alert('Could not delete scan.')
    }
  }

  if (loading) return <div className="max-w-2xl mx-auto px-4 py-8"><Spinner /></div>

  return (
    <div className="max-w-2xl mx-auto px-4 py-8">
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-2xl font-bold text-earth-900">My Scans</h1>
          <p className="text-sm text-earth-500 mt-1">Your previous crop checks and results.</p>
        </div>
        <Link to="/scan">
          <Button>Check a crop</Button>
        </Link>
      </div>

      {error && <Alert kind="error" className="mb-4">{error}</Alert>}

      {scans.length === 0 && !loading ? (
        <div className="text-center py-16">
          <div className="w-16 h-16 mx-auto mb-4 bg-cream-200 rounded-full flex items-center justify-center">
            <svg className="h-8 w-8 text-earth-400" fill="none" stroke="currentColor" strokeWidth="1.5" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" d="M12 6.042A8.967 8.967 0 006 3.75c-1.052 0-2.062.18-3 .512v14.25A8.987 8.987 0 016 18c2.305 0 4.408.867 6 2.292m0-14.25a8.966 8.966 0 016-2.292c1.052 0 2.062.18 3 .512v14.25A8.987 8.987 0 0018 18a8.967 8.967 0 00-6 2.292m0-14.25v14.25" />
            </svg>
          </div>
          <p className="text-lg font-medium text-earth-700">No scans yet</p>
          <p className="text-sm text-earth-400 mt-1 max-w-xs mx-auto">
            When you check a crop, your results will appear here for future reference.
          </p>
          <Link to="/scan" className="mt-6 inline-block">
            <Button>Check your first crop</Button>
          </Link>
        </div>
      ) : (
        <div className="flex flex-col gap-2">
          {scans.map((s) => (
            <div
              key={s.id}
              className="flex items-center justify-between gap-4 bg-white border border-cream-300 rounded-lg p-4 hover:border-brand-300 transition-colors"
            >
              <Link to={`/scans/${s.id}`} className="flex-1 min-w-0">
                <div>
                  <p className="font-medium text-earth-800 truncate">
                    {s.disease_name ?? s.predicted_label ?? s.crop_name}
                  </p>
                  <p className="text-sm text-earth-400">
                    {s.crop_name} · {new Date(s.created_at).toLocaleDateString('en-IN', { day: 'numeric', month: 'short', year: 'numeric' })}
                  </p>
                </div>
              </Link>
              <div className="flex items-center gap-2 flex-shrink-0">
                <span className={`text-xs font-medium rounded px-2 py-1 ${STATUS_BADGE[s.prediction_status]}`}>
                  {STATUS_LABEL[s.prediction_status] ?? s.prediction_status}
                </span>
                {s.confidence != null && (
                  <span className="text-xs text-earth-400">{(s.confidence * 100).toFixed(0)}%</span>
                )}
                <button
                  onClick={() => handleDelete(s.id)}
                  className="ml-1 text-earth-300 hover:text-red-500 transition-colors p-1 rounded"
                  title="Delete scan"
                  aria-label="Delete scan"
                >
                  <svg className="h-4 w-4" fill="none" stroke="currentColor" strokeWidth="1.5" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" d="M14.74 9l-.346 9m-4.788 0L9.26 9m9.968-3.21c.342.052.682.107 1.022.166m-1.022-.165L18.16 19.673a2.25 2.25 0 01-2.244 2.077H8.084a2.25 2.25 0 01-2.244-2.077L4.772 5.79m14.456 0a48.108 48.108 0 00-3.478-.397m-12 .562c.34-.059.68-.114 1.022-.165m0 0a48.11 48.11 0 013.478-.397m7.5 0v-.916c0-1.18-.91-2.164-2.09-2.201a51.964 51.964 0 00-3.32 0c-1.18.037-2.09 1.022-2.09 2.201v.916m7.5 0a48.667 48.667 0 00-7.5 0" />
                  </svg>
                </button>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Pagination */}
      {total > 10 && (
        <div className="flex justify-center gap-3 mt-6">
          <Button
            variant="secondary" size="sm"
            disabled={page === 1}
            onClick={() => setPage((p) => p - 1)}
          >
            Previous
          </Button>
          <span className="text-sm text-earth-400 py-1.5">
            Page {page} / {Math.ceil(total / 10)}
          </span>
          <Button
            variant="secondary" size="sm"
            disabled={page * 10 >= total}
            onClick={() => setPage((p) => p + 1)}
          >
            Next
          </Button>
        </div>
      )}
    </div>
  )
}
