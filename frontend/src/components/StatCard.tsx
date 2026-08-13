import { formatNumber, formatPercent } from '../utils/format'

type Accent = 'default' | 'accent' | 'success' | 'warn' | 'danger' | 'highlight'

interface StatCardProps {
  label: string
  value: number | string
  hint?: string
  icon?: string
  accent?: Accent
  featured?: boolean
  isPercent?: boolean
}

export function StatCard({
  label,
  value,
  hint,
  icon,
  accent = 'default',
  featured = false,
  isPercent,
}: StatCardProps) {
  const treatAsPercent = isPercent ?? label.toLowerCase().includes('rate')
  const display =
    typeof value === 'number'
      ? treatAsPercent
        ? formatPercent(value)
        : formatNumber(value)
      : value

  return (
    <article
      className={`stat-card accent-${accent}${featured ? ' featured' : ''}`}
      aria-label={`${label}: ${display}`}
    >
      <div className="stat-card-top">
        <p className="stat-label">{label}</p>
        {icon ? (
          <span className="stat-icon" aria-hidden="true">
            {icon}
          </span>
        ) : null}
      </div>
      <p className="stat-value">{display}</p>
      {hint ? <p className="stat-hint">{hint}</p> : null}
    </article>
  )
}
