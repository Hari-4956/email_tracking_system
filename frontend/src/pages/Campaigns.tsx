import { Link } from 'react-router-dom'
import { EmptyState } from '../components/EmptyState'
import { ErrorState } from '../components/ErrorState'
import { LoadingState } from '../components/LoadingState'
import { PageHeader } from '../components/PageHeader'
import { useAsyncData } from '../hooks/useAsyncData'
import { fetchCampaigns } from '../services/campaigns'
import { formatDateTime, formatNumber } from '../utils/format'

export function CampaignsPage() {
  const { data, loading, error, reload } = useAsyncData(
    () => fetchCampaigns(0, 50),
    [],
    'Unable to load campaign data.',
  )

  if (loading) return <LoadingState message="Loading campaigns..." />
  if (error || !data) {
    return <ErrorState message={error || 'Unable to load campaign data.'} onRetry={reload} />
  }

  if (!data.campaigns.length) {
    return (
      <EmptyState
        title="No campaigns"
        description="Campaigns appear after import into PostgreSQL."
      />
    )
  }

  return (
    <div className="page-stack">
      <PageHeader
        eyebrow="Campaigns"
        title="All campaigns"
        description={`${formatNumber(data.total)} campaign(s) loaded from FastAPI`}
        actions={
          <button type="button" className="btn btn-secondary" onClick={reload}>
            Refresh
          </button>
        }
      />

      <section className="campaign-grid" aria-label="Campaign list">
        {data.campaigns.map((campaign) => (
          <article key={campaign.id} className="campaign-card">
            <div className="campaign-card-top">
              <span className="campaign-id">#{campaign.id}</span>
              <Link className="btn btn-secondary btn-small" to={`/campaigns/${campaign.id}`}>
                Open
              </Link>
            </div>
            <h3>
              <Link className="table-link" to={`/campaigns/${campaign.id}`}>
                {campaign.name}
              </Link>
            </h3>
            <p className="muted campaign-subject" title={campaign.subject}>
              {campaign.subject}
            </p>
            <dl className="campaign-meta">
              <div>
                <dt>Created</dt>
                <dd>{formatDateTime(campaign.created_at)}</dd>
              </div>
              <div>
                <dt>Recipients</dt>
                <dd>{formatNumber(campaign.total_recipients)}</dd>
              </div>
            </dl>
          </article>
        ))}
      </section>
    </div>
  )
}
