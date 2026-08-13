-- Safe index documentation for E STAR Email Tracking System.
-- Use CREATE INDEX IF NOT EXISTS only.
-- Do NOT drop existing indexes or tables.

-- recipients
CREATE INDEX IF NOT EXISTS ix_recipients_campaign_id
    ON recipients (campaign_id);

CREATE INDEX IF NOT EXISTS ix_recipients_email
    ON recipients (email);

CREATE INDEX IF NOT EXISTS ix_recipients_tracking_token
    ON recipients (tracking_token);

CREATE INDEX IF NOT EXISTS ix_recipients_send_status
    ON recipients (send_status);

CREATE INDEX IF NOT EXISTS ix_recipients_campaign_send_status
    ON recipients (campaign_id, send_status);

CREATE INDEX IF NOT EXISTS ix_recipients_first_opened_at
    ON recipients (first_opened_at);

-- Optional note for Phase 6A search:
-- Current search uses parameterized ILIKE on name/email/tracking_token.
-- For 71k rows this is acceptable without full-text search infrastructure.
-- If search latency becomes an issue later, consider trigram indexes
-- (pg_trgm) rather than loading rows into application memory.

-- email_events
CREATE INDEX IF NOT EXISTS ix_email_events_recipient_id
    ON email_events (recipient_id);

CREATE INDEX IF NOT EXISTS ix_email_events_event_time
    ON email_events (event_time);

CREATE INDEX IF NOT EXISTS ix_email_events_event_type
    ON email_events (event_type);

CREATE INDEX IF NOT EXISTS ix_email_events_type_time
    ON email_events (event_type, event_time);
