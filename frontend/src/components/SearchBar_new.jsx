import { Search, SlidersHorizontal, RefreshCw, X } from 'lucide-react'
import { useRef, useState } from 'react'
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
    <div className="w-full bg-white rounded-xl border border-gray-200 shadow-sm p-4 space-y-4">
      {/* Search Input - Mobile First */}
      <div className="relative">
        <Search size={20} className="absolute left-4 top-1/2 -translate-y-1/2 text-gray-400 pointer-events-none" />
        <input
          ref={searchRef}
          type="text"
          placeholder="Search AI news..."
          value={params.q || ''}
          onChange={e => updateParam('q', e.target.value)}
          onKeyDown={e => e.key === 'Enter' && updateParam('q', e.target.value)}
          className="w-full pl-12 pr-12 py-3 bg-gray-50 border border-gray-300 rounded-lg text-gray-900 placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-purple-500 transition-all duration-200"
        />
        {params.q && (
          <button
            onClick={() => { updateParam('q', ''); searchRef.current.value = '' }}
            className="absolute right-4 top-1/2 -translate-y-1/2 text-gray-400 hover:text-gray-600 transition-colors duration-200"
            aria-label="Clear search"
          >
            <X size={18} />
          </button>
        )}
      </div>

      {/* Controls Row - Responsive Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3">
        {/* Sort Dropdown */}
        <div className="relative">
          <select
            value={params.sort_by}
            onChange={e => updateParam('sort_by', e.target.value)}
            className="w-full appearance-none bg-gray-50 border border-gray-300 rounded-lg px-4 py-3 pr-10 text-gray-900 focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-purple-500 transition-all duration-200 cursor-pointer"
          >
            {SORT_OPTIONS.map(o => <option key={o.value} value={o.value}>{o.label}</option>)}
          </select>
          <div className="absolute inset-y-0 right-0 flex items-center pr-3 pointer-events-none">
            <SlidersHorizontal size={16} className="text-gray-400" />
          </div>
        </div>

        {/* Filter Toggle */}
        <button
          onClick={() => setShowFilters(f => !f)}
          className={clsx(
            'flex items-center justify-center gap-2 px-4 py-3 rounded-lg font-medium transition-all duration-200 focus:outline-none focus:ring-2 focus:ring-purple-500 focus:ring-offset-2',
            showFilters 
              ? 'bg-purple-100 text-purple-700 border border-purple-200' 
              : 'bg-gray-50 text-gray-700 border border-gray-300 hover:bg-gray-100'
          )}
        >
          <SlidersHorizontal size={18} />
          <span>Filters</span>
        </button>

        {/* Refresh Button */}
        <button
          onClick={onRefresh}
          disabled={refreshing}
          className="flex items-center justify-center gap-2 px-4 py-3 rounded-lg font-medium bg-gray-50 text-gray-700 border border-gray-300 hover:bg-gray-100 transition-all duration-200 focus:outline-none focus:ring-2 focus:ring-purple-500 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          <RefreshCw size={18} className={refreshing ? 'animate-spin' : ''} />
          <span>{refreshing ? 'Fetching…' : 'Refresh'}</span>
        </button>
      </div>

      {/* Category Filters - Collapsible */}
      {showFilters && (
        <div className="space-y-3 pt-4 border-t border-gray-200 animate-fade-in">
          <div className="flex items-center gap-2 flex-wrap">
            <span className="text-sm font-semibold text-gray-700">Category:</span>
            {CATEGORIES.map(cat => (
              <button
                key={cat}
                onClick={() => updateParam('category', params.category === cat ? null : cat)}
                className={clsx(
                  'px-3 py-1.5 rounded-full text-sm font-medium border transition-all duration-200 focus:outline-none focus:ring-2 focus:ring-purple-500 focus:ring-offset-2',
                  params.category === cat
                    ? 'bg-purple-100 text-purple-700 border-purple-300 shadow-sm'
                    : 'bg-gray-100 text-gray-700 border-gray-300 hover:bg-gray-200'
                )}
              >
                {cat}
              </button>
            ))}
            {params.category && (
              <button 
                onClick={() => updateParam('category', null)} 
                className="px-3 py-1.5 rounded-full text-sm font-medium text-gray-600 hover:text-gray-900 transition-colors duration-200"
              >
                <X size={16} className="inline" /> Clear
              </button>
            )}
          </div>
        </div>
      )}

      {/* Results Count */}
      <div className="pt-3 border-t border-gray-200">
        <p className="text-sm text-gray-600 font-medium">
          {total.toLocaleString()} stories
          {params.q && (
            <span className="text-gray-500">
              {' '}matching <span className="font-semibold text-gray-700">"{params.q}"</span>
            </span>
          )}
        </p>
      </div>
    </div>
  )
}
