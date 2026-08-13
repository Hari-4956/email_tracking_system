interface StatusBadgeProps {
  status: string
}

export function StatusBadge({ status }: StatusBadgeProps) {
  const normalized = (status || 'UNKNOWN').toUpperCase()
  const tone =
    normalized === 'SENT'
      ? 'sent'
      : normalized === 'FAILED'
        ? 'failed'
        : normalized === 'DELIVERED'
          ? 'delivered'
          : normalized === 'PENDING'
            ? 'pending'
            : 'neutral'

  return <span className={`status-badge status-${tone}`}>{normalized}</span>
}
