import { useEffect, useMemo, useState } from 'react'
import { Link, useSearchParams } from 'react-router-dom'
import { EmptyState } from '../components/EmptyState'
import { ErrorState } from '../components/ErrorState'
import { LoadingState } from '../components/LoadingState'
import { OpenBadge } from '../components/OpenBadge'
import { PageHeader } from '../components/PageHeader'
import { Pagination } from '../components/Pagination'
import { StatusBadge } from '../components/StatusBadge'
import { useAsyncData } from '../hooks/useAsyncData'
import { useDebouncedValue } from '../hooks/useDebouncedValue'
import { fetchCampaigns, fetchRecipients } from '../services/campaigns'
import { formatDateTime, formatNumber } from '../utils/format'

const PAGE_SIZE = 50

function parseOpened(value: string | null): boolean | null {
  if (value === 'true') return true
  if (value === 'false') return false
  return null
}

export function RecipientsPage() {
  const [searchParams, setSearchParams] = useSearchParams()

  const [searchInput, setSearchInput] = useState(searchParams.get('search') ?? '')
  const debouncedSearch = useDebouncedValue(searchInput, 400)

  const status = (searchParams.get('status') ?? '') as '' | 'PENDING' | 'SENT' | 'FAILED'
  const opened = parseOpened(searchParams.get('opened'))
  const campaignParam = searchParams.get('campaign_id')
  const campaignId = campaignParam ? Number(campaignParam) : undefined
  const page = Math.max(1, Number(searchParams.get('page') ?? '1') || 1)
  const skip = (page - 1) * PAGE_SIZE

  const campaignsState = useAsyncData(
    () => fetchCampaigns(0, 50),
    [],
    'Unable to load campaign data.',
  )

  const queryKey = useMemo(
    () => ({
      skip,
      search: debouncedSearch.trim(),
      status,
      opened,
      campaign_id: Number.isFinite(campaignId) && (campaignId ?? 0) >= 1 ? campaignId : undefined,
    }),
    [skip, debouncedSearch, status, opened, campaignId],
  )

  const { data, loading, error, reload } = useAsyncData(
    () =>
      fetchRecipients({
        skip: queryKey.skip,
        limit: PAGE_SIZE,
        search: queryKey.search || undefined,
        status: queryKey.status || undefined,
        opened: queryKey.opened,
        campaign_id: queryKey.campaign_id,
      }),
    [queryKey.skip, queryKey.search, queryKey.status, queryKey.opened, queryKey.campaign_id],
    'Unable to load recipients.',
  )

  useEffect(() => {
    setSearchParams(
      (prev) => {
        const current = prev.get('search') ?? ''
        const nextSearch = debouncedSearch.trim()
        if (current === nextSearch) return prev

        const next = new URLSearchParams(prev)
        if (nextSearch) next.set('search', nextSearch)
        else next.delete('search')
        next.set('page', '1')
        return next
      },
      { replace: true },
    )
  }, [debouncedSearch, setSearchParams])

  function updateParams(mutator: (params: URLSearchParams) => void) {
    const next = new URLSearchParams(searchParams)
    mutator(next)
    setSearchParams(next, { replace: true })
  }

  function clearFilters() {
    setSearchInput('')
    setSearchParams(new URLSearchParams(), { replace: true })
  }

  const hasFilters = Boolean(
    searchInput.trim() || status || opened !== null || queryKey.campaign_id,
  )

  return (
    <div className="page-stack">
      <PageHeader
        eyebrow="Recipients"
        title="Recipient directory"
        description={`Server-side search and filters via FastAPI. Page size ${PAGE_SIZE} (backend max 500).`}
        actions={
          <button type="button" className="btn btn-secondary" onClick={reload}>
            Refresh
          </button>
        }
      />

      <section className="panel filters-panel" aria-label="Recipient filters">
        <div className="filters-grid">
          <label className="filter-field">
            <span>Search</span>
            <input
              type="search"
              placeholder="Search name, email, or tracking token…"
              value={searchInput}
              onChange={(event) => setSearchInput(event.target.value)}
              aria-label="Search recipients"
            />
          </label>

          <label className="filter-field">
            <span>Send status</span>
            <select
              value={status}
              aria-label="Filter by send status"
              onChange={(event) =>
                updateParams((params) => {
                  const value = event.target.value
                  if (value) params.set('status', value)
                  else params.delete('status')
                  params.set('page', '1')
                })
              }
            >
              <option value="">All statuses</option>
              <option value="PENDING">PENDING</option>
              <option value="SENT">SENT</option>
              <option value="FAILED">FAILED</option>
            </select>
          </label>

          <label className="filter-field">
            <span>Open status</span>
            <select
              value={opened === null ? '' : opened ? 'true' : 'false'}
              aria-label="Filter by open status"
              onChange={(event) =>
                updateParams((params) => {
                  const value = event.target.value
                  if (value) params.set('opened', value)
                  else params.delete('opened')
                  params.set('page', '1')
                })
              }
            >
              <option value="">All</option>
              <option value="true">Opened</option>
              <option value="false">Not opened</option>
            </select>
          </label>

          <label className="filter-field">
            <span>Campaign</span>
            <select
              value={queryKey.campaign_id ? String(queryKey.campaign_id) : ''}
              aria-label="Filter by campaign"
              onChange={(event) =>
                updateParams((params) => {
                  const value = event.target.value
                  if (value) params.set('campaign_id', value)
                  else params.delete('campaign_id')
                  params.set('page', '1')
                })
              }
            >
              <option value="">All campaigns</option>
              {(campaignsState.data?.campaigns ?? []).map((campaign) => (
                <option key={campaign.id} value={campaign.id}>
                  {campaign.id} · {campaign.name}
                </option>
              ))}
            </select>
          </label>
        </div>

        <div className="filters-actions">
          <button type="button" className="btn btn-secondary" onClick={clearFilters} disabled={!hasFilters}>
            Clear Filters
          </button>
          {data ? (
            <span className="muted">
              {formatNumber(data.total)} matching recipient{data.total === 1 ? '' : 's'}
            </span>
          ) : null}
        </div>
      </section>

      {error ? <ErrorState message={error} onRetry={reload} /> : null}

      <section className="panel table-panel">
        {loading ? <LoadingState message="Loading recipients..." /> : null}

        {!loading && !error && data ? (
          data.recipients.length === 0 ? (
            <EmptyState
              title="No recipients found."
              description={
                hasFilters
                  ? 'No recipients match your filters. Try a different search or clear filters.'
                  : 'No recipients are available.'
              }
            />
          ) : (
            <>
              <div className="table-scroll">
                <table>
                  <thead>
                    <tr>
                      <th scope="col">ID</th>
                      <th scope="col">Name</th>
                      <th scope="col">Email</th>
                      <th scope="col">Status</th>
                      <th scope="col">Opened</th>
                      <th scope="col">Open Count</th>
                      <th scope="col">First Opened</th>
                      <th scope="col">Last Opened</th>
                    </tr>
                  </thead>
                  <tbody>
                    {data.recipients.map((recipient) => (
                      <tr key={recipient.id}>
                        <td>
                          <Link className="table-link" to={`/recipients/${recipient.id}`}>
                            {recipient.id}
                          </Link>
                        </td>
                        <td>{recipient.name}</td>
                        <td>
                          <span className="email-cell" title={recipient.email}>
                            {recipient.email}
                          </span>
                        </td>
                        <td>
                          <StatusBadge status={recipient.send_status} />
                        </td>
                        <td>
                          <OpenBadge firstOpenedAt={recipient.first_opened_at} />
                        </td>
                        <td>{formatNumber(recipient.open_count)}</td>
                        <td>{formatDateTime(recipient.first_opened_at)}</td>
                        <td>{formatDateTime(recipient.last_opened_at)}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
              <Pagination
                skip={skip}
                limit={PAGE_SIZE}
                total={data.total}
                onChange={(nextSkip) =>
                  updateParams((params) => {
                    params.set('page', String(Math.floor(nextSkip / PAGE_SIZE) + 1))
                  })
                }
              />
            </>
          )
        ) : null}
      </section>
    </div>
  )
}
