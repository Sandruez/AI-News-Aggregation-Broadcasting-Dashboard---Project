import { useState, useCallback } from 'react'
import { useNews } from '../hooks/useNews'
import { SearchBar } from '../components/SearchBar_new'
import { NewsCard } from '../components/NewsCard_new'
import { TrendingUp, RefreshCw, AlertCircle } from 'lucide-react'

export default function FeedPage() {
  const { items, total, loading, refreshing, error, params, setParams, refreshNews, toggleFavorite } = useNews()

  const handleRefresh = useCallback(() => {
    refreshNews()
  }, [refreshNews])

  const handleToggleFavorite = useCallback(async (item) => {
    await toggleFavorite(item)
  }, [toggleFavorite])

  const handleBroadcast = useCallback((item) => {
    // TODO: Implement broadcast functionality
    console.log('Broadcast:', item)
  }, [])

  if (error) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center px-4">
        <div className="max-w-md w-full bg-white rounded-xl border border-gray-200 shadow-sm p-6 text-center">
          <div className="w-12 h-12 rounded-full bg-red-100 flex items-center justify-center mx-auto mb-4">
            <AlertCircle size={24} className="text-red-600" />
          </div>
          <h2 className="text-lg font-semibold text-gray-900 mb-2">Something went wrong</h2>
          <p className="text-gray-600 mb-4">{error}</p>
          <button
            onClick={handleRefresh}
            className="inline-flex items-center gap-2 px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 transition-colors duration-200 focus:outline-none focus:ring-2 focus:ring-purple-500 focus:ring-offset-2"
          >
            <RefreshCw size={16} />
            Try Again
          </button>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white border-b border-gray-200 sticky top-0 z-30">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-lg bg-purple-600 flex items-center justify-center">
                <TrendingUp size={20} className="text-white" />
              </div>
              <div>
                <h1 className="text-2xl font-bold text-gray-900">AI News Feed</h1>
                <p className="text-sm text-gray-600">Latest AI industry updates and insights</p>
              </div>
            </div>
            <button
              onClick={handleRefresh}
              disabled={refreshing}
              className="inline-flex items-center gap-2 px-4 py-2 bg-white border border-gray-300 rounded-lg text-gray-700 hover:bg-gray-50 transition-colors duration-200 focus:outline-none focus:ring-2 focus:ring-purple-500 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              <RefreshCw size={18} className={refreshing ? 'animate-spin' : ''} />
              <span className="hidden sm:inline">Refresh</span>
            </button>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
        {/* Search and Filters */}
        <div className="mb-6">
          <SearchBar
            params={params}
            setParams={setParams}
            onRefresh={handleRefresh}
            refreshing={refreshing}
            total={total}
          />
        </div>

        {/* Loading State */}
        {loading && items.length === 0 && (
          <div className="flex flex-col items-center justify-center py-12">
            <div className="w-12 h-12 rounded-full bg-purple-100 flex items-center justify-center mb-4">
              <RefreshCw size={24} className="text-purple-600 animate-spin" />
            </div>
            <p className="text-gray-600 font-medium">Loading news...</p>
          </div>
        )}

        {/* News Grid */}
        <div className="space-y-4">
          {items.length > 0 ? (
            items.map((item) => (
              <NewsCard
                key={item.id}
                item={item}
                onToggleFavorite={handleToggleFavorite}
                onBroadcast={handleBroadcast}
              />
            ))
          ) : !loading ? (
            <div className="text-center py-12">
              <div className="w-16 h-16 rounded-full bg-gray-100 flex items-center justify-center mx-auto mb-4">
                <TrendingUp size={32} className="text-gray-400" />
              </div>
              <h3 className="text-lg font-semibold text-gray-900 mb-2">No articles found</h3>
              <p className="text-gray-600 mb-4">
                {params.q ? `No results for "${params.q}"` : 'No articles available at the moment.'}
              </p>
              {params.q && (
                <button
                  onClick={() => setParams({ ...params, q: null })}
                  className="inline-flex items-center gap-2 px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 transition-colors duration-200 focus:outline-none focus:ring-2 focus:ring-purple-500 focus:ring-offset-2"
                >
                  Clear search
                </button>
              )}
            </div>
          ) : null}
        </div>

        {/* Load More */}
        {items.length > 0 && !loading && (
          <div className="mt-8 text-center">
            <button
              onClick={() => setParams({ ...params, page: (params.page || 1) + 1 })}
              className="inline-flex items-center gap-2 px-6 py-3 bg-white border border-gray-300 rounded-lg text-gray-700 hover:bg-gray-50 transition-colors duration-200 focus:outline-none focus:ring-2 focus:ring-purple-500 focus:ring-offset-2"
            >
              Load More Articles
            </button>
          </div>
        )}
      </main>
    </div>
  )
}
