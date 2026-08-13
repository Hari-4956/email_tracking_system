import { useState } from 'react'
import { Link, useParams } from 'react-router-dom'
import { EmptyState } from '../components/EmptyState'
import { ErrorState } from '../components/ErrorState'
import { LoadingState } from '../components/LoadingState'
import { OpenBadge } from '../components/OpenBadge'
import { PageHeader } from '../components/PageHeader'
import { Pagination } from '../components/Pagination'
import { StatusBadge } from '../components/StatusBadge'
import { useAsyncData } from '../hooks/useAsyncData'
import { fetchRecipient, fetchRecipientEvents } from '../services/campaigns'
import { formatDateTime, formatNumber } from '../utils/format'

const EVENT_PAGE_SIZE = 20

export function RecipientDetailsPage() {
  const params = useParams()
  const recipientId = Number(params.recipientId)
  const [eventSkip, setEventSkip] = useState(0)

  const recipientState = useAsyncData(
    () => fetchRecipient(recipientId),
    [recipientId],
    'Unable to load recipients.',
  )

  const eventsState = useAsyncData(
    () => fetchRecipientEvents(recipientId, eventSkip, EVENT_PAGE_SIZE),
    [recipientId, eventSkip],
    'Unable to load analytics.',
  )

  if (!Number.isFinite(recipientId) || recipientId < 1) {
    return <ErrorState message="Invalid recipient ID." />
  }

  if (recipientState.loading) {
    return <LoadingState message="Loading recipient..." />
  }

  if (recipientState.error || !recipientState.data) {
    return (
      <ErrorState
        message={recipientState.error || 'Unable to load recipients.'}
        onRetry={recipientState.reload}
      />
    )
  }

  const recipient = recipientState.data

  return (
    <div className="page-stack">
      <PageHeader
        eyebrow={`Recipient ${recipient.id}`}
        title={recipient.name}
        description={recipient.email}
        actions={
          <>
            <button type="button" className="btn btn-secondary" onClick={recipientState.reload}>
              Refresh
            </button>
            <Link className="btn btn-secondary" to="/recipients">
              Back to recipients
            </Link>
          </>
        }
      />

      <section className="detail-grid">
        <div className="detail-card">
          <div className="detail-card-head">
            <h3>Profile</h3>
            <div className="detail-badges">
              <StatusBadge status={recipient.send_status} />
              <OpenBadge firstOpenedAt={recipient.first_opened_at} />
            </div>
          </div>
          <dl className="detail-list">
            <div>
              <dt>Campaign</dt>
              <dd>
                <Link className="table-link" to={`/campaigns/${recipient.campaign_id}`}>
                  Campaign {recipient.campaign_id}
                </Link>
              </dd>
            </div>
            <div>
              <dt>Email</dt>
              <dd>
                <span className="email-cell" title={recipient.email}>
                  {recipient.email}
                </span>
              </dd>
            </div>
            <div>
              <dt>Sent At</dt>
              <dd>{formatDateTime(recipient.sent_at)}</dd>
            </div>
            <div>
              <dt>Delivered At</dt>
              <dd>{formatDateTime(recipient.delivered_at)}</dd>
            </div>
            <div>
              <dt>First Opened</dt>
              <dd>{formatDateTime(recipient.first_opened_at)}</dd>
            </div>
            <div>
              <dt>Last Opened</dt>
              <dd>{formatDateTime(recipient.last_opened_at)}</dd>
            </div>
            <div>
              <dt>Open Count</dt>
              <dd>{formatNumber(recipient.open_count)}</dd>
            </div>
            <div>
              <dt>Retry Count</dt>
              <dd>{formatNumber(recipient.retry_count)}</dd>
            </div>
            <div>
              <dt>Created At</dt>
              <dd>{formatDateTime(recipient.created_at)}</dd>
            </div>
            <div>
              <dt>Tracking URL</dt>
              <dd>
                <a
                  className="table-link break-link"
                  href={recipient.tracking_url}
                  target="_blank"
                  rel="noreferrer"
                >
                  {recipient.tracking_url}
                </a>
              </dd>
            </div>
          </dl>
        </div>
      </section>

      <section className="panel table-panel">
        <div className="panel-head">
          <h3>Event history</h3>
          <p className="muted">Paginated open events for this recipient</p>
        </div>

        {eventsState.loading ? <LoadingState message="Loading events..." /> : null}
        {eventsState.error ? (
          <ErrorState message={eventsState.error} onRetry={eventsState.reload} />
        ) : null}

        {!eventsState.loading && !eventsState.error && eventsState.data ? (
          eventsState.data.events.length === 0 ? (
            <EmptyState
              title="No events"
              description="No email events recorded for this recipient yet."
            />
          ) : (
            <>
              <div className="table-scroll">
                <table>
                  <thead>
                    <tr>
                      <th scope="col">Event Type</th>
                      <th scope="col">Event Time</th>
                      <th scope="col">IP Address</th>
                      <th scope="col">User Agent</th>
                    </tr>
                  </thead>
                  <tbody>
                    {eventsState.data.events.map((event) => (
                      <tr key={event.id}>
                        <td>{event.event_type}</td>
                        <td>{formatDateTime(event.event_time)}</td>
                        <td>{event.ip_address || '—'}</td>
                        <td className="ua-cell">{event.user_agent || '—'}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
              <Pagination
                skip={eventSkip}
                limit={EVENT_PAGE_SIZE}
                total={eventsState.data.total}
                onChange={setEventSkip}
              />
            </>
          )
        ) : null}
      </section>
    </div>
  )
}
