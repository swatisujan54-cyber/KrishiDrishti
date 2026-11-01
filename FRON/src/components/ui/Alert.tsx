import React from 'react'

type Kind = 'info' | 'success' | 'warning' | 'error'

const styles: Record<Kind, string> = {
  info:    'bg-brand-50  border-brand-200  text-brand-800',
  success: 'bg-brand-50 border-brand-200 text-brand-700',
  warning: 'bg-harvest-400/10 border-harvest-400/30 text-earth-700',
  error:   'bg-red-50   border-red-200   text-red-800',
}

export default function Alert({
  kind = 'info', title, children, className = '',
}: { kind?: Kind; title?: string; children: React.ReactNode; className?: string }) {
  return (
    <div className={`rounded-lg border p-4 text-sm ${styles[kind]} ${className}`}>
      {title && (
        <p className="font-semibold mb-1">{title}</p>
      )}
      <div>{children}</div>
    </div>
  )
}
