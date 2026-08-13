import { Link } from 'react-router-dom'
import { ErrorState } from '../components/ErrorState'
import { LoadingState } from '../components/LoadingState'
import { OpensTimelineChart } from '../components/OpensTimelineChart'
import { PageHeader } from '../components/PageHeader'
import { StatCard } from '../components/StatCard'
import { StatusDistributionChart } from '../components/StatusDistributionChart'
import { useAsyncData } from '../hooks/useAsyncData'
import {
  fetchCampaign,
  fetchCampaignStats,
  fetchOpenTimeline,
} from '../services/campaigns'
import { formatDateTime, formatNumber, formatPercent } from '../utils/format'

const DEFAULT_CAMPAIGN_ID = 1

export function DashboardPage() {
  const campaignState = useAsyncData(
    () => fetchCampaign(DEFAULT_CAMPAIGN_ID),
    [DEFAULT_CAMPAIGN_ID],
    'Unable to load campaign data.',
  )
  const statsState = useAsyncData(
    () => fetchCampaignStats(DEFAULT_CAMPAIGN_ID),
    [DEFAULT_CAMPAIGN_ID],
    'Unable to load campaign data.',
  )
  const timelineState = useAsyncData(
    () => fetchOpenTimeline(DEFAULT_CAMPAIGN_ID),
    [DEFAULT_CAMPAIGN_ID],
    'Unable to load analytics.',
  )

  const loading = campaignState.loading || statsState.loading
  const error = campaignState.error || statsState.error

  if (loading) {
    return <LoadingState message="Loading dashboard..." />
  }

  if (error || !statsState.data || !campaignState.data) {
    return (
      <ErrorState
        message={error || 'Unable to load campaign data.'}
        onRetry={() => {
          campaignState.reload()
          statsState.reload()
          timelineState.reload()
        }}
      />
    )
  }

  const campaign = campaignState.data
  const stats = statsState.data

  return (
    <div className="page-stack">
      <PageHeader
        eyebrow="Dashboard"
        title={stats.name}
        description="Campaign analytics and recipient engagement overview. Metrics are tracked opens, not guaranteed human opens."
        actions={
          <>
            <button
              type="button"
              className="btn btn-secondary"
              onClick={() => {
                campaignState.reload()
                statsState.reload()
                timelineState.reload()
              }}
            >
              Refresh
            </button>
            <Link className="btn btn-primary" to={`/campaigns/${stats.campaign_id}`}>
              View campaign
            </Link>
            <Link className="btn btn-secondary" to="/analytics">
              Open analytics
            </Link>
          </>
        }
      />

      <section className="overview-strip" aria-label="Campaign overview">
        <div>
          <p className="strip-label">Subject</p>
          <p className="strip-value">{campaign.subject}</p>
        </div>
        <div>
          <p className="strip-label">Created</p>
          <p className="strip-value">{formatDateTime(campaign.created_at)}</p>
        </div>
        <div>
          <p className="strip-label">Recipients</p>
          <p className="strip-value">{formatNumber(stats.total_recipients)}</p>
        </div>
        <div>
          <p className="strip-label">Open rate</p>
          <p className="strip-value highlight">{formatPercent(stats.open_rate)}</p>
        </div>
      </section>

      <section className="stat-grid" aria-label="Key performance indicators">
        <StatCard
          label="Open Rate"
          value={stats.open_rate}
          hint="Tracked opens ÷ recipients"
          icon="%"
          accent="highlight"
          featured
          isPercent
        />
        <StatCard label="Total Recipients" value={stats.total_recipients} icon="R" accent="accent" />
        <StatCard label="Sent" value={stats.sent} icon="S" />
        <StatCard label="Pending" value={stats.pending} icon="P" accent="warn" />
        <StatCard label="Failed" value={stats.failed} icon="F" accent="danger" />
        <StatCard label="Delivered" value={stats.delivered} hint="delivered_at is set" icon="D" />
        <StatCard label="Unique Opened" value={stats.unique_opened} icon="U" accent="success" />
        <StatCard label="Total Opens" value={stats.total_opens} icon="O" accent="success" />
      </section>

      <section className="charts-grid">
        <article className="panel">
          <div className="panel-head">
            <h3>Opens over time</h3>
            <p className="muted">Tracked open events grouped by date</p>
          </div>
          {timelineState.loading ? (
            <LoadingState message="Loading analytics..." />
          ) : timelineState.error ? (
            <ErrorState message={timelineState.error} onRetry={timelineState.reload} />
          ) : (
            <OpensTimelineChart data={timelineState.data?.timeline ?? []} />
          )}
        </article>

        <article className="panel">
          <div className="panel-head">
            <h3>Send status</h3>
            <p className="muted">PENDING / SENT / FAILED from PostgreSQL</p>
          </div>
          <StatusDistributionChart stats={stats} />
        </article>
      </section>
    </div>
  )
}
