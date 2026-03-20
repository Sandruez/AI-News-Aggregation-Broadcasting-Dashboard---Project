import { useState, useEffect, useCallback } from 'react'
import { fetchFavorites, removeFavorite } from '../utils/api'

export function useFavorites() {
  const [favorites, setFavorites] = useState([])
  const [loading, setLoading] = useState(true)

  const load = useCallback(async () => {
    setLoading(true)
    try {
      const data = await fetchFavorites()
      setFavorites(data)
    } catch (e) {
      console.error(e)
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
