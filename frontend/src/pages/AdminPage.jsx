import { useState, useEffect } from 'react'
import { fetchAdminOverview, fetchNewsTrend, fetchSourceDistribution, fetchCategoryBreakdown } from '../utils/api'
import { BarChart, Bar, LineChart, Line, PieChart, Pie, Cell, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts'
import { TrendingUp, Users, Newspaper, Activity, Database, Clock, AlertTriangle, CheckCircle, Zap, Globe, BarChart3, RefreshCw, Star, Settings } from 'lucide-react'

const COLORS = ['#3B82F6', '#10B981', '#F59E0B', '#EF4444', '#8B5CF6', '#EC4899']

export default function AdminPage() {
  const [stats, setStats] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [timeRange, setTimeRange] = useState('7d')

  useEffect(() => {
    loadStats()
  }, [timeRange])

  const loadStats = async () => {
    setLoading(true)
    setError(null)
    try {
      console.log('Fetching admin stats...')
      const [overview, newsTrend, sourceDist, categories] = await Promise.all([
        fetchAdminOverview(),
        fetchNewsTrend(timeRange === '24h' ? 1 : timeRange === '7d' ? 7 : 30),
        fetchSourceDistribution(),
        fetchCategoryBreakdown()
      ])

      console.log('Admin API responses:', { overview, newsTrend, sourceDist, categories })

      setStats({
        overview,
        newsTrend: newsTrend?.trend || newsTrend || [],
        sourceDistribution: (sourceDist?.distribution || sourceDist || []).map((item, index) => ({
          ...item,
          color: COLORS[index % COLORS.length]
        })),
        categoryBreakdown: categories?.categories || categories || []
      })
    } catch (error) {
      console.error('Failed to fetch admin stats:', error)
      setError(error.message || 'Failed to fetch admin stats')
      // Set empty state as fallback
      setStats({
        overview: { totalNews: 0, totalFavorites: 0, totalBroadcasts: 0, activeSources: 0, recentNews: 0, uptime: "N/A" },
        newsTrend: [],
        sourceDistribution: [],
        categoryBreakdown: []
      })
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
    <div className="max-w-7xl mx-auto px-6 py-8 space-y-8">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="font-display font-800 text-2xl text-white tracking-tight">Admin Dashboard</h1>
          <p className="text-sm text-ink-400 mt-1 font-body">
            System analytics and performance monitoring
          </p>
        </div>
        <div className="flex items-center gap-3">
          <select
            value={timeRange}
            onChange={(e) => setTimeRange(e.target.value)}
            className="bg-ink-800 border border-ink-600 rounded-lg px-3 py-2 text-sm text-white"
          >
            <option value="24h">Last 24 Hours</option>
            <option value="7d">Last 7 Days</option>
            <option value="30d">Last 30 Days</option>
          </select>
        </div>
      </div>

      {/* Overview Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-6 gap-4">
        <div className="bg-ink-800 border border-ink-600 rounded-xl p-4">
          <div className="flex items-center justify-between">
            <Newspaper className="text-blue-400" size={20} />
            <span className="text-xs text-ink-400">Total</span>
          </div>
          <div className="mt-2">
            <div className="text-2xl font-bold text-white">{(stats.overview.totalNews || 0).toLocaleString()}</div>
            <div className="text-xs text-ink-400">News Articles</div>
          </div>
        </div>

        <div className="bg-ink-800 border border-ink-600 rounded-xl p-4">
          <div className="flex items-center justify-between">
            <Users className="text-green-400" size={20} />
            <span className="text-xs text-ink-400">Total</span>
          </div>
          <div className="mt-2">
            <div className="text-2xl font-bold text-white">{(stats.overview.totalFavorites || 0).toLocaleString()}</div>
            <div className="text-xs text-ink-400">Favorites</div>
          </div>
        </div>

        <div className="bg-ink-800 border border-ink-600 rounded-xl p-4">
          <div className="flex items-center justify-between">
            <Settings className="text-purple-400" size={20} />
            <span className="text-xs text-ink-400">Active</span>
          </div>
          <div className="mt-2">
            <div className="text-2xl font-bold text-white">{(stats.overview.activeSources || 0).toLocaleString()}</div>
            <div className="text-xs text-ink-400">Sources</div>
          </div>
        </div>

        <div className="bg-ink-800 border border-ink-600 rounded-xl p-4">
          <div className="flex items-center justify-between">
            <Zap className="text-yellow-400" size={20} />
            <span className="text-xs text-ink-400">Total</span>
          </div>
          <div className="mt-2">
            <div className="text-2xl font-bold text-white">{(stats.overview.totalBroadcasts || 0).toLocaleString()}</div>
            <div className="text-xs text-ink-400">Broadcasts</div>
          </div>
        </div>

        <div className="bg-ink-800 border border-ink-600 rounded-xl p-4">
          <div className="flex items-center justify-between">
            <Globe className="text-purple-400" size={20} />
            <span className="text-xs text-ink-400">Active</span>
          </div>
          <div className="mt-2">
            <div className="text-2xl font-bold text-white">{(stats.overview.activeSources || 0).toLocaleString()}</div>
            <div className="text-xs text-ink-400">Sources</div>
          </div>
        </div>

        <div className="bg-ink-800 border border-ink-600 rounded-xl p-4">
          <div className="flex items-center justify-between">
            <Users className="text-pink-400" size={20} />
            <span className="text-xs text-ink-400">Recent</span>
          </div>
          <div className="mt-2">
            <div className="text-2xl font-bold text-white">{(stats.overview.recentNews || 0).toLocaleString()}</div>
            <div className="text-xs text-ink-400">Recent News</div>
          </div>
        </div>

        <div className="bg-ink-800 border border-ink-600 rounded-xl p-4">
          <div className="flex items-center justify-between">
            <CheckCircle className="text-emerald-400" size={20} />
            <span className="text-xs text-ink-400">Current</span>
          </div>
          <div className="mt-2">
            <div className="text-2xl font-bold text-white">{stats.overview.uptime || 'N/A'}</div>
            <div className="text-xs text-ink-400">Uptime</div>
          </div>
        </div>
      </div>

      {/* Charts Row */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* News Trend Chart */}
        <div className="bg-ink-800 border border-ink-600 rounded-xl p-6">
          <h3 className="font-semibold text-white mb-4">News Ingestion Trend</h3>
          <ResponsiveContainer width="100%" height={300}>
            <LineChart data={stats.newsTrend || []}>
              <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
              <XAxis dataKey="date" stroke="#9CA3AF" />
              <YAxis stroke="#9CA3AF" />
              <Tooltip 
                contentStyle={{ backgroundColor: '#1F2937', border: '1px solid #374151' }}
                labelStyle={{ color: '#9CA3AF' }}
              />
              <Line type="monotone" dataKey="articles" stroke="#3B82F6" strokeWidth={2} name="Articles" />
              <Line type="monotone" dataKey="duplicates" stroke="#EF4444" strokeWidth={2} name="Duplicates" />
            </LineChart>
          </ResponsiveContainer>
        </div>

        {/* Source Distribution */}
        <div className="bg-ink-800 border border-ink-600 rounded-xl p-6">
          <h3 className="font-semibold text-white mb-4">Source Distribution</h3>
          <ResponsiveContainer width="100%" height={300}>
            <PieChart>
              <Pie
                data={stats.sourceDistribution || []}
                cx="50%"
                cy="50%"
                outerRadius={100}
                fill="#8884d8"
                dataKey="count"
                label={({ source, percent }) => `${source} ${(percent * 100).toFixed(0)}%`}
              >
                {(stats.sourceDistribution || []).map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={entry.color} />
                ))}
              </Pie>
              <Tooltip />
            </PieChart>
          </ResponsiveContainer>
        </div>

        {/* Category Breakdown */}
        <div className="bg-ink-800 border border-ink-600 rounded-xl p-6">
          <h3 className="font-semibold text-white mb-4">Category Performance</h3>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={stats.categoryBreakdown || []}>
              <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
              <XAxis dataKey="category" stroke="#9CA3AF" />
              <YAxis stroke="#9CA3AF" />
              <Tooltip 
                contentStyle={{ backgroundColor: '#1F2937', border: '1px solid #374151' }}
                labelStyle={{ color: '#9CA3AF' }}
              />
              <Bar dataKey="count" fill="#3B82F6" name="Articles" />
              <Bar dataKey="impact" fill="#10B981" name="Avg Impact" />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>
    </div>
  )
}
