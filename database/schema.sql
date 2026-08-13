-- Documentation / reference schema for E STAR Email Tracking System.
-- IMPORTANT:
-- Do NOT run DROP / TRUNCATE against production data.
-- Existing PostgreSQL tables already contain live campaign data.
-- Prefer CREATE TABLE IF NOT EXISTS / CREATE INDEX IF NOT EXISTS.

-- campaigns
CREATE TABLE IF NOT EXISTS campaigns (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    subject VARCHAR(500) NOT NULL,
    created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    total_recipients INTEGER DEFAULT 0
);

-- recipients
CREATE TABLE IF NOT EXISTS recipients (
    id SERIAL PRIMARY KEY,
    campaign_id INTEGER NOT NULL REFERENCES campaigns(id),
    name VARCHAR(255) NOT NULL,
    email VARCHAR(320) NOT NULL,
    tracking_token VARCHAR(36) NOT NULL UNIQUE,
    send_status VARCHAR(50) NOT NULL DEFAULT 'PENDING',
    sent_at TIMESTAMP WITHOUT TIME ZONE NULL,
    delivered_at TIMESTAMP WITHOUT TIME ZONE NULL,
    first_opened_at TIMESTAMP WITHOUT TIME ZONE NULL,
    last_opened_at TIMESTAMP WITHOUT TIME ZONE NULL,
    open_count INTEGER NOT NULL DEFAULT 0,
    retry_count INTEGER NOT NULL DEFAULT 0,
    last_error TEXT NULL,
    created_at TIMESTAMP WITHOUT TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT uq_campaign_recipient_email UNIQUE (campaign_id, email)
);

-- email_events
CREATE TABLE IF NOT EXISTS email_events (
    id SERIAL PRIMARY KEY,
    recipient_id INTEGER NOT NULL REFERENCES recipients(id),
    event_type VARCHAR(50) NOT NULL,
    event_time TIMESTAMP WITHOUT TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    ip_address VARCHAR(45) NULL,
    user_agent TEXT NULL
);
