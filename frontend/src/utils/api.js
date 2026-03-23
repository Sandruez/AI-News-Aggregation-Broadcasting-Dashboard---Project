import axios from 'axios'

// Production-ready API configuration with fallback
// Note: VITE_API_URL should NOT include /api suffix
const apiUrl = import.meta.env.VITE_API_URL

if (!apiUrl) {
  console.error('VITE_API_URL is not defined! Set it in Railway dashboard.')
}

const api = axios.create({
  baseURL: apiUrl, // Fallback to relative path if env var not set
  timeout: 15000,
})

// All endpoints already start with /api/...
// Feed
export const fetchFeed = () => api.get('/feed').then(r => r.data)

// News
export const fetchNews = (params) => api.get('/api/news', { params }).then(r => r.data)
export const refreshNews = () => api.post('/api/news/refresh').then(r => r.data)
export const fetchNewsItem = (id) => api.get(`/api/news/${id}`).then(r => r.data)

// Favorites
export const fetchFavorites = () => api.get('/api/favorites').then(r => r.data)
export const addFavorite = (newsItemId) => api.post(`/api/favorites/${newsItemId}`).then(r => r.data)
export const removeFavorite = (newsItemId) => api.delete(`/api/favorites/${newsItemId}`).then(r => r.data)

// Broadcast
export const broadcast = (payload) => api.post('/api/broadcast', payload).then(r => r.data)

// Sources
export const fetchSources = () => api.get('/api/sources').then(r => r.data)
export const toggleSource = (id) => api.patch(`/api/sources/${id}/toggle`).then(r => r.data)

// Admin
export const fetchAdminOverview = () => api.get('/api/admin/overview').then(r => r.data)
export const fetchNewsTrend = (days = 7) => api.get('/api/admin/news-trend', { params: { days } }).then(r => r.data)
export const fetchSourceDistribution = () => api.get('/api/admin/source-distribution').then(r => r.data)
export const fetchCategoryBreakdown = () => api.get('/api/admin/category-breakdown').then(r => r.data)
export const fetchBroadcastAnalytics = () => api.get('/api/admin/broadcast-analytics').then(r => r.data)
export const fetchSystemHealth = () => api.get('/api/admin/system-health').then(r => r.data)
export const fetchRecentActivity = () => api.get('/api/admin/recent-activity').then(r => r.data)

export default api
