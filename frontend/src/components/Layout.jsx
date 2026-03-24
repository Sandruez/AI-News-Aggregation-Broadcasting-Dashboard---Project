import { NavLink } from 'react-router-dom'
import { Rss, Star, Settings, Zap, BarChart3, Menu, X } from 'lucide-react'
import { useState, useEffect, useRef } from 'react'
import clsx from 'clsx'

const navItems = [
  { to: '/feed', icon: Rss, label: 'Feed' },
  { to: '/favorites', icon: Star, label: 'Favorites' },
  { to: '/sources', icon: Settings, label: 'Sources' },
  { to: '/admin', icon: BarChart3, label: 'Admin' },
]

export default function Layout({ children }) {
  const [isSidebarOpen, setIsSidebarOpen] = useState(false)
  const sidebarRef = useRef(null)
  const overlayRef = useRef(null)

  // Close sidebar when clicking outside
  useEffect(() => {
    const handleClickOutside = (event) => {
      if (isSidebarOpen && 
          sidebarRef.current && 
          !sidebarRef.current.contains(event.target) &&
          overlayRef.current &&
          overlayRef.current.contains(event.target)) {
        setIsSidebarOpen(false)
      }
    }

    const handleEscapeKey = (event) => {
      if (event.key === 'Escape' && isSidebarOpen) {
        setIsSidebarOpen(false)
      }
    }

    if (isSidebarOpen) {
      document.addEventListener('mousedown', handleClickOutside)
      document.addEventListener('keydown', handleEscapeKey)
      // Prevent body scroll when sidebar is open
      document.body.style.overflow = 'hidden'
    } else {
      document.body.style.overflow = 'unset'
    }

    return () => {
      document.removeEventListener('mousedown', handleClickOutside)
      document.removeEventListener('keydown', handleEscapeKey)
      document.body.style.overflow = 'unset'
    }
  }, [isSidebarOpen])

  const toggleSidebar = () => {
    setIsSidebarOpen(!isSidebarOpen)
  }

  const closeSidebar = () => {
    setIsSidebarOpen(false)
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Mobile Header with Hamburger Menu */}
      <header className="lg:hidden sticky top-0 z-50 bg-white border-b border-gray-200 shadow-sm">
        <div className="flex items-center justify-between px-4 py-3">
          <div className="flex items-center gap-3">
            {/* Hamburger Menu Button */}
            <button
              onClick={toggleSidebar}
              className="p-2.5 rounded-lg bg-gray-100 hover:bg-gray-200 transition-all duration-200 focus:outline-none focus:ring-2 focus:ring-purple-500 focus:ring-offset-2"
              aria-label="Open sidebar menu"
              aria-expanded={isSidebarOpen}
            >
              <Menu size={20} className="text-gray-700" />
            </button>
            
            {/* Mobile Logo */}
            <div className="flex items-center gap-2">
              <div className="w-8 h-8 rounded-lg bg-purple-600 flex items-center justify-center shadow-sm">
                <Zap size={16} className="text-white" />
              </div>
              <span className="font-bold text-lg text-gray-900">Pulse</span>
            </div>
          </div>
          
          {/* Mobile Header Right Side - Add future elements here */}
          <div className="flex items-center gap-2">
            {/* Placeholder for future header elements */}
          </div>
        </div>
      </header>

      {/* Mobile Sidebar Overlay */}
      <div 
        ref={overlayRef}
        className={clsx(
          "lg:hidden fixed inset-0 z-40 bg-black/50 transition-opacity duration-300",
          isSidebarOpen ? "opacity-100 pointer-events-auto" : "opacity-0 pointer-events-none"
        )}
        aria-hidden={!isSidebarOpen}
      />

      {/* Responsive Sidebar */}
      <aside
        ref={sidebarRef}
        className={clsx(
          "fixed lg:static inset-y-0 left-0 z-50 w-72 max-w-[80vw] bg-white border-r border-gray-200 transform transition-transform duration-300 ease-in-out lg:translate-x-0 lg:transform-none",
          isSidebarOpen ? "translate-x-0" : "-translate-x-full lg:translate-x-0"
        )}
        aria-label="Main navigation"
      >
        {/* Close Button for Mobile */}
        <div className="lg:hidden flex items-center justify-between p-4 border-b border-gray-100">
          <div className="flex items-center gap-2">
            <div className="w-8 h-8 rounded-lg bg-purple-600 flex items-center justify-center">
              <Zap size={16} className="text-white" />
            </div>
            <span className="font-bold text-lg text-gray-900">Pulse</span>
          </div>
          <button
            onClick={closeSidebar}
            className="p-2 rounded-lg hover:bg-gray-100 transition-all duration-200 focus:outline-none focus:ring-2 focus:ring-purple-500 focus:ring-offset-2"
            aria-label="Close sidebar menu"
          >
            <X size={20} className="text-gray-700" />
          </button>
        </div>

        {/* Logo (Desktop Only) */}
        <div className="hidden lg:block px-6 pt-6 pb-8 border-b border-gray-100">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-purple-600 flex items-center justify-center shadow-lg">
              <Zap size={20} className="text-white" />
            </div>
            <div>
              <span className="font-bold text-xl text-gray-900 block">Pulse</span>
              <p className="text-sm text-gray-500">AI News Intelligence</p>
            </div>
          </div>
        </div>

        {/* Navigation */}
        <nav className="flex-1 px-4 py-6 lg:px-6 lg:py-8 space-y-2">
          <h2 className="hidden lg:block text-xs font-semibold text-gray-400 uppercase tracking-wider mb-4">
            Navigation
          </h2>
          {navItems.map(({ to, icon: Icon, label }) => (
            <NavLink
              key={to}
              to={to}
              onClick={closeSidebar}
              className={({ isActive }) =>
                clsx(
                  'flex items-center gap-3 px-4 py-3 rounded-xl text-sm font-medium transition-all duration-200 focus:outline-none focus:ring-2 focus:ring-purple-500 focus:ring-offset-2 min-h-[44px]',
                  isActive
                    ? 'bg-purple-50 text-purple-700 border border-purple-200 shadow-sm'
                    : 'text-gray-600 hover:text-gray-900 hover:bg-gray-50'
                )
              }
            >
              <Icon size={20} className="flex-shrink-0" />
              <span className="truncate">{label}</span>
            </NavLink>
          ))}
        </nav>

        {/* Footer (Desktop Only) */}
        <div className="hidden lg:block px-6 py-4 border-t border-gray-100">
          <div className="text-xs text-gray-400">
            <p>&copy; 2024 Pulse AI</p>
            <p className="mt-1">Version 1.0.0</p>
          </div>
        </div>
      </aside>

      {/* Main Content Area */}
      <main className="lg:ml-72 relative z-30">
        <div className="w-full px-4 lg:px-6">
          {children}
        </div>
      </main>
    </div>
  )
}
