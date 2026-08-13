interface PaginationProps {
  skip: number
  limit: number
  total: number
  onChange: (skip: number) => void
}

export function Pagination({ skip, limit, total, onChange }: PaginationProps) {
  const page = Math.floor(skip / limit) + 1
  const totalPages = Math.max(1, Math.ceil(total / limit))
  const canPrev = skip > 0
  const canNext = skip + limit < total

  return (
    <div className="pagination">
      <button
        type="button"
        className="btn btn-secondary"
        disabled={!canPrev}
        onClick={() => onChange(Math.max(0, skip - limit))}
      >
        Previous
      </button>
      <span className="pagination-meta">
        Page {page} of {totalPages} · {total.toLocaleString()} total
      </span>
      <button
        type="button"
        className="btn btn-secondary"
        disabled={!canNext}
        onClick={() => onChange(skip + limit)}
      >
        Next
      </button>
    </div>
  )
}
