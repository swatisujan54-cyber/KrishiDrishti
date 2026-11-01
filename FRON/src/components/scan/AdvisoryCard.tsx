import { useState } from 'react'
import type { Advisory } from '../../api/types'

interface Section {
  title: string
  content: string | undefined
}

export default function AdvisoryCard({ advisory }: { advisory: Advisory }) {
  const [expanded, setExpanded] = useState<string | null>('symptoms')

  const sections: Section[] = [
    { title: 'Symptoms',              content: advisory.symptoms },
    { title: 'Possible Causes',       content: advisory.possible_causes },
    { title: 'Preventive Measures',   content: advisory.preventive_measures },
    { title: 'Recommended Next Steps',content: advisory.recommended_next_steps },
    { title: 'Expert Guidance',       content: advisory.expert_consultation_guidance },
  ].filter((s) => s.content)

  return (
    <div className="rounded-lg border border-cream-300 bg-white p-5">
      <div className="flex items-center justify-between mb-4">
        <h3 className="font-semibold text-earth-900">Disease Advisory</h3>
        <div className="flex items-center gap-2">
          {advisory.is_translated && (
            <span className="text-xs bg-brand-100 text-brand-700 rounded px-2 py-0.5 font-medium">
              {advisory.language.toUpperCase()}
            </span>
          )}
          <span className={`text-xs rounded px-2 py-0.5 font-medium ${
            advisory.review_status === 'reviewed'
              ? 'bg-brand-100 text-brand-700'
              : advisory.review_status === 'demonstration'
              ? 'bg-harvest-400/15 text-harvest-600'
              : 'bg-cream-200 text-earth-500'
          }`}>
            {advisory.review_status === 'reviewed' ? 'Reviewed' : advisory.review_status === 'demonstration' ? 'Demo data' : 'Unreviewed'}
          </span>
        </div>
      </div>

      {/* Advisory sections */}
      <div className="flex flex-col gap-1">
        {sections.map((s) => (
          <div key={s.title} className="border border-cream-200 rounded-lg overflow-hidden">
            <button
              onClick={() => setExpanded(expanded === s.title ? null : s.title)}
              className="w-full flex items-center justify-between px-4 py-3 text-sm font-medium text-earth-700 hover:bg-cream-50 transition-colors text-left"
            >
              {s.title}
              <svg
                className={`h-4 w-4 text-earth-400 flex-shrink-0 transition-transform ${expanded === s.title ? 'rotate-180' : ''}`}
                fill="none" stroke="currentColor" strokeWidth="2" viewBox="0 0 24 24"
              >
                <path strokeLinecap="round" strokeLinejoin="round" d="M19 9l-7 7-7-7" />
              </svg>
            </button>
            {expanded === s.title && (
              <div className="px-4 pb-3 text-sm text-earth-600 leading-relaxed border-t border-cream-200">
                {s.content}
              </div>
            )}
          </div>
        ))}
      </div>

      {/* Disclaimer */}
      <p className="mt-4 text-xs text-earth-600 bg-harvest-400/5 border border-harvest-400/20 rounded-lg p-3 leading-relaxed">
        {advisory.disclaimer}
      </p>

      {advisory.advisory_source && (
        <p className="mt-2 text-xs text-earth-400">Source: {advisory.advisory_source}</p>
      )}
    </div>
  )
}
