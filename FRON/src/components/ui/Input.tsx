import React from 'react'

interface Props extends React.InputHTMLAttributes<HTMLInputElement> {
  label?: string
  error?: string
  hint?: string
}

export default function Input({ label, error, hint, id, className = '', ...rest }: Props) {
  const inputId = id ?? label?.toLowerCase().replace(/\s+/g, '-')
  return (
    <div className="flex flex-col gap-1">
      {label && (
        <label htmlFor={inputId} className="text-sm font-medium text-earth-700">
          {label}
        </label>
      )}
      <input
        id={inputId}
        {...rest}
        className={`
          w-full rounded-lg border px-3 py-2.5 text-sm outline-none
          transition-colors duration-150
          ${error
            ? 'border-red-400 focus:border-red-500 focus:ring-1 focus:ring-red-400'
            : 'border-cream-300 bg-cream-50/50 focus:border-brand-500 focus:ring-1 focus:ring-brand-400'
          }
          disabled:bg-cream-100 disabled:text-earth-400
          ${className}
        `}
      />
      {error && <p className="text-xs text-red-600">{error}</p>}
      {hint && !error && <p className="text-xs text-gray-500">{hint}</p>}
    </div>
  )
}
