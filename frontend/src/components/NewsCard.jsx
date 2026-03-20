import { Star, ExternalLink, Clock, User } from 'lucide-react'
import { formatDistanceToNow } from 'date-fns'
import clsx from 'clsx'

const CATEGORY_COLORS = {
  lab: 'text-pulse-400 bg-pulse-500/10 border-pulse-500/20',
  media: 'text-sky-400 bg-sky-400/10 border-sky-400/20',
  research: 'text-acid-400 bg-acid-400/10 border-acid-400/20',
  community: 'text-ember-400 bg-ember-400/10 border-ember-400/20',
  vc: 'text-yellow-400 bg-yellow-400/10 border-yellow-400/20',
  products: 'text-pink-400 bg-pink-400/10 border-pink-400/20',
}

function ImpactBadge({ score }) {
  const color =
    score >= 8 ? 'bg-acid-500/20 text-acid-400 border border-acid-500/30' :
    score >= 5 ? 'bg-ember-500/20 text-ember-400 border border-ember-500/30' :
                 'bg-ink-700 text-ink-400 border border-ink-600'
  return (
    <span className={clsx('impact-badge text-xs font-mono px-2 py-0.5 rounded-md', color)}>
      {score}/10
    </span>
  )
}

export default function NewsCard({ item, onToggleFavorite, onBroadcast }) {
  const timeAgo = item.published_at
    ? formatDistanceToNow(new Date(item.published_at), { addSuffix: true })
    : 'Unknown date'

  const catColor = CATEGORY_COLORS[item.source?.category] || 'text-ink-400 bg-ink-700 border-ink-600'

  return (
    <article className="card p-4 animate-slide-up group">
      {/* Header row */}
      <div className="flex items-start justify-between gap-3 mb-2">
        <div className="flex items-center gap-2 flex-wrap">
          {item.source && (
            <span className={clsx('tag border', catColor)}>
              {item.source.name}
            </span>
          )}
          {item.tags?.slice(0, 2).map(tag => (
            <span key={tag} className="tag">{tag}</span>
          ))}
          <ImpactBadge score={item.impact_score} />
        </div>

        <button
          onClick={() => onToggleFavorite(item)}
          className={clsx(
            'shrink-0 p-1.5 rounded-lg transition-all duration-150',
            item.is_favorited
              ? 'text-yellow-400 bg-yellow-400/10'
              : 'text-ink-500 hover:text-yellow-400 hover:bg-yellow-400/10'
          )}
          title={item.is_favorited ? 'Remove from favorites' : 'Save to favorites'}
        >
          <Star size={15} fill={item.is_favorited ? 'currentColor' : 'none'} />
        </button>
      </div>

      {/* Title */}
      <h3 className="font-display font-600 text-sm text-white leading-snug mb-1.5 group-hover:text-pulse-300 transition-colors">
        {item.title}
      </h3>

      {/* AI Summary or raw summary */}
      {(item.ai_summary || item.summary) && (
        <p className="text-xs text-ink-400 leading-relaxed line-clamp-2 mb-3">
          {item.ai_summary || item.summary}
        </p>
      )}

      {/* Footer */}
      <div className="flex items-center justify-between pt-2 border-t border-ink-700">
        <div className="flex items-center gap-3 text-xs text-ink-500">
          <span className="flex items-center gap-1">
            <Clock size={11} />
            {timeAgo}
          </span>
          {item.author && (
            <span className="flex items-center gap-1">
              <User size={11} />
              {item.author.slice(0, 20)}
            </span>
          )}
        </div>

        <div className="flex items-center gap-2">
          {item.is_favorited && onBroadcast && (
            <button
              onClick={() => onBroadcast(item)}
              className="text-xs text-pulse-400 hover:text-pulse-300 font-body font-500 transition-colors"
            >
              Broadcast →
            </button>
          )}
          <a
            href={item.url}
            target="_blank"
            rel="noopener noreferrer"
            className="text-ink-500 hover:text-white transition-colors"
          >
            <ExternalLink size={13} />
          </a>
        </div>
      </div>
    </article>
  )
}
