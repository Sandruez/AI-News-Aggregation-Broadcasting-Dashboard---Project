import { useState, useEffect } from 'react'
import { fetchSources, toggleSource } from '../utils/api'
import { Rss, ToggleLeft, ToggleRight, Loader2, Globe } from 'lucide-react'
import clsx from 'clsx'

const TYPE_COLORS = {
  rss: 'text-ember-400 bg-ember-400/10 border-ember-400/20',
  hn: 'text-yellow-400 bg-yellow-400/10 border-yellow-400/20',
  reddit: 'text-orange-400 bg-orange-400/10 border-orange-400/20',
  arxiv: 'text-acid-400 bg-acid-400/10 border-acid-400/20',
  producthunt: 'text-pink-400 bg-pink-400/10 border-pink-400/20',
}

export default function SourcesPage() {
  const [sources, setSources] = useState([])
  const [loading, setLoading] = useState(true)
  const [toggling, setToggling] = useState(null)

  useEffect(() => {
    fetchSources().then(data => { setSources(data); setLoading(false) })
  }, [])

  const handleToggle = async (source) => {
    setToggling(source.id)
    try {
      const result = await toggleSource(source.id)
      setSources(prev => prev.map(s => s.id === source.id ? { ...s, active: result.active } : s))
    } catch (e) {
      console.error(e)
    } finally {
      setToggling(null)
    }
  }

  const active = sources.filter(s => s.active).length

  return (
    <div className="max-w-4xl mx-auto px-6 py-8">
      <div className="mb-6">
        <h1 className="font-display font-800 text-2xl text-white tracking-tight">Sources</h1>
        <p className="text-sm text-ink-400 mt-1 font-body">
          {active} of {sources.length} sources active. Toggle to include or exclude from ingestion.
        </p>
      </div>

      {loading && (
        <div className="flex items-center justify-center py-20 text-ink-500">
          <Loader2 size={24} className="animate-spin mr-3" />
          <span className="text-sm font-body">Loading sources…</span>
        </div>
      )}

      {!loading && (
        <div className="grid gap-2">
          {sources.map((source, i) => (
            <div
              key={source.id}
              className={clsx(
                'card flex items-center justify-between px-4 py-3 animate-slide-up',
                !source.active && 'opacity-50'
              )}
              style={{ animationDelay: `${i * 15}ms` }}
            >
              <div className="flex items-center gap-3 min-w-0">
                <Globe size={14} className="text-ink-500 shrink-0" />
                <div className="min-w-0">
                  <p className="text-sm font-body font-500 text-white truncate">{source.name}</p>
                  {source.url && (
                    <a
                      href={source.url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="text-xs text-ink-500 hover:text-ink-300 transition-colors truncate block"
                    >
                      {source.url}
                    </a>
                  )}
                </div>
              </div>

              <div className="flex items-center gap-3 shrink-0">
                {source.category && (
                  <span className={clsx('tag border text-xs', TYPE_COLORS['rss'])}>
                    {source.category}
                  </span>
                )}
                <button
                  onClick={() => handleToggle(source)}
                  disabled={toggling === source.id}
                  className="text-ink-400 hover:text-white transition-colors disabled:opacity-50"
                  title={source.active ? 'Disable source' : 'Enable source'}
                >
                  {toggling === source.id
                    ? <Loader2 size={20} className="animate-spin" />
                    : source.active
                      ? <ToggleRight size={20} className="text-pulse-400" />
                      : <ToggleLeft size={20} />
                  }
                </button>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
