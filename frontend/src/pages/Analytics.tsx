import { useState } from 'react'
import { Link } from 'react-router-dom'
import { EmptyState } from '../components/EmptyState'
import { ErrorState } from '../components/ErrorState'
import { LoadingState } from '../components/LoadingState'
import { OpensTimelineChart } from '../components/OpensTimelineChart'
import { PageHeader } from '../components/PageHeader'
import { Pagination } from '../components/Pagination'
import { StatCard } from '../components/StatCard'
import { StatusDistributionChart } from '../components/StatusDistributionChart'
import { useAsyncData } from '../hooks/useAsyncData'
import {
  fetchCampaignAnalytics,
  fetchCampaignOpens,
  fetchOpenTimeline,
} from '../services/campaigns'
import { formatDateTime, formatNumber } from '../utils/format'

const DEFAULT_CAMPAIGN_ID = 1
const OPENS_PAGE_SIZE = 25

export function AnalyticsPage() {
  const [opensSkip, setOpensSkip] = useState(0)

  const statsState = useAsyncData(
    () => fetchCampaignAnalytics(DEFAULT_CAMPAIGN_ID),
    [DEFAULT_CAMPAIGN_ID],
    'Unable to load analytics.',
  )
  const timelineState = useAsyncData(
    () => fetchOpenTimeline(DEFAULT_CAMPAIGN_ID),
    [DEFAULT_CAMPAIGN_ID],
    'Unable to load analytics.',
  )
  const opensState = useAsyncData(
    () => fetchCampaignOpens(DEFAULT_CAMPAIGN_ID, opensSkip, OPENS_PAGE_SIZE),
    [DEFAULT_CAMPAIGN_ID, opensSkip],
    'Unable to load analytics.',
  )

  if (statsState.loading) {
    return <LoadingState message="Loading analytics..." />
  }

  if (statsState.error || !statsState.data) {
    return (
      <ErrorState
        message={statsState.error || 'Unable to load analytics.'}
        onRetry={statsState.reload}
      />
    )
  }

  const stats = statsState.data

  return (
    <div className="page-stack">
      <PageHeader
        eyebrow="Analytics"
        title={stats.name}
        description="Tracked opens only — privacy scanners and image blocking can affect accuracy."
        actions={
          <button
            type="button"
            className="btn btn-secondary"
            onClick={() => {
              statsState.reload()
              timelineState.reload()
              opensState.reload()
            }}
          >
            Refresh
          </button>
        }
      />

      <section className="stat-grid" aria-label="Analytics KPIs">
        <StatCard label="Open Rate" value={stats.open_rate} featured accent="highlight" isPercent icon="%" />
        <StatCard label="Total Recipients" value={stats.total_recipients} accent="accent" icon="R" />
        <StatCard label="Unique Opens" value={stats.unique_opened} accent="success" icon="U" />
        <StatCard label="Total Opens" value={stats.total_opens} accent="success" icon="O" />
        <StatCard label="Sent" value={stats.sent} icon="S" />
        <StatCard label="Pending" value={stats.pending} accent="warn" icon="P" />
        <StatCard label="Failed" value={stats.failed} accent="danger" icon="F" />
        <StatCard label="Delivered" value={stats.delivered} icon="D" />
      </section>

      <section className="charts-grid">
        <article className="panel">
          <div className="panel-head">
            <h3>Open timeline</h3>
            <p className="muted">Daily tracked open volume</p>
          </div>
          {timelineState.loading ? (
            <LoadingState message="Loading timeline..." />
          ) : timelineState.error ? (
            <ErrorState message={timelineState.error} onRetry={timelineState.reload} />
          ) : (
            <OpensTimelineChart data={timelineState.data?.timeline ?? []} />
          )}
        </article>

        <article className="panel">
          <div className="panel-head">
            <h3>Send status distribution</h3>
            <p className="muted">Based on recipient send_status</p>
          </div>
          <StatusDistributionChart stats={stats} />
        </article>
      </section>

      <section className="panel table-panel">
        <div className="panel-head">
          <h3>Campaign open events</h3>
          <p className="muted">
            Paginated event feed · {formatNumber(opensState.data?.total ?? 0)} total opens logged
          </p>
        </div>

        {opensState.loading ? <LoadingState message="Loading opens..." /> : null}
        {opensState.error ? <ErrorState message={opensState.error} onRetry={opensState.reload} /> : null}

        {!opensState.loading && !opensState.error && opensState.data ? (
          opensState.data.opens.length === 0 ? (
            <EmptyState title="No open activity yet." description="No OPENED events for this campaign." />
          ) : (
            <>
              <div className="table-scroll">
                <table>
                  <thead>
                    <tr>
                      <th scope="col">Event ID</th>
                      <th scope="col">Recipient</th>
                      <th scope="col">Email</th>
                      <th scope="col">Type</th>
                      <th scope="col">Time</th>
                      <th scope="col">IP</th>
                      <th scope="col">User Agent</th>
                    </tr>
                  </thead>
                  <tbody>
                    {opensState.data.opens.map((item) => (
                      <tr key={item.event_id}>
                        <td>{item.event_id}</td>
                        <td>
                          <Link className="table-link" to={`/recipients/${item.recipient_id}`}>
                            {item.recipient_name}
                          </Link>
                        </td>
                        <td>
                          <span className="email-cell" title={item.recipient_email}>
                            {item.recipient_email}
                          </span>
                        </td>
                        <td>{item.event_type}</td>
                        <td>{formatDateTime(item.event_time)}</td>
                        <td>{item.ip_address || '—'}</td>
                        <td className="ua-cell">{item.user_agent || '—'}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
              <Pagination
                skip={opensSkip}
                limit={OPENS_PAGE_SIZE}
                total={opensState.data.total}
                onChange={setOpensSkip}
              />
            </>
          )
        ) : null}
      </section>
    </div>
  )
}
