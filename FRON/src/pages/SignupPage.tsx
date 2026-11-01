import React, { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
import Button from '../components/ui/Button'
import Input from '../components/ui/Input'
import Alert from '../components/ui/Alert'

const LANGUAGES = [
  { code: 'en', label: 'English' },
  { code: 'hi', label: 'हिन्दी (Hindi)' },
]

export default function SignupPage() {
  const { signup } = useAuth()
  const navigate   = useNavigate()

  const [fullName,  setFullName]  = useState('')
  const [email,     setEmail]     = useState('')
  const [password,  setPassword]  = useState('')
  const [lang,      setLang]      = useState('en')
  const [loading,   setLoading]   = useState(false)
  const [error,     setError]     = useState('')

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault()
    if (password.length < 8) {
      setError('Password must be at least 8 characters.')
      return
    }
    setError('')
    setLoading(true)
    try {
      await signup(email, password, fullName, lang)
      navigate('/')
    } catch (err: any) {
      setError(err.response?.data?.detail ?? 'Registration failed. Please try again.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen flex">
      {/* Left panel — warm welcome */}
      <div className="hidden md:flex md:w-2/5 bg-brand-800 flex-col justify-between p-10 relative overflow-hidden">
        <div className="absolute inset-0 opacity-10" style={{
          backgroundImage: 'radial-gradient(circle at 20% 80%, #a8b88a 1px, transparent 1px), radial-gradient(circle at 80% 20%, #638046 1px, transparent 1px)',
          backgroundSize: '40px 40px',
        }} />

        <div className="relative z-10">
          <Link to="/" className="flex items-center gap-2 font-bold text-xl text-cream-50">
            <svg className="h-6 w-6 text-brand-300" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5">
              <path strokeLinecap="round" strokeLinejoin="round" d="M12 21c-4.97 0-9-3.582-9-8 0-3.866 3-7 7-7 1.657 0 3 .5 4 1.5C15 5.5 16.343 5 18 5c.35 0 .685.04 1 .115M12 21c4.97 0 9-3.582 9-8 0-1.5-.5-3-1.5-4M12 21V8" />
            </svg>
            KrishiDrishti
          </Link>
        </div>

        <div className="relative z-10 space-y-4">
          <h2 className="text-2xl font-bold text-cream-50 leading-snug">
            Join thousands of farmers
          </h2>
          <p className="text-cream-200 text-sm leading-relaxed max-w-xs">
            Get help identifying crop diseases early. Upload a photo, understand the problem,
            and take the right action before it spreads.
          </p>
          <p className="text-brand-300 text-xs pt-4 border-t border-brand-700 max-w-xs">
            Free to use. Your data stays private — only you can see your scans.
          </p>
        </div>
      </div>

      {/* Right panel — signup form */}
      <div className="flex-1 flex flex-col items-center justify-center px-6 py-12 bg-cream-50">
        <div className="w-full max-w-sm">
          {/* Mobile logo */}
          <div className="flex items-center gap-2 font-bold text-xl text-brand-800 mb-8 md:hidden">
            <svg className="h-6 w-6 text-brand-600" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5">
              <path strokeLinecap="round" strokeLinejoin="round" d="M12 21c-4.97 0-9-3.582-9-8 0-3.866 3-7 7-7 1.657 0 3 .5 4 1.5C15 5.5 16.343 5 18 5c.35 0 .685.04 1 .115M12 21c4.97 0 9-3.582 9-8 0-1.5-.5-3-1.5-4M12 21V8" />
            </svg>
            KrishiDrishti
          </div>

          <h1 className="text-2xl font-bold text-earth-900 mb-1">Create your account</h1>
          <p className="text-sm text-earth-500 mb-8">It takes less than a minute.</p>

          {error && <Alert kind="error" className="mb-4">{error}</Alert>}

          <form onSubmit={handleSubmit} className="flex flex-col gap-4">
            <Input
              label="Full name"
              value={fullName}
              onChange={(e) => setFullName(e.target.value)}
              placeholder="e.g. Ramesh Kumar"
              required
            />
            <Input
              label="Email address"
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              autoComplete="email"
              required
            />
            <Input
              label="Password"
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              hint="At least 8 characters"
              autoComplete="new-password"
              required
            />
            <div className="flex flex-col gap-1">
              <label className="text-sm font-medium text-earth-700">Preferred language</label>
              <select
                value={lang}
                onChange={(e) => setLang(e.target.value)}
                className="w-full rounded-lg border border-cream-300 bg-cream-50/50 px-3 py-2.5 text-sm outline-none focus:border-brand-500 focus:ring-1 focus:ring-brand-400"
              >
                {LANGUAGES.map((l) => (
                  <option key={l.code} value={l.code}>{l.label}</option>
                ))}
              </select>
            </div>
            <Button type="submit" loading={loading} size="lg" className="mt-2">
              Create account
            </Button>
          </form>

          <p className="text-center text-sm text-earth-600 mt-6">
            Already have an account?{' '}
            <Link to="/login" className="text-brand-600 font-medium hover:underline">
              Sign in
            </Link>
          </p>
        </div>
      </div>
    </div>
  )
}
