import { api } from './api'
import type {
  Campaign,
  CampaignListResponse,
  CampaignOpenEventListResponse,
  CampaignStats,
  EmailEventListResponse,
  OpenTimelineResponse,
  Recipient,
  RecipientListResponse,
} from '../types'

export async function fetchCampaigns(skip = 0, limit = 50): Promise<CampaignListResponse> {
  const { data } = await api.get<CampaignListResponse>('/api/campaigns', {
    params: { skip, limit },
  })
  return data
}

export async function fetchCampaign(campaignId: number): Promise<Campaign> {
  const { data } = await api.get<Campaign>(`/api/campaigns/${campaignId}`)
  return data
}

export async function fetchCampaignStats(campaignId: number): Promise<CampaignStats> {
  const { data } = await api.get<CampaignStats>(`/api/campaigns/${campaignId}/stats`)
  return data
}

export interface RecipientQueryParams {
  skip?: number
  limit?: number
  campaign_id?: number
  search?: string
  status?: 'PENDING' | 'SENT' | 'FAILED' | ''
  opened?: boolean | null
}

export async function fetchRecipients(
  params: RecipientQueryParams = {},
): Promise<RecipientListResponse> {
  const query: Record<string, string | number | boolean> = {
    skip: params.skip ?? 0,
    limit: params.limit ?? 50,
  }

  if (params.campaign_id) {
    query.campaign_id = params.campaign_id
  }
  if (params.search && params.search.trim()) {
    query.search = params.search.trim()
  }
  if (params.status) {
    query.status = params.status
  }
  if (params.opened === true || params.opened === false) {
    query.opened = params.opened
  }

  const { data } = await api.get<RecipientListResponse>('/api/recipients', {
    params: query,
  })
  return data
}

export async function fetchRecipient(recipientId: number): Promise<Recipient> {
  const { data } = await api.get<Recipient>(`/api/recipients/${recipientId}`)
  return data
}

export async function fetchCampaignAnalytics(campaignId: number): Promise<CampaignStats> {
  const { data } = await api.get<CampaignStats>(`/api/analytics/campaign/${campaignId}`)
  return data
}

export async function fetchRecipientAnalytics(recipientId: number): Promise<Recipient> {
  const { data } = await api.get<Recipient>(`/api/analytics/recipient/${recipientId}`)
  return data
}

export async function fetchRecipientEvents(
  recipientId: number,
  skip = 0,
  limit = 50,
): Promise<EmailEventListResponse> {
  const { data } = await api.get<EmailEventListResponse>(
    `/api/analytics/recipient/${recipientId}/events`,
    { params: { skip, limit } },
  )
  return data
}

export async function fetchCampaignOpens(
  campaignId: number,
  skip = 0,
  limit = 50,
): Promise<CampaignOpenEventListResponse> {
  const { data } = await api.get<CampaignOpenEventListResponse>(
    `/api/analytics/campaign/${campaignId}/opens`,
    { params: { skip, limit } },
  )
  return data
}

export async function fetchOpenTimeline(campaignId: number): Promise<OpenTimelineResponse> {
  const { data } = await api.get<OpenTimelineResponse>(
    `/api/analytics/campaign/${campaignId}/opens/timeline`,
  )
  return data
}
