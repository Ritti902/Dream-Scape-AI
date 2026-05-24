import { BrowserRouter, Route, Routes } from 'react-router-dom'
import Navbar from './components/Navbar'
import Generate from './pages/Generate'
import History from './pages/History'
import Home from './pages/Home'
import './styles/global.css'

export default function App() {
  return (
    <BrowserRouter>
      <div className="app-shell">
        <div className="app-ambient app-ambient-left" aria-hidden="true" />
        <div className="app-ambient app-ambient-right" aria-hidden="true" />
        <div className="app-grid-overlay" aria-hidden="true" />
        <Navbar />
        <main className="app-main">
          <div className="app-main-inner">
            <Routes>
              <Route path="/" element={<Home />} />
              <Route path="/generate" element={<Generate />} />
              <Route path="/history" element={<History />} />
            </Routes>
          </div>
        </main>
      </div>
    </BrowserRouter>
  )
}
