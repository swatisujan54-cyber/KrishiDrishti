import type { Scan } from '../../api/types'

const STATUS_STYLES = {
  completed:   'bg-brand-50  border-brand-200  text-brand-800',
  uncertain:   'bg-harvest-400/10 border-harvest-400/30 text-earth-700',
  unsupported: 'bg-cream-200 border-cream-300 text-earth-500',
  failed:      'bg-red-50    border-red-200    text-red-700',
  pending:     'bg-cream-100 border-cream-200 text-earth-500',
}

const STATUS_LABELS = {
  completed:   'Identification complete',
  uncertain:   'Low confidence — result uncertain',
  unsupported: 'This crop is not yet supported by the disease model',
  failed:      'Could not identify the disease',
  pending:     'Processing…',
}

export default function PredictionCard({ scan }: { scan: Scan }) {
  const statusStyle = STATUS_STYLES[scan.prediction_status]
  const statusLabel = STATUS_LABELS[scan.prediction_status]
  const confidence  = scan.confidence != null ? `${(scan.confidence * 100).toFixed(1)}%` : null

  return (
    <div className={`rounded-lg border p-5 ${statusStyle}`}>
      {/* Header */}
      <div className="flex items-start justify-between gap-4 mb-4">
        <div className="flex-1">
          <p className="text-xs font-medium uppercase tracking-wide opacity-70 mb-1">{statusLabel}</p>
          {scan.predicted_label ? (
            <h2 className="text-xl font-bold text-earth-900">{formatLabel(scan.predicted_label)}</h2>
          ) : (
            <h2 className="text-xl font-bold text-earth-400">No disease identified</h2>
          )}
          <p className="text-sm text-earth-500 mt-0.5">
            Crop: <strong className="text-earth-700">{scan.crop_name}</strong>
          </p>
        </div>
        {confidence && (
          <div className="text-right flex-shrink-0">
            <p className="text-2xl font-bold text-earth-800">{confidence}</p>
            <p className="text-xs text-earth-400">confidence</p>
          </div>
        )}
      </div>

      {/* Confidence bar */}
      {scan.confidence != null && (
        <div className="w-full bg-white/60 rounded-full h-2 mb-4">
          <div
            className={`h-2 rounded-full transition-all ${
              scan.confidence >= 0.5 ? 'bg-brand-500' : 'bg-harvest-500'
            }`}
            style={{ width: `${scan.confidence * 100}%` }}
          />
        </div>
      )}

      {/* Top predictions */}
      {scan.top_predictions && scan.top_predictions.length > 1 && (
        <div className="mt-3 pt-3 border-t border-current/10">
          <p className="text-xs font-medium text-earth-500 mb-2">Other possible matches:</p>
          <ul className="flex flex-col gap-1.5">
            {scan.top_predictions.slice(1).map((p, i) => (
              <li key={i} className="flex items-center justify-between text-sm">
                <span className="text-earth-600">{formatLabel(p.label)}</span>
                <span className="font-mono text-earth-400">{(p.confidence * 100).toFixed(1)}%</span>
              </li>
            ))}
          </ul>
        </div>
      )}

      {/* Mock warning */}
      {scan.is_mock_prediction && (
        <p className="mt-4 text-xs border-t border-current/10 pt-3 text-earth-500">
          This result was produced by a demonstration model, not a trained AI.
          It should not be relied upon for real decisions. Please consult an agricultural expert.
        </p>
      )}

      {/* Uncertainty guidance */}
      {scan.prediction_status === 'uncertain' && (
        <p className="mt-4 text-xs border-t border-current/10 pt-3">
          The model's confidence is below the acceptable threshold. This result is indicative only —
          please seek confirmation from a qualified agricultural expert.
        </p>
      )}

      {/* Unsupported guidance */}
      {scan.prediction_status === 'unsupported' && (
        <p className="mt-4 text-xs border-t border-current/10 pt-3">
          We can still store this scan for your records. Disease identification for this crop
          may be added in a future update.
        </p>
      )}

      <p className="mt-3 text-xs text-earth-400">Analysis model: {scan.model_version ?? 'unknown'}</p>
    </div>
  )
}

function formatLabel(label: string): string {
  // "Tomato___Early_blight" → "Early blight (Tomato)"
  const parts = label.split('___')
  if (parts.length === 2) {
    const crop    = parts[0].replace(/_/g, ' ')
    const disease = parts[1].replace(/_/g, ' ')
    return `${disease} (${crop})`
  }
  return label.replace(/_/g, ' ')
}
