import { BrowserRouter, Navigate, Outlet, Route, Routes } from 'react-router-dom'
import { AuthProvider } from './context/AuthContext'
import ProtectedRoute    from './components/layout/ProtectedRoute'
import Navbar            from './components/layout/Navbar'
import LoginPage         from './pages/LoginPage'
import SignupPage        from './pages/SignupPage'
import HomePage          from './pages/HomePage'
import ScanPage          from './pages/ScanPage'
import HistoryPage       from './pages/HistoryPage'
import ScanDetailPage    from './pages/ScanDetailPage'
import ProfilePage       from './pages/ProfilePage'

/** Layout wrapper that shows Navbar above the page content. */
function AppLayout() {
  return (
    <>
      <Navbar />
      <main className="flex-1">
        <Outlet />
      </main>
    </>
  )
}

export default function App() {
  return (
    <BrowserRouter>
      <AuthProvider>
        <div className="min-h-screen flex flex-col">
          <Routes>
            {/* Public routes — no Navbar, no auth required */}
            <Route path="/login"  element={<LoginPage />} />
            <Route path="/signup" element={<SignupPage />} />

            {/* Protected routes — require auth, wrapped in Navbar */}
            <Route element={<ProtectedRoute />}>
              <Route element={<AppLayout />}>
                <Route path="/"          element={<HomePage />} />
                <Route path="/scan"      element={<ScanPage />} />
                <Route path="/history"   element={<HistoryPage />} />
                <Route path="/scans/:id" element={<ScanDetailPage />} />
                <Route path="/profile"   element={<ProfilePage />} />
                <Route path="*"          element={<Navigate to="/" replace />} />
              </Route>
            </Route>
          </Routes>
        </div>
      </AuthProvider>
    </BrowserRouter>
  )
}
