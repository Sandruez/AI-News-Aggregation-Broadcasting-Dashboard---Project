import { Star, ExternalLink, Clock, User } from 'lucide-react'
import { formatDistanceToNow } from 'date-fns'
import clsx from 'clsx'

const CATEGORY_COLORS = {
  lab: 'bg-purple-100 text-purple-800 border-purple-200',
  media: 'bg-blue-100 text-blue-800 border-blue-200',
  research: 'bg-green-100 text-green-800 border-green-200',
  community: 'bg-orange-100 text-orange-800 border-orange-200',
  vc: 'bg-yellow-100 text-yellow-800 border-yellow-200',
  products: 'bg-pink-100 text-pink-800 border-pink-200',
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

  const catColor = CATEGORY_COLORS[item.source?.category] || 'bg-gray-100 text-gray-800 border-gray-200'

  return (
    <article className="bg-white rounded-xl border border-gray-200 shadow-sm hover:shadow-md transition-all duration-200 overflow-hidden group">
      <div className="p-6 space-y-4">
        {/* Header row */}
        <div className="flex flex-col sm:flex-row sm:items-start justify-between gap-3">
          <div className="flex flex-wrap items-center gap-2">
            {item.source && (
              <span className={clsx('inline-flex items-center px-3 py-1 rounded-full text-xs font-medium border', catColor)}>
                {item.source.name}
              </span>
            )}
            {item.tags?.slice(0, 2).map(tag => (
              <span key={tag} className="inline-flex items-center px-2.5 py-1 rounded-full text-xs font-medium bg-gray-100 text-gray-800 border border-gray-200">
                {tag}
              </span>
            ))}
            <ImpactBadge score={item.impact_score} />
          </div>

          <div className="flex items-center gap-2">
            <button
              onClick={() => onToggleFavorite(item)}
              className={clsx(
                'p-2 rounded-lg transition-all duration-200 focus:outline-none focus:ring-2 focus:ring-purple-500 focus:ring-offset-2',
                item.is_favorited
                  ? 'bg-purple-100 text-purple-700 hover:bg-purple-200'
                  : 'bg-gray-100 text-gray-600 hover:bg-gray-200 hover:text-gray-900'
              )}
              aria-label={item.is_favorited ? 'Remove from favorites' : 'Add to favorites'}
            >
              <Star size={18} className={item.is_favorited ? 'fill-current' : ''} />
            </button>
            
            <button
              onClick={() => onBroadcast(item)}
              className="p-2 rounded-lg bg-gray-100 text-gray-600 hover:bg-gray-200 hover:text-gray-900 transition-all duration-200 focus:outline-none focus:ring-2 focus:ring-purple-500 focus:ring-offset-2"
              aria-label="Broadcast article"
            >
              <ExternalLink size={18} />
            </button>
          </div>
        </div>

        {/* Content */}
        <div className="space-y-3">
          <h3 className="text-lg font-semibold text-gray-900 leading-tight hover:text-purple-700 transition-colors duration-200 cursor-pointer">
            {item.title}
          </h3>
          
          {item.summary && (
            <p className="text-gray-600 leading-relaxed line-clamp-3">
              {item.summary}
            </p>
          )}
        </div>

        {/* Footer */}
        <div className="flex items-center justify-between pt-4 border-t border-gray-100">
          <div className="flex items-center gap-4 text-sm text-gray-500">
            <div className="flex items-center gap-1">
              <Clock size={14} />
              <span>{timeAgo}</span>
            </div>
            {item.author && (
              <div className="flex items-center gap-1">
                <User size={14} />
                <span>{item.author}</span>
              </div>
            )}
          </div>
          
          {item.url && (
            <a
              href={item.url}
              target="_blank"
              rel="noopener noreferrer"
              className="inline-flex items-center gap-1 text-sm font-medium text-purple-600 hover:text-purple-700 transition-colors duration-200 focus:outline-none focus:ring-2 focus:ring-purple-500 focus:ring-offset-2 rounded"
            >
              Read more
              <ExternalLink size={14} />
            </a>
          )}
        </div>
      </div>
    </article>
  )
}
