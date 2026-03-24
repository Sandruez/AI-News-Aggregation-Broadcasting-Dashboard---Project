import { Star, ExternalLink, Clock, User } from 'lucide-react'
import { formatDistanceToNow } from 'date-fns'
import clsx from 'clsx'

const CATEGORY_COLORS = {
  lab: 'text-purple-600 bg-purple-50 border-purple-200',
  media: 'text-blue-600 bg-blue-50 border-blue-200',
  research: 'text-green-600 bg-green-50 border-green-200',
  community: 'text-orange-600 bg-orange-50 border-orange-200',
  vc: 'text-yellow-600 bg-yellow-50 border-yellow-200',
  products: 'text-pink-600 bg-pink-50 border-pink-200',
}

function ImpactBadge({ score }) {
  const color =
    score >= 8 ? 'bg-green-100 text-green-800 border-green-200' :
    score >= 5 ? 'bg-orange-100 text-orange-800 border-orange-200' :
                 'bg-gray-100 text-gray-800 border-gray-200'
  return (
    <span className={clsx('inline-flex items-center px-2.5 py-1 rounded-full text-xs font-semibold border', color)}>
      {score}/10
    </span>
  )
}

export default function NewsCard({ item, onToggleFavorite, onBroadcast }) {
  const timeAgo = item.published_at
    ? formatDistanceToNow(new Date(item.published_at), { addSuffix: true })
    : 'Unknown date'

  const catColor = CATEGORY_COLORS[item.source?.category] || 'text-blue-600 bg-blue-50 border-blue-200'

  return (
    <article className="bg-white rounded-lg border border-gray-200 shadow-sm hover:shadow-md transition-all duration-200 overflow-hidden group">
      <div className="p-5 space-y-4">
        {/* Header row */}
        <div className="flex items-start justify-between gap-3">
          <div className="flex items-center gap-2 flex-wrap">
            {item.source && (
              <span className={clsx('px-3 py-1 rounded-full text-xs font-medium border', catColor)}>
                {item.source.name}
              </span>
            )}
            {item.tags?.slice(0, 2).map(tag => (
              <span key={tag} className="px-2 py-1 rounded-full text-xs font-medium bg-gray-100 text-gray-700">
                {tag}
              </span>
            ))}
            <ImpactBadge score={item.impact_score} />
          </div>

          <div className="flex items-center gap-2 shrink-0">
            <button
              onClick={() => onToggleFavorite(item)}
              className={clsx(
                'p-2 rounded-lg transition-all duration-150',
                item.is_favorited
                  ? 'text-yellow-500 bg-yellow-50'
                  : 'text-gray-400 hover:text-yellow-500 hover:bg-yellow-50'
              )}
              title={item.is_favorited ? 'Remove from favorites' : 'Save to favorites'}
            >
              <Star size={16} fill={item.is_favorited ? 'currentColor' : 'none'} />
            </button>
            
            <button
              onClick={() => onBroadcast(item)}
              className="p-2 rounded-lg text-gray-400 hover:text-gray-600 hover:bg-gray-50 transition-all duration-150"
              title="Broadcast article"
            >
              <ExternalLink size={16} />
            </button>
          </div>
        </div>

        {/* Title */}
        <h3 className="font-semibold text-base text-gray-900 leading-snug group-hover:text-blue-600 transition-colors">
          {item.title}
        </h3>

        {/* Summary */}
        {(item.ai_summary || item.summary) && (
          <p className="text-sm text-gray-600 leading-relaxed line-clamp-3">
            {item.ai_summary || item.summary}
          </p>
        )}

        {/* Footer */}
        <div className="flex items-center justify-between pt-3 border-t border-gray-100">
          <div className="flex items-center gap-3 text-xs text-gray-500">
            <span className="flex items-center gap-1">
              <Clock size={12} />
              {timeAgo}
            </span>
            {item.author && (
              <span className="flex items-center gap-1">
                <User size={12} />
                {item.author.slice(0, 20)}
              </span>
            )}
          </div>

          <div className="flex items-center gap-2">
            {item.is_favorited && onBroadcast && (
              <button
                onClick={() => onBroadcast(item)}
                className="text-xs text-blue-600 hover:text-blue-700 font-medium transition-colors"
              >
                Broadcast →
              </button>
            )}
            <a
              href={item.url}
              target="_blank"
              rel="noopener noreferrer"
              className="text-gray-400 hover:text-gray-600 transition-colors"
            >
              <ExternalLink size={14} />
            </a>
          </div>
        </div>
      </div>
    </article>
  )
}
