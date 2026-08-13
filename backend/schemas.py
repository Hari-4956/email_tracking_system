from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class RecipientResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    campaign_id: int
    name: str
    email: str
    tracking_token: str
    send_status: str
    sent_at: Optional[datetime] = None
    delivered_at: Optional[datetime] = None
    first_opened_at: Optional[datetime] = None
    last_opened_at: Optional[datetime] = None
    open_count: int
    retry_count: int
    last_error: Optional[str] = None
    created_at: datetime
    tracking_url: str


# Alias used by analytics docs / consumers
RecipientAnalyticsResponse = RecipientResponse


class RecipientListResponse(BaseModel):
    total: int
    skip: int
    limit: int
    recipients: list[RecipientResponse]


class CampaignResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    subject: str
    created_at: datetime
    total_recipients: int


class CampaignListResponse(BaseModel):
    total: int
    skip: int
    limit: int
    campaigns: list[CampaignResponse]


class CampaignStatsResponse(BaseModel):
    campaign_id: int
    name: str
    subject: str
    total_recipients: int
    pending: int
    sent: int
    failed: int
    delivered: int
    opened: int
    unique_opened: int
    total_opens: int
    open_rate: float


class RecipientStatsResponse(BaseModel):
    recipient_id: int
    email: str
    send_status: str
    open_count: int
    first_opened_at: Optional[datetime] = None
    last_opened_at: Optional[datetime] = None
    tracking_url: str


class EmailEventResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    recipient_id: int
    event_type: str
    event_time: datetime
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None


class EmailEventListResponse(BaseModel):
    recipient_id: int
    total: int
    skip: int
    limit: int
    events: list[EmailEventResponse]


class CampaignOpenEventItem(BaseModel):
    event_id: int
    recipient_id: int
    recipient_name: str
    recipient_email: str
    event_type: str
    event_time: datetime
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None


class CampaignOpenEventListResponse(BaseModel):
    campaign_id: int
    total: int
    skip: int
    limit: int
    opens: list[CampaignOpenEventItem]


class OpenTimelineItem(BaseModel):
    date: str
    opens: int


class OpenTimelineResponse(BaseModel):
    campaign_id: int
    timeline: list[OpenTimelineItem]


class TestRecipientResponse(BaseModel):
    status: str
    recipient: Optional[RecipientResponse] = None
    message: Optional[str] = None


class PaginationParams(BaseModel):
    skip: int = Field(default=0, ge=0)
    limit: int = Field(default=50, ge=1, le=500)
