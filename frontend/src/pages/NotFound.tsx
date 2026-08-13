import { Link } from 'react-router-dom'

export function NotFoundPage() {
  return (
    <div className="not-found" role="status">
      <p className="eyebrow">404</p>
      <h2>Page not found</h2>
      <p className="muted">
        That route does not exist in the E STAR tracking dashboard.
      </p>
      <Link className="btn btn-primary" to="/">
        Return to Dashboard
      </Link>
    </div>
  )
}
