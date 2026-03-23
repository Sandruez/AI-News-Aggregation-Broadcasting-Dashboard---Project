import { useState, useEffect, useCallback } from 'react'
import { fetchNews, refreshNews, addFavorite, removeFavorite } from '../utils/api'

export function useNews() {
  const [items, setItems] = useState([])
  const [total, setTotal] = useState(0)
  const [loading, setLoading] = useState(true)
  const [refreshing, setRefreshing] = useState(false)
  const [error, setError] = useState(null)

  const [params, setParams] = useState({
    page: 1,
    page_size: 30,
    sort_by: 'date',
    q: '',
    source_id: null,
    category: null,
  })

  const load = useCallback(async () => {
    setLoading(true)
    setError(null)
    try {
      const clean = Object.fromEntries(Object.entries(params).filter(([, v]) => v != null && v !== ''))
      const data = await fetchNews(clean)
      setItems(data.items || [])
      setTotal(data.total || 0)
    } catch (e) {
      console.error('Failed to load news:', e)
      setError(e.message || 'Failed to load news')
      // Set empty state to prevent crashes
      setItems([])
      setTotal(0)
    } finally {
      setLoading(false)
    }
  }, [params])

  useEffect(() => { load() }, [load])

  const refresh = async () => {
    setRefreshing(true)
    try {
      await refreshNews()
      await load()
    } finally {
      setRefreshing(false)
    }
  }

  const toggleFavorite = async (item) => {
    try {
      if (item.is_favorited) {
        await removeFavorite(item.id)
      } else {
        await addFavorite(item.id)
      }
      setItems(prev =>
        prev.map(i => i.id === item.id ? { ...i, is_favorited: !i.is_favorited } : i)
      )
    } catch (e) {
      console.error('Favorite toggle failed', e)
    }
  }

  return { items, total, loading, refreshing, error, params, setParams, refresh, toggleFavorite }
}
