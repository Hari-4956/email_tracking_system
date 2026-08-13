export interface Recipient {
  id: number
  campaign_id: number
  name: string
  email: string
  tracking_token: string
  send_status: string
  sent_at: string | null
  delivered_at: string | null
  first_opened_at: string | null
  last_opened_at: string | null
  open_count: number
  retry_count: number
  last_error: string | null
  created_at: string
  tracking_url: string
}

export interface RecipientListResponse {
  total: number
  skip: number
  limit: number
  recipients: Recipient[]
}

export interface Campaign {
  id: number
  name: string
  subject: string
  created_at: string
  total_recipients: number
}

export interface CampaignListResponse {
  total: number
  skip: number
  limit: number
  campaigns: Campaign[]
}

export interface CampaignStats {
  campaign_id: number
  name: string
  subject: string
  total_recipients: number
  pending: number
  sent: number
  failed: number
  delivered: number
  opened: number
  unique_opened: number
  total_opens: number
  open_rate: number
}

export interface EmailEvent {
  id: number
  recipient_id: number
  event_type: string
  event_time: string
  ip_address: string | null
  user_agent: string | null
}

export interface EmailEventListResponse {
  recipient_id: number
  total: number
  skip: number
  limit: number
  events: EmailEvent[]
}

export interface CampaignOpenEvent {
  event_id: number
  recipient_id: number
  recipient_name: string
  recipient_email: string
  event_type: string
  event_time: string
  ip_address: string | null
  user_agent: string | null
}

export interface CampaignOpenEventListResponse {
  campaign_id: number
  total: number
  skip: number
  limit: number
  opens: CampaignOpenEvent[]
}

export interface TimelinePoint {
  date: string
  opens: number
}

export interface OpenTimelineResponse {
  campaign_id: number
  timeline: TimelinePoint[]
}
