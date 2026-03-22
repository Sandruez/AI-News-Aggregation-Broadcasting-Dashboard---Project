import axios from 'axios'

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || '/api',
  timeout: 15000,
})

// News
export const fetchNews = (params) => api.get('/news', { params }).then(r => r.data)
export const refreshNews = () => api.post('/news/refresh').then(r => r.data)
export const fetchNewsItem = (id) => api.get(`/news/${id}`).then(r => r.data)

// Favorites
export const fetchFavorites = () => api.get('/favorites').then(r => r.data)
export const addFavorite = (newsItemId) => api.post(`/favorites/${newsItemId}`).then(r => r.data)
export const removeFavorite = (newsItemId) => api.delete(`/favorites/${newsItemId}`).then(r => r.data)

// Broadcast
export const broadcast = (payload) => api.post('/broadcast', payload).then(r => r.data)

// Sources
export const fetchSources = () => api.get('/sources').then(r => r.data)
export const toggleSource = (id) => api.patch(`/sources/${id}/toggle`).then(r => r.data)

// Admin
export const fetchAdminOverview = () => api.get('/admin/overview').then(r => r.data)
export const fetchNewsTrend = (days = 7) => api.get('/admin/news-trend', { params: { days } }).then(r => r.data)
export const fetchSourceDistribution = () => api.get('/admin/source-distribution').then(r => r.data)
export const fetchCategoryBreakdown = () => api.get('/admin/category-breakdown').then(r => r.data)
export const fetchBroadcastAnalytics = () => api.get('/admin/broadcast-analytics').then(r => r.data)
export const fetchSystemHealth = () => api.get('/admin/system-health').then(r => r.data)
export const fetchRecentActivity = () => api.get('/admin/recent-activity').then(r => r.data)

export default api
