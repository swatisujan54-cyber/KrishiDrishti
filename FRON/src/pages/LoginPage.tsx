import React, { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
import Button from '../components/ui/Button'
import Input from '../components/ui/Input'
import Alert from '../components/ui/Alert'

export default function LoginPage() {
  const { login } = useAuth()
  const navigate   = useNavigate()

  const [email,    setEmail]    = useState('')
  const [password, setPassword] = useState('')
  const [loading,  setLoading]  = useState(false)
  const [error,    setError]    = useState('')

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault()
    setError('')
    setLoading(true)
    try {
      await login(email, password)
      navigate('/')
    } catch (err: any) {
      setError(err.response?.data?.detail ?? 'Login failed. Please check your credentials.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen flex">
      {/* Left panel — warm welcome for farmers */}
      <div className="hidden md:flex md:w-2/5 bg-brand-800 flex-col justify-between p-10 relative overflow-hidden">
        {/* Subtle texture overlay */}
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
            Understand your crop's health
          </h2>
          <p className="text-cream-200 text-sm leading-relaxed max-w-xs">
            Take a photo of an affected leaf, and KrishiDrishti will help identify the problem
            and suggest practical next steps.
          </p>
          <p className="text-brand-300 text-xs pt-4 border-t border-brand-700 max-w-xs">
            A decision-support tool for farmers. Always confirm with your local
            agricultural officer before acting on any advice.
          </p>
        </div>
      </div>

      {/* Right panel — login form */}
      <div className="flex-1 flex flex-col items-center justify-center px-6 py-12 bg-cream-50">
        <div className="w-full max-w-sm">
          {/* Mobile logo */}
          <div className="flex items-center gap-2 font-bold text-xl text-brand-800 mb-8 md:hidden">
            <svg className="h-6 w-6 text-brand-600" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5">
              <path strokeLinecap="round" strokeLinejoin="round" d="M12 21c-4.97 0-9-3.582-9-8 0-3.866 3-7 7-7 1.657 0 3 .5 4 1.5C15 5.5 16.343 5 18 5c.35 0 .685.04 1 .115M12 21c4.97 0 9-3.582 9-8 0-1.5-.5-3-1.5-4M12 21V8" />
            </svg>
            KrishiDrishti
          </div>

          <h1 className="text-2xl font-bold text-earth-900 mb-1">Sign in</h1>
          <p className="text-sm text-earth-500 mb-8">Welcome back. Enter your details to continue.</p>

          {error && <Alert kind="error" className="mb-4">{error}</Alert>}

          <form onSubmit={handleSubmit} className="flex flex-col gap-4">
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
              autoComplete="current-password"
              required
            />
            <Button type="submit" loading={loading} size="lg" className="mt-2">
              Sign in
            </Button>
          </form>

          <p className="text-center text-sm text-earth-600 mt-6">
            New here?{' '}
            <Link to="/signup" className="text-brand-600 font-medium hover:underline">
              Create an account
            </Link>
          </p>
        </div>
      </div>
    </div>
  )
}
