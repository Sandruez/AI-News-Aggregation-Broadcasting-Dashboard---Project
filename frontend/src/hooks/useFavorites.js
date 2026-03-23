import { useState, useEffect, useCallback } from 'react'
import { fetchFavorites, removeFavorite } from '../utils/api'

export function useFavorites() {
  const [favorites, setFavorites] = useState([])
  const [loading, setLoading] = useState(true)

  const load = useCallback(async () => {
    setLoading(true)
    try {
      const data = await fetchFavorites()
      // Handle both wrapped and unwrapped response
      const items = data?.items || data || []
      setFavorites(items)
    } catch (e) {
      console.error('Failed to load favorites:', e)
      setFavorites([]) // Set empty array on error
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => { load() }, [load])

  const remove = async (newsItemId) => {
    await removeFavorite(newsItemId)
    setFavorites(prev => prev.filter(f => f.news_item_id !== newsItemId))
  }

  return { favorites, loading, remove, reload: load }
}
