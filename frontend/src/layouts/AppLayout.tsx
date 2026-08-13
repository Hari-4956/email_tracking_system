import { NavLink, Outlet, useLocation } from 'react-router-dom'
import { useMemo, useState } from 'react'

const links = [
  { to: '/', label: 'Dashboard', end: true, hint: 'Overview' },
  { to: '/campaigns', label: 'Campaigns', hint: 'Campaign list' },
  { to: '/recipients', label: 'Recipients', hint: 'Search & browse' },
  { to: '/analytics', label: 'Analytics', hint: 'Opens & trends' },
]

function titleForPath(pathname: string): { title: string; subtitle: string } {
  if (pathname.startsWith('/campaigns/')) {
    return { title: 'Campaign detail', subtitle: 'Live campaign metrics and opens' }
  }
  if (pathname.startsWith('/campaigns')) {
    return { title: 'Campaigns', subtitle: 'Browse imported campaigns' }
  }
  if (pathname.startsWith('/recipients/')) {
    return { title: 'Recipient detail', subtitle: 'Profile and open history' }
  }
  if (pathname.startsWith('/recipients')) {
    return { title: 'Recipients', subtitle: 'Search, filter, and paginate' }
  }
  if (pathname.startsWith('/analytics')) {
    return { title: 'Analytics', subtitle: 'Tracked opens and engagement' }
  }
  return { title: 'Dashboard', subtitle: 'Campaign analytics overview' }
}

export function AppLayout() {
  const [open, setOpen] = useState(false)
  const location = useLocation()
  const header = useMemo(() => titleForPath(location.pathname), [location.pathname])

  return (
    <div className={`app-shell ${open ? 'nav-open' : ''}`}>
      <aside className="sidebar" aria-label="Sidebar">
        <div className="brand">
          <span className="brand-mark" aria-hidden="true">
            E
          </span>
          <div>
            <p className="brand-title">E STAR</p>
            <p className="brand-sub">Email Tracking</p>
          </div>
        </div>

        <nav className="side-nav" aria-label="Main navigation">
          {links.map((link) => (
            <NavLink
              key={link.to}
              to={link.to}
              end={link.end}
              className={({ isActive }) => (isActive ? 'nav-link active' : 'nav-link')}
              onClick={() => setOpen(false)}
            >
              <span className="nav-label">{link.label}</span>
              <span className="nav-hint">{link.hint}</span>
            </NavLink>
          ))}
        </nav>

        <div className="side-footer">
          <p className="side-note">Read-only monitoring dashboard.</p>
          <p className="side-note subtle">Email sending remains in n8n → Gmail.</p>
        </div>
      </aside>

      <div className="main-column">
        <header className="topbar">
          <button
            type="button"
            className="btn btn-ghost menu-btn"
            aria-label="Toggle navigation menu"
            aria-expanded={open}
            onClick={() => setOpen((value) => !value)}
          >
            Menu
          </button>
          <div>
            <h1 className="page-kicker">{header.title}</h1>
            <p className="page-sub">{header.subtitle}</p>
          </div>
          <span className="topbar-pill" title="Read-only mode">
            Live API · Read-only
          </span>
        </header>

        <main className="content" id="main-content">
          <Outlet />
        </main>
      </div>

      {open ? (
        <button
          type="button"
          className="backdrop"
          aria-label="Close navigation menu"
          onClick={() => setOpen(false)}
        />
      ) : null}
    </div>
  )
}
