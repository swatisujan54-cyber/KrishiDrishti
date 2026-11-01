import React, { useState } from 'react'
import { useAuth } from '../context/AuthContext'
import { authApi } from '../api/auth'
import Button from '../components/ui/Button'
import Input from '../components/ui/Input'
import Alert from '../components/ui/Alert'

const LANGUAGES = [
  { code: 'en', label: 'English' },
  { code: 'hi', label: 'हिन्दी (Hindi)' },
]

export default function ProfilePage() {
  const { user, refreshUser } = useAuth()

  const [fullName,  setFullName]  = useState(user?.full_name ?? '')
  const [lang,      setLang]      = useState(user?.preferred_language ?? 'en')
  const [password,  setPassword]  = useState('')
  const [loading,   setLoading]   = useState(false)
  const [success,   setSuccess]   = useState('')
  const [error,     setError]     = useState('')

  async function handleSave(e: React.FormEvent) {
    e.preventDefault()
    setError(''); setSuccess('')
    if (password && password.length < 8) {
      setError('New password must be at least 8 characters.')
      return
    }
    setLoading(true)
    try {
      await authApi.updateMe({
        full_name: fullName,
        preferred_language: lang,
        ...(password ? { password } : {}),
      })
      await refreshUser()
      setPassword('')
      setSuccess('Your details have been saved.')
    } catch (err: any) {
      setError(err.response?.data?.detail ?? 'Could not save changes.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="max-w-lg mx-auto px-4 py-8">
      <h1 className="text-2xl font-bold text-earth-900 mb-1">Your Account</h1>
      <p className="text-sm text-earth-500 mb-6">Manage your profile and preferences.</p>

      <div className="bg-white border border-cream-300 rounded-lg p-6">
        {/* Account summary */}
        <div className="mb-6 pb-5 border-b border-cream-200">
          <p className="text-xs text-earth-400 uppercase tracking-wide">Email</p>
          <p className="font-medium text-earth-800 mt-0.5">{user?.email}</p>
          <p className="text-xs text-earth-400 mt-2">Account type: {user?.role}</p>
        </div>

        {success && <Alert kind="success" className="mb-4">{success}</Alert>}
        {error   && <Alert kind="error"   className="mb-4">{error}</Alert>}

        <form onSubmit={handleSave} className="flex flex-col gap-4">
          <Input
            label="Full name"
            value={fullName}
            onChange={(e) => setFullName(e.target.value)}
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
            <p className="text-xs text-earth-400">
              Advisory information will be shown in this language when a translation is available.
            </p>
          </div>

          <Input
            label="New password (leave blank to keep current)"
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            hint="At least 8 characters"
          />

          <Button type="submit" loading={loading} className="mt-2">
            Save changes
          </Button>
        </form>
      </div>
    </div>
  )
}
