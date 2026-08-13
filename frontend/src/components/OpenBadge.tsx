interface OpenBadgeProps {
  firstOpenedAt: string | null | undefined
}

export function OpenBadge({ firstOpenedAt }: OpenBadgeProps) {
  const opened = Boolean(firstOpenedAt)
  return (
    <span className={`open-badge ${opened ? 'opened' : 'not-opened'}`}>
      {opened ? 'Opened' : 'Not Opened'}
    </span>
  )
}
