import { useEffect, useState } from 'react'
import { NavLink } from 'react-router-dom'
import { checkHealth } from '../api/api'

const links = [
  { to: '/', label: 'Home' },
  { to: '/generate', label: 'Studio' },
  { to: '/history', label: 'Library' },
]

export default function Navbar() {
  const [online, setOnline] = useState(null)

  useEffect(() => {
    let active = true

    async function ping() {
      const { ok } = await checkHealth()
      if (active) {
        setOnline(ok)
      }
    }

    ping()
    const intervalId = window.setInterval(ping, 15_000)

    return () => {
      active = false
      window.clearInterval(intervalId)
    }
  }, [])

  return (
    <header className="topbar">
      <div className="topbar-inner">
        <NavLink to="/" className="brand">
          <span className="brand-mark">
            <span className="brand-mark-core">DS</span>
          </span>
          <span className="brand-copy">
            <strong>DreamScape</strong>
            <small>Emotion to Film Studio</small>
          </span>
        </NavLink>

        <div className="topbar-panel">
          <nav className="nav-links" aria-label="Primary">
            {links.map((link) => (
              <NavLink
                key={link.to}
                to={link.to}
                end={link.to === '/'}
                className={({ isActive }) => (isActive ? 'nav-link active' : 'nav-link')}
              >
                {link.label}
              </NavLink>
            ))}
          </nav>

          <div className="status-pill">
            <span className="status-copy">
              <strong>Runtime</strong>
              <small>
                {online === null ? 'Checking backend' : online ? 'Backend online' : 'Backend offline'}
              </small>
            </span>
            <span
              className={
                online === false ? 'status-dot status-dot-offline' : 'status-dot status-dot-online'
              }
            />
          </div>
        </div>
      </div>
    </header>
  )
}
