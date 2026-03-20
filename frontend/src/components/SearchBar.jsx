import { useState, useRef } from 'react'
import { Search, SlidersHorizontal, X, RefreshCw } from 'lucide-react'
import clsx from 'clsx'

const SORT_OPTIONS = [
  { value: 'date', label: 'Latest' },
  { value: 'impact', label: 'Impact' },
  { value: 'source', label: 'Source' },
]

const CATEGORIES = ['lab', 'media', 'research', 'community', 'vc', 'products']

export default function SearchBar({ params, setParams, onRefresh, refreshing, total }) {
  const [showFilters, setShowFilters] = useState(false)
  const searchRef = useRef()

  const updateParam = (key, value) => setParams(p => ({ ...p, [key]: value || null, page: 1 }))

  return (
    <div className="space-y-3">
      {/* Top row */}
      <div className="flex items-center gap-3">
        {/* Search */}
        <div className="relative flex-1">
          <Search size={14} className="absolute left-3 top-1/2 -translate-y-1/2 text-ink-500 pointer-events-none" />
          <input
            ref={searchRef}
            type="text"
            placeholder="Search AI news…"
            defaultValue={params.q || ''}
            onKeyDown={e => e.key === 'Enter' && updateParam('q', e.target.value)}
            className="w-full bg-ink-800 border border-ink-600 rounded-lg pl-9 pr-4 py-2 text-sm text-white 
                       placeholder:text-ink-500 focus:outline-none focus:border-pulse-500 transition-colors font-body"
          />
          {params.q && (
            <button
              onClick={() => { updateParam('q', ''); searchRef.current.value = '' }}
              className="absolute right-3 top-1/2 -translate-y-1/2 text-ink-500 hover:text-white"
            >
              <X size={13} />
            </button>
          )}
        </div>

        {/* Sort */}
        <select
          value={params.sort_by || 'date'}
          onChange={e => updateParam('sort_by', e.target.value)}
          className="bg-ink-800 border border-ink-600 text-ink-300 text-sm rounded-lg px-3 py-2 
                     focus:outline-none focus:border-pulse-500 cursor-pointer"
        >
          {SORT_OPTIONS.map(o => <option key={o.value} value={o.value}>{o.label}</option>)}
        </select>

        {/* Filter toggle */}
        <button
          onClick={() => setShowFilters(f => !f)}
          className={clsx('btn-ghost flex items-center gap-2', showFilters && 'text-pulse-400 border-pulse-500/40')}
        >
          <SlidersHorizontal size={14} />
          Filters
        </button>

        {/* Refresh */}
        <button
          onClick={onRefresh}
          disabled={refreshing}
          className="btn-ghost flex items-center gap-2"
          title="Re-fetch all sources"
        >
          <RefreshCw size={14} className={refreshing ? 'animate-spin' : ''} />
          {refreshing ? 'Fetching…' : 'Refresh'}
        </button>
      </div>

      {/* Filter row */}
      {showFilters && (
        <div className="flex items-center gap-2 flex-wrap animate-fade-in">
          <span className="text-xs text-ink-500 font-body">Category:</span>
          {CATEGORIES.map(cat => (
            <button
              key={cat}
              onClick={() => updateParam('category', params.category === cat ? null : cat)}
              className={clsx(
                'px-3 py-1 rounded-full text-xs font-body border transition-all duration-150',
                params.category === cat
                  ? 'bg-pulse-500/20 border-pulse-500/40 text-pulse-300'
                  : 'border-ink-600 text-ink-400 hover:border-ink-500 hover:text-white'
              )}
            >
              {cat}
            </button>
          ))}
          {params.category && (
            <button onClick={() => updateParam('category', null)} className="text-xs text-ink-500 hover:text-white">
              <X size={12} />
            </button>
          )}
        </div>
      )}

      {/* Result count */}
      <p className="text-xs text-ink-500 font-mono">
        {total.toLocaleString()} stories
        {params.q && <> matching <span className="text-ink-300">"{params.q}"</span></>}
      </p>
    </div>
  )
}
