import { useState, useEffect } from 'react'
import { BarChart, Bar, LineChart, Line, PieChart, Pie, Cell, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts'
import { TrendingUp, Users, Newspaper, Activity, Database, Clock, AlertTriangle, CheckCircle, Zap, Globe } from 'lucide-react'
import {
  fetchAdminOverview,
  fetchNewsTrend,
  fetchSourceDistribution,
  fetchCategoryBreakdown,
  fetchBroadcastAnalytics,
  fetchSystemHealth,
  fetchRecentActivity
} from '../utils/api'

const COLORS = ['#3B82F6', '#10B981', '#F59E0B', '#EF4444', '#8B5CF6', '#EC4899']

export default function AdminPage() {
  const [stats, setStats] = useState(null)
  const [loading, setLoading] = useState(true)
  const [timeRange, setTimeRange] = useState('7d')

  useEffect(() => {
    fetchAdminStats()
  }, [timeRange])

  const fetchAdminStats = async () => {
    setLoading(true)
    try {
      const [overview, newsTrend, sourceDist, categories, broadcasts, health, activity] = await Promise.all([
        fetchAdminOverview(),
        fetchNewsTrend(timeRange === '24h' ? 1 : timeRange === '7d' ? 7 : 30),
        fetchSourceDistribution(),
        fetchCategoryBreakdown(),
        fetchBroadcastAnalytics(),
        fetchSystemHealth(),
        fetchRecentActivity()
      ])

      setStats({
        overview,
        newsTrend,
        sourceDistribution: sourceDist.map((item, index) => ({
          ...item,
          color: COLORS[index % COLORS.length]
        })),
        categoryBreakdown: categories,
        broadcastAnalytics: broadcasts,
        systemHealth: health,
        recentActivity: activity
      })
    } catch (error) {
      console.error('Failed to fetch admin stats:', error)
      // Set mock data as fallback
      setStats({
        overview: { totalNews: 0, totalFavorites: 0, totalBroadcasts: 0, activeSources: 0, recentNews: 0, uptime: "N/A" },
        newsTrend: [],
        sourceDistribution: [],
        categoryBreakdown: [],
        broadcastAnalytics: [],
        systemHealth: {},
        recentActivity: []
      })
    } finally {
      setLoading(false)
    }
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center py-20 text-ink-500">
        <Activity className="animate-spin mr-3" size={24} />
        <span className="font-body text-sm">Loading admin dashboard…</span>
      </div>
    )
  }

  if (!stats) return null

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
            <div className="text-2xl font-bold text-white">{stats.overview.totalNews.toLocaleString()}</div>
            <div className="text-xs text-ink-400">News Articles</div>
          </div>
        </div>

        <div className="bg-ink-800 border border-ink-600 rounded-xl p-4">
          <div className="flex items-center justify-between">
            <Users className="text-green-400" size={20} />
            <span className="text-xs text-ink-400">Total</span>
          </div>
          <div className="mt-2">
            <div className="text-2xl font-bold text-white">{stats.overview.totalFavorites}</div>
            <div className="text-xs text-ink-400">Favorites</div>
          </div>
        </div>

        <div className="bg-ink-800 border border-ink-600 rounded-xl p-4">
          <div className="flex items-center justify-between">
            <Zap className="text-yellow-400" size={20} />
            <span className="text-xs text-ink-400">Total</span>
          </div>
          <div className="mt-2">
            <div className="text-2xl font-bold text-white">{stats.overview.totalBroadcasts}</div>
            <div className="text-xs text-ink-400">Broadcasts</div>
          </div>
        </div>

        <div className="bg-ink-800 border border-ink-600 rounded-xl p-4">
          <div className="flex items-center justify-between">
            <Globe className="text-purple-400" size={20} />
            <span className="text-xs text-ink-400">Active</span>
          </div>
          <div className="mt-2">
            <div className="text-2xl font-bold text-white">{stats.overview.activeSources}</div>
            <div className="text-xs text-ink-400">Sources</div>
          </div>
        </div>

        <div className="bg-ink-800 border border-ink-600 rounded-xl p-4">
          <div className="flex items-center justify-between">
            <Users className="text-pink-400" size={20} />
            <span className="text-xs text-ink-400">Recent</span>
          </div>
          <div className="mt-2">
            <div className="text-2xl font-bold text-white">{stats.overview.recentNews}</div>
            <div className="text-xs text-ink-400">Recent News</div>
          </div>
        </div>

        <div className="bg-ink-800 border border-ink-600 rounded-xl p-4">
          <div className="flex items-center justify-between">
            <CheckCircle className="text-emerald-400" size={20} />
            <span className="text-xs text-ink-400">Current</span>
          </div>
          <div className="mt-2">
            <div className="text-2xl font-bold text-white">{stats.overview.uptime}</div>
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
            <LineChart data={stats.newsTrend}>
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
                data={stats.sourceDistribution}
                cx="50%"
                cy="50%"
                outerRadius={100}
                fill="#8884d8"
                dataKey="value"
                label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
              >
                {stats.sourceDistribution.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={entry.color} />
                ))}
              </Pie>
              <Tooltip />
            </PieChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Category Breakdown */}
      <div className="bg-ink-800 border border-ink-600 rounded-xl p-6">
        <h3 className="font-semibold text-white mb-4">Category Performance</h3>
        <ResponsiveContainer width="100%" height={300}>
          <BarChart data={stats.categoryBreakdown}>
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

      {/* Broadcast Analytics & System Health */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Broadcast Analytics */}
        <div className="bg-ink-800 border border-ink-600 rounded-xl p-6">
          <h3 className="font-semibold text-white mb-4">Broadcast Analytics</h3>
          <div className="space-y-3">
            {stats.broadcastAnalytics.map((platform) => (
              <div key={platform.platform} className="flex items-center justify-between p-3 bg-ink-700 rounded-lg">
                <div className="flex items-center gap-3">
                  <div className="w-2 h-2 bg-green-400 rounded-full"></div>
                  <span className="text-white font-medium">{platform.platform}</span>
                </div>
                <div className="flex items-center gap-4 text-sm">
                  <span className="text-ink-300">{platform.sent} sent</span>
                  <span className="text-green-400">{platform.success} success</span>
                  {platform.failed > 0 && (
                    <span className="text-red-400">{platform.failed} failed</span>
                  )}
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* System Health */}
        <div className="bg-ink-800 border border-ink-600 rounded-xl p-6">
          <h3 className="font-semibold text-white mb-4">System Health</h3>
          <div className="space-y-3">
            {Object.entries(stats.systemHealth).map(([service, health]) => (
              <div key={service} className="flex items-center justify-between p-3 bg-ink-700 rounded-lg">
                <div className="flex items-center gap-3">
                  <div className={`w-2 h-2 rounded-full ${
                    health.status === 'healthy' ? 'bg-green-400' : 
                    health.status === 'running' ? 'bg-blue-400' : 'bg-red-400'
                  }`}></div>
                  <span className="text-white font-medium capitalize">{service}</span>
                </div>
                <div className="text-sm text-ink-300">
                  {health.responseTime && `${health.responseTime} • `}
                  {health.connections && `${health.connections} connections • `}
                  {health.requests && `${health.requests} requests • `}
                  {health.lastRun && `Last: ${health.lastRun} • `}
                  {health.tokens && `${health.tokens.toLocaleString()} tokens`}
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Recent Activity */}
      <div className="bg-ink-800 border border-ink-600 rounded-xl p-6">
        <h3 className="font-semibold text-white mb-4">Recent Activity</h3>
        <div className="space-y-2">
          {stats.recentActivity.map((activity, index) => (
            <div key={index} className="flex items-center justify-between p-3 bg-ink-700 rounded-lg">
              <div className="flex items-center gap-3">
                {activity.status === 'success' && <CheckCircle className="text-green-400" size={16} />}
                {activity.status === 'warning' && <AlertTriangle className="text-yellow-400" size={16} />}
                {activity.status === 'error' && <AlertTriangle className="text-red-400" size={16} />}
                <span className="text-white text-sm">{activity.message}</span>
              </div>
              <span className="text-ink-400 text-xs">{activity.time}</span>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}
