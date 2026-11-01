import { useEffect, useState } from 'react'
import { Link, useNavigate, useParams } from 'react-router-dom'
import { scansApi } from '../api/scans'
import type { Advisory, Scan } from '../api/types'
import { useAuth } from '../context/AuthContext'
import Button from '../components/ui/Button'
import Spinner from '../components/ui/Spinner'
import Alert from '../components/ui/Alert'
import PredictionCard from '../components/scan/PredictionCard'
import AdvisoryCard from '../components/scan/AdvisoryCard'

export default function ScanDetailPage() {
  const { id }      = useParams<{ id: string }>()
  const { user }    = useAuth()
  const navigate    = useNavigate()

  const [scan,      setScan]      = useState<Scan | null>(null)
  const [advisory,  setAdvisory]  = useState<Advisory | null>(null)
  const [loading,   setLoading]   = useState(true)
  const [error,     setError]     = useState('')
  const [feedback,  setFeedback]  = useState<boolean | null>(null)
  const [fbDone,    setFbDone]    = useState(false)

  const lang = user?.preferred_language ?? 'en'

  useEffect(() => {
    if (!id) return
    scansApi.get(Number(id))
      .then((s) => {
        setScan(s)
        if (s.disease_id) {
          scansApi.getAdvisory(s.disease_id, lang).then(setAdvisory).catch(() => {})
        }
      })
      .catch(() => setError('Scan not found or access denied.'))
      .finally(() => setLoading(false))
  }, [id, lang])

  async function handleFeedback(correct: boolean) {
    if (!scan) return
    try {
      await scansApi.submitFeedback(scan.id, correct)
      setFeedback(correct)
      setFbDone(true)
    } catch { /* non-critical */ }
  }

  async function handleDelete() {
    if (!scan) return
    if (!confirm('Delete this scan? This cannot be undone.')) return
    await scansApi.delete(scan.id)
    navigate('/history')
  }

  if (loading) return <div className="max-w-2xl mx-auto px-4 py-8"><Spinner /></div>

  if (error || !scan) return (
    <div className="max-w-2xl mx-auto px-4 py-8">
      <Alert kind="error">{error || 'Scan not found.'}</Alert>
      <Link to="/history" className="mt-4 inline-block">
        <Button variant="secondary" className="mt-4">Back to my scans</Button>
      </Link>
    </div>
  )

  return (
    <div className="max-w-2xl mx-auto px-4 py-8">
      <div className="flex items-center justify-between mb-6">
        <Link to="/history" className="text-sm text-brand-600 hover:underline flex items-center gap-1">
          <svg className="h-4 w-4" fill="none" stroke="currentColor" strokeWidth="2" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" d="M10 19l-7-7m0 0l7-7m-7 7h18" />
          </svg>
          Back to my scans
        </Link>
        <button
          onClick={handleDelete}
          className="text-xs text-earth-400 hover:text-red-500 transition-colors"
        >
          Delete scan
        </button>
      </div>

      <p className="text-sm text-earth-400 mb-4">
        Scanned on {new Date(scan.created_at).toLocaleString('en-IN')}
      </p>

      <div className="flex flex-col gap-5">
        <PredictionCard scan={scan} />

        {advisory && <AdvisoryCard advisory={advisory} />}

        {/* Feedback */}
        <div className="bg-white border border-cream-300 rounded-lg p-4">
          <p className="text-sm font-medium text-earth-700 mb-3">
            Was this identification helpful?
          </p>
          {fbDone ? (
            <p className="text-sm text-brand-600">
              Thank you for your feedback{feedback === true ? ' — glad it helped.' : '.'}
            </p>
          ) : (
            <div className="flex gap-3">
              <Button variant="secondary" size="sm" onClick={() => handleFeedback(true)}>
                Yes, looks correct
              </Button>
              <Button variant="ghost" size="sm" onClick={() => handleFeedback(false)}>
                No, seems wrong
              </Button>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
