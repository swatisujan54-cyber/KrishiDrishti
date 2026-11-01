import { Navigate, Outlet } from 'react-router-dom'
import { useAuth } from '../../context/AuthContext'
import Spinner from '../ui/Spinner'

/**
 * Wraps private routes: shows a spinner while auth is being validated,
 * then redirects to /login if no token exists.
 */
export default function ProtectedRoute() {
  const { user, loading } = useAuth()
  if (loading) return <Spinner label="Verifying session…" />
  if (!user)   return <Navigate to="/login" replace />
  return <Outlet />
}
