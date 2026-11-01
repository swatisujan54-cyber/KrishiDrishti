import { Link, NavLink, useNavigate } from 'react-router-dom'
import { useAuth } from '../../context/AuthContext'

export default function Navbar() {
  const { user, logout } = useAuth()
  const navigate = useNavigate()

  function handleLogout() {
    logout()
    navigate('/login')
  }

  return (
    <nav className="bg-brand-800 text-cream-100 border-b border-brand-900/30">
      <div className="max-w-5xl mx-auto px-4 h-14 flex items-center justify-between">
        {/* Logo — text-based, clean */}
        <Link to="/" className="flex items-center gap-2 font-bold text-lg tracking-tight text-cream-50">
          <svg className="h-5 w-5 text-brand-300" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5">
            <path strokeLinecap="round" strokeLinejoin="round" d="M12 21c-4.97 0-9-3.582-9-8 0-3.866 3-7 7-7 1.657 0 3 .5 4 1.5C15 5.5 16.343 5 18 5c.35 0 .685.04 1 .115M12 21c4.97 0 9-3.582 9-8 0-1.5-.5-3-1.5-4M12 21V8" />
          </svg>
          KrishiDrishti
        </Link>

        {/* Nav links */}
        {user && (
          <div className="flex items-center gap-1 text-sm">
            <NavLink
              to="/scan"
              className={({ isActive }) =>
                `px-3 py-1.5 rounded-md transition-colors ${isActive ? 'bg-brand-700 text-cream-50' : 'text-cream-200 hover:bg-brand-700/60 hover:text-cream-50'}`
              }
            >
              Check Crop
            </NavLink>
            <NavLink
              to="/history"
              className={({ isActive }) =>
                `px-3 py-1.5 rounded-md transition-colors ${isActive ? 'bg-brand-700 text-cream-50' : 'text-cream-200 hover:bg-brand-700/60 hover:text-cream-50'}`
              }
            >
              My Scans
            </NavLink>
            <NavLink
              to="/profile"
              className={({ isActive }) =>
                `px-3 py-1.5 rounded-md transition-colors ${isActive ? 'bg-brand-700 text-cream-50' : 'text-cream-200 hover:bg-brand-700/60 hover:text-cream-50'}`
              }
            >
              {user.full_name.split(' ')[0]}
            </NavLink>
            <button
              onClick={handleLogout}
              className="px-3 py-1.5 rounded-md text-cream-200 hover:bg-brand-700/60 hover:text-cream-50 transition-colors"
            >
              Sign out
            </button>
          </div>
        )}
      </div>
    </nav>
  )
}
