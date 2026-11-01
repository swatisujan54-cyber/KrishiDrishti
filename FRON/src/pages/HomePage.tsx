import { Link } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
import Button from '../components/ui/Button'

export default function HomePage() {
  const { user } = useAuth()
  const firstName = user?.full_name.split(' ')[0] ?? 'farmer'

  return (
    <div className="max-w-3xl mx-auto px-4 py-10">
      {/* Greeting */}
      <div className="mb-8">
        <h1 className="text-2xl font-bold text-earth-900">
          Namaste, {firstName}
        </h1>
        <p className="text-earth-500 mt-1">
          What would you like to do today?
        </p>
      </div>

      {/* Primary action — Check Your Crop */}
      <Link to="/scan" className="block group mb-6">
        <div className="bg-white border border-cream-300 rounded-lg p-6 hover:border-brand-400 transition-colors">
          <div className="flex items-start justify-between gap-4">
            <div className="flex-1">
              <h2 className="text-lg font-semibold text-earth-900 mb-1">
                Check Your Crop
              </h2>
              <p className="text-sm text-earth-500 leading-relaxed">
                Take a photo of an affected leaf and KrishiDrishti will help identify the problem.
                You'll get information about symptoms, causes, and practical next steps.
              </p>
              <span className="inline-flex items-center gap-1 mt-3 text-sm font-medium text-brand-600 group-hover:gap-2 transition-all">
                Start scanning
                <svg className="h-4 w-4" fill="none" stroke="currentColor" strokeWidth="2" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" d="M14 5l7 7m0 0l-7 7m7-7H3" />
                </svg>
              </span>
            </div>
            <div className="hidden sm:flex items-center justify-center w-14 h-14 bg-brand-50 rounded-lg flex-shrink-0">
              <svg className="h-7 w-7 text-brand-600" fill="none" stroke="currentColor" strokeWidth="1.5" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" d="M6.827 6.175A2.31 2.31 0 015.186 7.23c-.38.054-.757.112-1.134.174-1.083.18-1.858 1.125-1.858 2.222v9.374c0 1.096.775 2.041 1.858 2.222 1.814.302 3.665.526 5.548.67v-3.922a.75.75 0 011.5 0v3.922a49.095 49.095 0 005.548-.67c1.083-.18 1.858-1.126 1.858-2.222V9.453c0-1.097-.775-2.042-1.858-2.222a41.11 41.11 0 00-1.134-.174 2.31 2.31 0 01-1.64-1.055l-.822-1.316a2.192 2.192 0 00-1.736-1.039 48.774 48.774 0 00-5.232 0 2.192 2.192 0 00-1.736 1.039l-.821 1.316z" />
                <path strokeLinecap="round" strokeLinejoin="round" d="M16.5 12.75a4.5 4.5 0 11-9 0 4.5 4.5 0 019 0zM18.75 10.5h.008v.008h-.008V10.5z" />
              </svg>
            </div>
          </div>
        </div>
      </Link>

      {/* Secondary action — My Scans */}
      <Link to="/history" className="block group">
        <div className="bg-white border border-cream-300 rounded-lg p-6 hover:border-brand-400 transition-colors">
          <div className="flex items-start justify-between gap-4">
            <div className="flex-1">
              <h2 className="text-lg font-semibold text-earth-900 mb-1">
                My Scans
              </h2>
              <p className="text-sm text-earth-500 leading-relaxed">
                View your previous scans, check past results, and review advisory information
                for diseases you've already identified.
              </p>
              <span className="inline-flex items-center gap-1 mt-3 text-sm font-medium text-brand-600 group-hover:gap-2 transition-all">
                View history
                <svg className="h-4 w-4" fill="none" stroke="currentColor" strokeWidth="2" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" d="M14 5l7 7m0 0l-7 7m7-7H3" />
                </svg>
              </span>
            </div>
            <div className="hidden sm:flex items-center justify-center w-14 h-14 bg-cream-200 rounded-lg flex-shrink-0">
              <svg className="h-7 w-7 text-earth-500" fill="none" stroke="currentColor" strokeWidth="1.5" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" d="M12 6.042A8.967 8.967 0 006 3.75c-1.052 0-2.062.18-3 .512v14.25A8.987 8.987 0 016 18c2.305 0 4.408.867 6 2.292m0-14.25a8.966 8.966 0 016-2.292c1.052 0 2.062.18 3 .512v14.25A8.987 8.987 0 0018 18a8.967 8.967 0 00-6 2.292m0-14.25v14.25" />
              </svg>
            </div>
          </div>
        </div>
      </Link>

      {/* Helpful note */}
      <div className="mt-8 p-4 bg-harvest-400/5 border border-harvest-400/20 rounded-lg">
        <p className="text-sm text-earth-600 leading-relaxed">
          <strong className="text-earth-700">Note:</strong> KrishiDrishti is a decision-support tool.
          It can help you identify possible problems early, but it is not a replacement for expert advice.
          Always confirm the diagnosis with your local agricultural officer before applying any treatment.
        </p>
      </div>
    </div>
  )
}
