/**
 * Axios client pre-configured to talk to the KrishiDrishti FastAPI backend.
 *
 * Base URL is empty so all requests go to /api/..., which Vite's dev proxy
 * forwards to http://127.0.0.1:8000.  In production, set VITE_API_BASE_URL.
 */
import axios from 'axios'

const BASE_URL = import.meta.env.VITE_API_BASE_URL ?? ''

export const api = axios.create({
  baseURL: BASE_URL,
  headers: { 'Content-Type': 'application/json' },
})

// Attach JWT on every request if one is stored.
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('kd_token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

// On 401, clear stale token so the user is redirected to login.
api.interceptors.response.use(
  (res) => res,
  (err) => {
    if (err.response?.status === 401) {
      localStorage.removeItem('kd_token')
      localStorage.removeItem('kd_user')
      // Redirect without hard-importing the router to avoid circular deps.
      if (!window.location.pathname.startsWith('/login')) {
        window.location.href = '/login'
      }
    }
    return Promise.reject(err)
  },
)
