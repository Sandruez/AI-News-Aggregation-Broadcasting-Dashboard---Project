import { NavLink } from 'react-router-dom'
import { Rss, Star, Settings, Zap, BarChart3 } from 'lucide-react'
import clsx from 'clsx'

const navItems = [
  { to: '/feed', icon: Rss, label: 'Feed' },
  { to: '/favorites', icon: Star, label: 'Favorites' },
  { to: '/sources', icon: Settings, label: 'Sources' },
  { to: '/admin', icon: BarChart3, label: 'Admin' },
]

export default function Layout({ children }) {
  return (
    <div className="flex min-h-screen bg-ink-950">
      {/* Sidebar */}
      <aside className="w-56 shrink-0 flex flex-col border-r border-ink-700 bg-ink-900 sticky top-0 h-screen">
        {/* Logo */}
        <div className="px-5 pt-6 pb-8">
          <div className="flex items-center gap-2">
            <div className="w-7 h-7 rounded-lg bg-pulse-500 flex items-center justify-center">
              <Zap size={14} className="text-white" />
            </div>
            <span className="font-display font-800 text-lg tracking-tight text-white">Pulse</span>
          </div>
          <p className="text-xs text-ink-400 mt-1 font-body">AI News Intelligence</p>
        </div>

        {/* Nav */}
        <nav className="flex-1 px-3 space-y-1">
          {navItems.map(({ to, icon: Icon, label }) => (
            <NavLink
              key={to}
              to={to}
              className={({ isActive }) =>
                clsx(
                  'flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-body font-500 transition-all duration-150',
                  isActive
                    ? 'bg-pulse-500/15 text-pulse-400 border border-pulse-500/25'
                    : 'text-ink-400 hover:text-white hover:bg-ink-700'
                )
              }
            >
              <Icon size={16} />
              {label}
            </NavLink>
          ))}
        </nav>

        {/* Footer */}
        <div className="px-5 py-4 border-t border-ink-700">
          <p className="text-xs text-ink-500 font-mono">v1.0 · Powered by Groq</p>
        </div>
      </aside>

      {/* Main content */}
      <main className="flex-1 overflow-auto">
        {children}
      </main>
    </div>
  )
}
