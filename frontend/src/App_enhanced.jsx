// Enhanced App.jsx with Theme Provider
import { BrowserRouter } from 'react-router-dom'
import { ThemeProvider } from './contexts/ThemeContext'
import Layout from './components/Layout_enhanced'
import FeedPage from './pages/FeedPage'
import FavoritesPage from './pages/FavoritesPage'
import SourcesPage from './pages/SourcesPage'
import AdminPage from './pages/AdminPage'

function App() {
  return (
    <ThemeProvider>
      <BrowserRouter>
        <Layout>
          <Routes>
            <Route path="/" element={<Navigate to="/feed" replace />} />
            <Route path="/feed" element={<FeedPage />} />
            <Route path="/favorites" element={<FavoritesPage />} />
            <Route path="/sources" element={<SourcesPage />} />
            <Route path="/admin" element={<AdminPage />} />
          </Routes>
        </Layout>
      </BrowserRouter>
    </ThemeProvider>
  )
}

export default App
