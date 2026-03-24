import { useState, useEffect } from 'react'
import { fetchAdminOverview, fetchNewsTrend, fetchSourceDistribution, fetchCategoryBreakdown } from '../utils/api'
import { BarChart, Bar, LineChart, Line, PieChart, Pie, Cell, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts'
import { TrendingUp, Users, Newspaper, Activity, Database, Clock, AlertTriangle, CheckCircle, Zap, Globe, Settings } from 'lucide-react'

const COLORS = ['#8b5cf6', '#3b82f6', '#10b981', '#f59e0b', '#ef4444', '#ec4899']

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
      <div className="min-h-screen bg-gray-50 flex items-center justify-center px-4">
        <div className="text-center">
          <div className="w-16 h-16 rounded-full bg-purple-100 flex items-center justify-center mx-auto mb-4">
            <Activity size={32} className="text-purple-600 animate-spin" />
          </div>
          <p className="text-gray-600 font-medium">Loading admin dashboard...</p>
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center px-4">
        <div className="max-w-md w-full bg-white rounded-xl border border-gray-200 shadow-sm p-6 text-center">
          <div className="w-12 h-12 rounded-full bg-red-100 flex items-center justify-center mx-auto mb-4">
            <AlertTriangle size={24} className="text-red-600" />
          </div>
          <h2 className="text-lg font-semibold text-gray-900 mb-2">Admin Dashboard Error</h2>
          <p className="text-gray-600 mb-4">{error}</p>
          <button
            onClick={loadStats}
            className="inline-flex items-center gap-2 px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 transition-colors duration-200 focus:outline-none focus:ring-2 focus:ring-purple-500 focus:ring-offset-2"
          >
            Try Again
          </button>
        </div>
      </div>
    )
  }

  if (!stats || !stats.overview) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center px-4">
        <div className="text-center">
          <div className="w-16 h-16 rounded-full bg-gray-100 flex items-center justify-center mx-auto mb-4">
            <Database size={32} className="text-gray-400" />
          </div>
          <p className="text-gray-600 font-medium">No data available</p>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white border-b border-gray-200 sticky top-0 z-30">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-lg bg-purple-600 flex items-center justify-center">
                <BarChart3 size={20} className="text-white" />
              </div>
              <div>
                <h1 className="text-2xl font-bold text-gray-900">Admin Dashboard</h1>
                <p className="text-sm text-gray-600">System analytics and performance monitoring</p>
              </div>
            </div>
            <div className="flex items-center gap-3">
              <select
                value={timeRange}
                onChange={(e) => setTimeRange(e.target.value)}
                className="px-4 py-2 bg-white border border-gray-300 rounded-lg text-gray-900 focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-purple-500"
              >
                <option value="24h">Last 24 Hours</option>
                <option value="7d">Last 7 Days</option>
                <option value="30d">Last 30 Days</option>
              </select>
              <button
                onClick={loadStats}
                className="inline-flex items-center gap-2 px-4 py-2 bg-white border border-gray-300 rounded-lg text-gray-700 hover:bg-gray-50 transition-colors duration-200 focus:outline-none focus:ring-2 focus:ring-purple-500 focus:ring-offset-2"
              >
                <RefreshCw size={18} />
                Refresh
              </button>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6 space-y-6">
        {/* Overview Cards */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-6 gap-4">
          <div className="bg-white rounded-xl border border-gray-200 shadow-sm p-4">
            <div className="flex items-center justify-between mb-3">
              <Newspaper className="text-blue-600" size={20} />
              <span className="text-xs font-medium text-gray-500">Total</span>
            </div>
            <div className="space-y-1">
              <div className="text-2xl font-bold text-gray-900">{(stats.overview.totalNews || 0).toLocaleString()}</div>
              <div className="text-xs text-gray-600">News Articles</div>
            </div>
          </div>

          <div className="bg-white rounded-xl border border-gray-200 shadow-sm p-4">
            <div className="flex items-center justify-between mb-3">
              <Star className="text-yellow-600" size={20} />
              <span className="text-xs font-medium text-gray-500">Total</span>
            </div>
            <div className="space-y-1">
              <div className="text-2xl font-bold text-gray-900">{(stats.overview.totalFavorites || 0).toLocaleString()}</div>
              <div className="text-xs text-gray-600">Favorites</div>
            </div>
          </div>

          <div className="bg-white rounded-xl border border-gray-200 shadow-sm p-4">
            <div className="flex items-center justify-between mb-3">
              <Settings className="text-purple-600" size={20} />
              <span className="text-xs font-medium text-gray-500">Active</span>
            </div>
            <div className="space-y-1">
              <div className="text-2xl font-bold text-gray-900">{(stats.overview.activeSources || 0).toLocaleString()}</div>
              <div className="text-xs text-gray-600">Sources</div>
            </div>
          </div>

          <div className="bg-white rounded-xl border border-gray-200 shadow-sm p-4">
            <div className="flex items-center justify-between mb-3">
              <Zap className="text-orange-600" size={20} />
              <span className="text-xs font-medium text-gray-500">Total</span>
            </div>
            <div className="space-y-1">
              <div className="text-2xl font-bold text-gray-900">{(stats.overview.totalBroadcasts || 0).toLocaleString()}</div>
              <div className="text-xs text-gray-600">Broadcasts</div>
            </div>
          </div>

          <div className="bg-white rounded-xl border border-gray-200 shadow-sm p-4">
            <div className="flex items-center justify-between mb-3">
              <Globe className="text-green-600" size={20} />
              <span className="text-xs font-medium text-gray-500">Recent</span>
            </div>
            <div className="space-y-1">
              <div className="text-2xl font-bold text-gray-900">{(stats.overview.recentNews || 0).toLocaleString()}</div>
              <div className="text-xs text-gray-600">Recent News</div>
            </div>
          </div>

          <div className="bg-white rounded-xl border border-gray-200 shadow-sm p-4">
            <div className="flex items-center justify-between mb-3">
              <CheckCircle className="text-emerald-600" size={20} />
              <span className="text-xs font-medium text-gray-500">Current</span>
            </div>
            <div className="space-y-1">
              <div className="text-2xl font-bold text-gray-900">{stats.overview.uptime || 'N/A'}</div>
              <div className="text-xs text-gray-600">Uptime</div>
            </div>
          </div>
        </div>

        {/* Charts Row */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* News Trend Chart */}
          <div className="bg-white rounded-xl border border-gray-200 shadow-sm p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">News Ingestion Trend</h3>
            <div className="h-80">
              <ResponsiveContainer width="100%" height="100%">
                <LineChart data={stats.newsTrend || []}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
                  <XAxis dataKey="date" stroke="#6b7280" />
                  <YAxis stroke="#6b7280" />
                  <Tooltip 
                    contentStyle={{ backgroundColor: '#ffffff', border: '1px solid #e5e7eb', borderRadius: '8px' }}
                    labelStyle={{ color: '#111827', fontWeight: 'bold' }}
                  />
                  <Line type="monotone" dataKey="articles" stroke="#8b5cf6" strokeWidth={2} name="Articles" />
                  <Line type="monotone" dataKey="duplicates" stroke="#ef4444" strokeWidth={2} name="Duplicates" />
                </LineChart>
              </ResponsiveContainer>
            </div>
          </div>

          {/* Source Distribution */}
          <div className="bg-white rounded-xl border border-gray-200 shadow-sm p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Source Distribution</h3>
            <div className="h-80">
              <ResponsiveContainer width="100%" height="100%">
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
          </div>
        </div>

        {/* Category Breakdown */}
        <div className="bg-white rounded-xl border border-gray-200 shadow-sm p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Category Performance</h3>
          <div className="h-80">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={stats.categoryBreakdown || []}>
                <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
                <XAxis dataKey="category" stroke="#6b7280" />
                <YAxis stroke="#6b7280" />
                <Tooltip 
                  contentStyle={{ backgroundColor: '#ffffff', border: '1px solid #e5e7eb', borderRadius: '8px' }}
                  labelStyle={{ color: '#111827', fontWeight: 'bold' }}
                />
                <Bar dataKey="count" fill="#8b5cf6" name="Articles" />
                <Bar dataKey="impact" fill="#10b981" name="Avg Impact" />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
      </main>
    </div>
  )
}
