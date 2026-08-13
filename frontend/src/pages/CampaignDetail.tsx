import { Link, useParams } from 'react-router-dom'
import { ErrorState } from '../components/ErrorState'
import { LoadingState } from '../components/LoadingState'
import { OpensTimelineChart } from '../components/OpensTimelineChart'
import { PageHeader } from '../components/PageHeader'
import { StatCard } from '../components/StatCard'
import { StatusDistributionChart } from '../components/StatusDistributionChart'
import { useAsyncData } from '../hooks/useAsyncData'
import { fetchCampaign, fetchCampaignStats, fetchOpenTimeline } from '../services/campaigns'
import { formatDateTime, formatNumber } from '../utils/format'

export function CampaignDetailPage() {
  const params = useParams()
  const campaignId = Number(params.campaignId)

  const campaignState = useAsyncData(
    () => fetchCampaign(campaignId),
    [campaignId],
    'Unable to load campaign data.',
  )
  const statsState = useAsyncData(
    () => fetchCampaignStats(campaignId),
    [campaignId],
    'Unable to load campaign data.',
  )
  const timelineState = useAsyncData(
    () => fetchOpenTimeline(campaignId),
    [campaignId],
    'Unable to load analytics.',
  )

  if (!Number.isFinite(campaignId) || campaignId < 1) {
    return <ErrorState message="Invalid campaign ID." />
  }

  if (campaignState.loading || statsState.loading) {
    return <LoadingState message="Loading campaign..." />
  }

  if (campaignState.error || !campaignState.data) {
    return (
      <ErrorState
        message={campaignState.error || 'Unable to load campaign data.'}
        onRetry={campaignState.reload}
      />
    )
  }

  if (statsState.error || !statsState.data) {
    return (
      <ErrorState
        message={statsState.error || 'Unable to load campaign data.'}
        onRetry={statsState.reload}
      />
    )
  }

  const campaign = campaignState.data
  const stats = statsState.data

  return (
    <div className="page-stack">
      <PageHeader
        eyebrow={`Campaign ${campaign.id}`}
        title={campaign.name}
        description={`${campaign.subject} · Created ${formatDateTime(campaign.created_at)} · ${formatNumber(stats.total_recipients)} recipients`}
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
            <Link className="btn btn-secondary" to="/campaigns">
              Back to campaigns
            </Link>
            <Link className="btn btn-primary" to="/analytics">
              Analytics
            </Link>
          </>
        }
      />

      <section className="stat-grid" aria-label="Campaign KPIs">
        <StatCard label="Open Rate" value={stats.open_rate} featured accent="highlight" isPercent icon="%" />
        <StatCard label="Total Recipients" value={stats.total_recipients} accent="accent" icon="R" />
        <StatCard label="Sent" value={stats.sent} icon="S" />
        <StatCard label="Pending" value={stats.pending} accent="warn" icon="P" />
        <StatCard label="Failed" value={stats.failed} accent="danger" icon="F" />
        <StatCard label="Delivered" value={stats.delivered} icon="D" />
        <StatCard label="Opened" value={stats.opened} accent="success" icon="U" />
        <StatCard label="Total Opens" value={stats.total_opens} accent="success" icon="O" />
      </section>

      <section className="charts-grid">
        <article className="panel">
          <div className="panel-head">
            <h3>Opens timeline</h3>
            <p className="muted">Daily tracked opens</p>
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
            <p className="muted">PENDING / SENT / FAILED</p>
          </div>
          <StatusDistributionChart stats={stats} />
        </article>
      </section>
    </div>
  )
}
