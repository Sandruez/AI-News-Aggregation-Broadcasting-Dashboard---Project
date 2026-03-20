import { Routes, Route, Navigate } from 'react-router-dom'
import Layout from './components/Layout'
import FeedPage from './pages/FeedPage'
import FavoritesPage from './pages/FavoritesPage'
import SourcesPage from './pages/SourcesPage'

export default function App() {
  return (
    <Layout>
      <Routes>
        <Route path="/" element={<Navigate to="/feed" replace />} />
        <Route path="/feed" element={<FeedPage />} />
        <Route path="/favorites" element={<FavoritesPage />} />
        <Route path="/sources" element={<SourcesPage />} />
      </Routes>
    </Layout>
  )
}
