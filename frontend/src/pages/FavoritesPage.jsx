import { useState } from 'react'
import { useFavorites } from '../hooks/useFavorites'
import BroadcastModal from '../components/BroadcastModal'
import { formatDistanceToNow } from 'date-fns'
import { Star, ExternalLink, Trash2, Send, Loader2, Inbox } from 'lucide-react'
import clsx from 'clsx'

const PLATFORM_ICONS = {
  email: '✉️', linkedin: '💼', whatsapp: '💬', blog: '📝', newsletter: '📰'
}

export default function FavoritesPage() {
  const { favorites, loading, remove } = useFavorites()
  const [broadcastTarget, setBroadcastTarget] = useState(null)

  return (
    <div className="max-w-4xl mx-auto px-6 py-8">
      <div className="mb-6">
        <h1 className="font-display font-800 text-2xl text-white tracking-tight">Favorites</h1>
        <p className="text-sm text-ink-400 mt-1 font-body">
          Saved stories ready to broadcast across platforms.
        </p>
      </div>

      {loading && (
        <div className="flex items-center justify-center py-20 text-ink-500">
          <Loader2 size={24} className="animate-spin mr-3" />
          <span className="text-sm font-body">Loading favorites…</span>
        </div>
      )}

      {!loading && favorites.length === 0 && (
        <div className="flex flex-col items-center py-20 text-ink-500 gap-3">
          <Star size={32} />
          <p className="text-sm font-body">No favorites yet — star stories from the Feed.</p>
        </div>
      )}

      {!loading && favorites.length > 0 && (
        <div className="grid gap-3">
          {favorites.map((fav, i) => {
            const item = fav.news_item
            if (!item) return null
            return (
              <article
                key={fav.id}
                className="card p-4 animate-slide-up"
                style={{ animationDelay: `${i * 25}ms` }}
              >
                <div className="flex items-start justify-between gap-4">
                  <div className="flex-1 min-w-0">
                    {/* Source + time */}
                    <div className="flex items-center gap-2 mb-2">
                      {item.source && (
                        <span className="tag">{item.source.name}</span>
                      )}
                      <span className="text-xs text-ink-500 font-mono">
                        {fav.created_at
                          ? formatDistanceToNow(new Date(fav.created_at), { addSuffix: true })
                          : ''}
                      </span>
                    </div>

                    {/* Title */}
                    <h3 className="font-display font-600 text-sm text-white leading-snug mb-1.5">
                      {item.title}
                    </h3>

                    {/* Summary */}
                    {(item.ai_summary || item.summary) && (
                      <p className="text-xs text-ink-400 leading-relaxed line-clamp-2">
                        {item.ai_summary || item.summary}
                      </p>
                    )}
                  </div>

                  {/* Actions */}
                  <div className="flex flex-col gap-2 shrink-0">
                    <button
                      onClick={() => setBroadcastTarget(fav)}
                      className="flex items-center gap-1.5 px-3 py-1.5 bg-pulse-500/15 hover:bg-pulse-500/25 
                                 border border-pulse-500/30 text-pulse-400 rounded-lg text-xs font-body font-500 
                                 transition-all duration-150 whitespace-nowrap"
                    >
                      <Send size={12} />
                      Broadcast
                    </button>
                    <a
                      href={item.url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="flex items-center gap-1.5 px-3 py-1.5 btn-ghost text-xs whitespace-nowrap"
                    >
                      <ExternalLink size={12} />
                      Open
                    </a>
                    <button
                      onClick={() => remove(item.id)}
                      className="flex items-center gap-1.5 px-3 py-1.5 text-xs text-ink-500 hover:text-red-400 
                                 border border-ink-600 hover:border-red-400/40 rounded-lg transition-all duration-150"
                    >
                      <Trash2 size={12} />
                      Remove
                    </button>
                  </div>
                </div>
              </article>
            )
          })}
        </div>
      )}

      {broadcastTarget && (
        <BroadcastModal
          favoriteId={broadcastTarget.id}
          newsItem={broadcastTarget.news_item}
          onClose={() => setBroadcastTarget(null)}
        />
      )}
    </div>
  )
}
