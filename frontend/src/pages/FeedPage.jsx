import { useState } from 'react'
import { useNews } from '../hooks/useNews'
import NewsCard from '../components/NewsCard'
import SearchBar from '../components/SearchBar'
import BroadcastModal from '../components/BroadcastModal'
import { Loader2, AlertTriangle, Inbox } from 'lucide-react'

export default function FeedPage() {
  const { items, total, loading, refreshing, error, params, setParams, refresh, toggleFavorite } = useNews()
  const [broadcastTarget, setBroadcastTarget] = useState(null)

  return (
    <div className="max-w-4xl mx-auto px-6 py-8">
      {/* Page header */}
      <div className="mb-6">
        <h1 className="font-display font-800 text-2xl text-white tracking-tight">AI News Feed</h1>
        <p className="text-sm text-ink-400 mt-1 font-body">
          Aggregating from 20+ sources, deduplicated and scored by Groq.
        </p>
      </div>

      {/* Search & filters */}
      <div className="mb-6">
        <SearchBar
          params={params}
          setParams={setParams}
          onRefresh={refresh}
          refreshing={refreshing}
          total={total}
        />
      </div>

      {/* States */}
      {error && (
        <div className="flex items-center gap-3 p-4 bg-red-500/10 border border-red-500/30 rounded-xl text-red-400 text-sm mb-6">
          <AlertTriangle size={16} />
          {error}
        </div>
      )}

      {loading && (
        <div className="flex items-center justify-center py-20 text-ink-500">
          <Loader2 size={24} className="animate-spin mr-3" />
          <span className="font-body text-sm">Loading stories…</span>
        </div>
      )}

      {!loading && items.length === 0 && (
        <div className="flex flex-col items-center py-20 text-ink-500 gap-3">
          <Inbox size={32} />
          <p className="font-body text-sm">No stories yet. Hit Refresh to fetch from all sources.</p>
        </div>
      )}

      {/* News grid */}
      {!loading && items.length > 0 && (
        <div className="grid gap-3">
          {items.map((item, i) => (
            <div key={item.id} style={{ animationDelay: `${i * 20}ms` }}>
              <NewsCard
                item={item}
                onToggleFavorite={toggleFavorite}
                onBroadcast={(item) => setBroadcastTarget(item)}
              />
            </div>
          ))}
        </div>
      )}

      {/* Pagination */}
      {!loading && total > params.page_size && (
        <div className="flex items-center justify-center gap-4 mt-8">
          <button
            disabled={params.page <= 1}
            onClick={() => setParams(p => ({ ...p, page: p.page - 1 }))}
            className="btn-ghost disabled:opacity-40"
          >
            ← Previous
          </button>
          <span className="text-xs text-ink-500 font-mono">
            Page {params.page} of {Math.ceil(total / params.page_size)}
          </span>
          <button
            disabled={params.page >= Math.ceil(total / params.page_size)}
            onClick={() => setParams(p => ({ ...p, page: p.page + 1 }))}
            className="btn-ghost disabled:opacity-40"
          >
            Next →
          </button>
        </div>
      )}

      {/* Broadcast Modal */}
      {broadcastTarget && (
        <BroadcastModal
          favoriteId={broadcastTarget.favorites?.[0]?.id || broadcastTarget.id}
          newsItem={broadcastTarget}
          onClose={() => setBroadcastTarget(null)}
        />
      )}
    </div>
  )
}
