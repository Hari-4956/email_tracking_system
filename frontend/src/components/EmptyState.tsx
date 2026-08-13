interface EmptyStateProps {
  title: string
  description?: string
}

export function EmptyState({ title, description }: EmptyStateProps) {
  return (
    <div className="state-panel state-empty">
      <p className="empty-title">{title}</p>
      {description ? <p className="empty-desc">{description}</p> : null}
    </div>
  )
}
