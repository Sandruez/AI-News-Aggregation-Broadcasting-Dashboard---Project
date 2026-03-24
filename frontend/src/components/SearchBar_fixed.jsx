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

  const updateParam = (key, value) => {
    setParams(p => ({ ...p, [key]: value || null, page: 1 }))
  }

  return (
    <div className="space-y-4">
      {/* Search input */}
      <div className="relative">
        <Search size={18} className="absolute left-4 top-1/2 -translate-y-1/2 text-gray-400 pointer-events-none" />
        <input
          ref={searchRef}
          type="text"
          placeholder="Search AI news..."
          value={params.q || ''}
          onChange={e => updateParam('q', e.target.value)}
          onKeyDown={e => e.key === 'Enter' && updateParam('q', e.target.value)}
          className="w-full pl-12 pr-4 py-3 bg-white border border-gray-300 rounded-lg text-gray-900 placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
        />
        {params.q && (
          <button
            onClick={() => { updateParam('q', ''); searchRef.current.value = '' }}
            className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-400 hover:text-gray-600"
          >
            <X size={16} />
          </button>
        )}
      </div>

      {/* Filters row - responsive */}
      <div className="flex flex-col sm:flex-row gap-3">
        {/* Sort dropdown */}
        <select
          value={params.sort_by}
          onChange={e => updateParam('sort_by', e.target.value)}
          className="flex-1 sm:flex-none px-4 py-2 bg-white border border-gray-300 rounded-lg text-gray-900 focus:outline-none focus:ring-2 focus:ring-blue-500"
        >
          {SORT_OPTIONS.map(o => <option key={o.value} value={o.value}>{o.label}</option>)}
        </select>

        {/* Filter toggle */}
        <button
          onClick={() => setShowFilters(f => !f)}
          className="flex-1 sm:flex-none px-4 py-2 bg-gray-100 hover:bg-gray-200 rounded-lg text-gray-700 font-medium transition-colors"
        >
          {showFilters ? 'Hide Filters' : 'Show Filters'}
        </button>

        {/* Refresh button */}
        <button
          onClick={onRefresh}
          disabled={refreshing}
          className="flex-1 sm:flex-none px-4 py-2 bg-blue-500 hover:bg-blue-600 disabled:bg-blue-300 text-white rounded-lg font-medium transition-colors disabled:opacity-50"
        >
          {refreshing ? 'Refreshing…' : 'Refresh'}
        </button>
      </div>

      {/* Category filters */}
      {showFilters && (
        <div className="flex flex-wrap gap-2 pt-4 border-t border-gray-200">
          {CATEGORIES.map(cat => (
            <button
              key={cat}
              onClick={() => updateParam('category', params.category === cat ? null : cat)}
              className={clsx(
                'px-3 py-1 rounded-full text-sm font-medium border transition-colors',
                params.category === cat
                  ? 'bg-blue-500 text-white border-blue-600'
                  : 'bg-gray-100 text-gray-700 border-gray-300 hover:bg-gray-200'
              )}
            >
              {cat}
            </button>
          ))}
          {params.category && (
            <button 
              onClick={() => updateParam('category', null)} 
              className="px-3 py-1 rounded-full text-sm font-medium text-gray-500 hover:text-gray-700"
            >
              Clear
            </button>
          )}
        </div>
      )}

      {/* Results count */}
      <div className="text-sm text-gray-600">
        {total.toLocaleString()} stories found
        {params.q && (
          <span> matching "{params.q}"</span>
        )}
      </div>
    </div>
  )
}
