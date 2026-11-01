/**
 * AuthContext — global auth state.
 *
 * Stores the JWT in localStorage (kd_token) and the user profile (kd_user).
 * The Axios interceptor in client.ts reads kd_token automatically on every
 * request, so components just need to call login/logout here.
 */
import React, { createContext, useCallback, useContext, useEffect, useState } from 'react'
import { authApi } from '../api/auth'
import type { User } from '../api/types'

interface AuthContextValue {
  user: User | null
  token: string | null
  loading: boolean
  login: (email: string, password: string) => Promise<void>
  signup: (email: string, password: string, fullName: string, lang?: string) => Promise<void>
  logout: () => void
  refreshUser: () => Promise<void>
}

const AuthContext = createContext<AuthContextValue | null>(null)

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<User | null>(() => {
    const s = localStorage.getItem('kd_user')
    return s ? JSON.parse(s) : null
  })
  const [token, setToken] = useState<string | null>(() => localStorage.getItem('kd_token'))
  const [loading, setLoading] = useState(true)

  // On mount only: re-validate the stored token by fetching /api/users/me.
  // We use an empty dependency array so this only runs once at startup.
  useEffect(() => {
    const storedToken = localStorage.getItem('kd_token')
    if (!storedToken) { setLoading(false); return }
    authApi.getMe()
      .then((u) => { setUser(u); localStorage.setItem('kd_user', JSON.stringify(u)) })
      .catch(() => {
        localStorage.removeItem('kd_token')
        localStorage.removeItem('kd_user')
        setToken(null); setUser(null)
      })
      .finally(() => setLoading(false))
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [])

  const login = useCallback(async (email: string, password: string) => {
    const t = await authApi.login({ email, password })
    localStorage.setItem('kd_token', t.access_token)
    setToken(t.access_token)
    const u = await authApi.getMe()
    setUser(u)
    localStorage.setItem('kd_user', JSON.stringify(u))
  }, [])

  const signup = useCallback(async (
    email: string, password: string, fullName: string, lang = 'en'
  ) => {
    await authApi.signup({ email, password, full_name: fullName, preferred_language: lang })
    await login(email, password)
  }, [login])

  const logout = useCallback(() => {
    authApi.logout().catch(() => {})
    localStorage.removeItem('kd_token')
    localStorage.removeItem('kd_user')
    setToken(null)
    setUser(null)
  }, [])

  const refreshUser = useCallback(async () => {
    const u = await authApi.getMe()
    setUser(u)
    localStorage.setItem('kd_user', JSON.stringify(u))
  }, [])

  return (
    <AuthContext.Provider value={{ user, token, loading, login, signup, logout, refreshUser }}>
      {children}
    </AuthContext.Provider>
  )
}

export function useAuth() {
  const ctx = useContext(AuthContext)
  if (!ctx) throw new Error('useAuth must be used inside AuthProvider')
  return ctx
}
