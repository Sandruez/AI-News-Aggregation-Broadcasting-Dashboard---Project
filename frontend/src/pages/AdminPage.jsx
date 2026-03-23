import { useState, useEffect } from 'react'
import { fetchAdminOverview } from '../utils/api'

export default function AdminPage() {
  const [stats, setStats] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  useEffect(() => {
    loadStats()
  }, [])

  const loadStats = async () => {
    setLoading(true)
    setError(null)
    try {
      console.log('Fetching admin overview...')
      const overview = await fetchAdminOverview()
      console.log('Overview response:', overview)
      setStats(overview)
    } catch (error) {
      console.error('Failed to fetch admin overview:', error)
      setError(error.message || 'Failed to fetch admin stats')
    } finally {
      setLoading(false)
    }
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center py-20 text-ink-500">
        <div>Loading admin dashboard...</div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="flex flex-col items-center justify-center py-20 text-ink-500">
        <div className="text-red-400 mb-4">Admin Dashboard Error</div>
        <div className="text-sm mb-4">{error}</div>
        <button onClick={loadStats}>Try Again</button>
        <button onClick={() => console.log('Current stats:', stats)}>Debug Stats</button>
      </div>
    )
  }

  if (!stats) {
    return (
      <div className="flex items-center justify-center py-20 text-ink-500">
        <div>No stats available</div>
      </div>
    )
  }

  return (
    <div className="max-w-7xl mx-auto px-6 py-8">
      <h1 className="font-display font-800 text-2xl text-white tracking-tight mb-6">Admin Dashboard</h1>
      
      <div className="bg-ink-800 border border-ink-600 rounded-xl p-6 mb-6">
        <h2 className="font-semibold text-white mb-4">Overview</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          <div className="bg-ink-700 rounded-lg p-4">
            <div className="text-2xl font-bold text-white">{stats.totalNews || 0}</div>
            <div className="text-xs text-ink-400">Total News</div>
          </div>
          <div className="bg-ink-700 rounded-lg p-4">
            <div className="text-2xl font-bold text-white">{stats.totalFavorites || 0}</div>
            <div className="text-xs text-ink-400">Total Favorites</div>
          </div>
          <div className="bg-ink-700 rounded-lg p-4">
            <div className="text-2xl font-bold text-white">{stats.totalSources || 0}</div>
            <div className="text-xs text-ink-400">Total Sources</div>
          </div>
          <div className="bg-ink-700 rounded-lg p-4">
            <div className="text-2xl font-bold text-white">{stats.activeSources || 0}</div>
            <div className="text-xs text-ink-400">Active Sources</div>
          </div>
        </div>
      </div>

      <div className="bg-ink-800 border border-ink-600 rounded-xl p-6">
        <h2 className="font-semibold text-white mb-4">Debug Info</h2>
        <pre className="text-xs text-ink-300 bg-ink-900 p-4 rounded overflow-auto">
          {JSON.stringify(stats, null, 2)}
        </pre>
      </div>
    </div>
  )
}
