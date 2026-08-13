from sqlalchemy import Date, cast, func
from sqlalchemy.orm import Session

from backend.models import Campaign, EmailEvent, Recipient
from backend.schemas import (
    CampaignOpenEventItem,
    CampaignStatsResponse,
    EmailEventResponse,
    OpenTimelineItem,
    RecipientResponse,
)
from backend.services import campaign_service, recipient_service

DEFAULT_LIMIT = 50
MAX_LIMIT = 500


def _clamp_limit(limit: int) -> int:
    if limit < 1:
        return 1
    if limit > MAX_LIMIT:
        return MAX_LIMIT
    return limit


def get_campaign_analytics(
    db: Session,
    campaign_id: int,
) -> CampaignStatsResponse | None:
    return campaign_service.get_campaign_stats(db, campaign_id)


def get_recipient_analytics(
    db: Session,
    recipient_id: int,
) -> RecipientResponse | None:
    recipient = recipient_service.get_recipient_by_id(db, recipient_id)
    if recipient is None:
        return None
    return recipient_service.build_recipient_response(recipient)


def get_recipient_events(
    db: Session,
    recipient_id: int,
    skip: int = 0,
    limit: int = DEFAULT_LIMIT,
) -> tuple[list[EmailEvent], int] | None:
    recipient = recipient_service.get_recipient_by_id(db, recipient_id)
    if recipient is None:
        return None

    limit = _clamp_limit(limit)
    skip = max(skip, 0)

    query = db.query(EmailEvent).filter(EmailEvent.recipient_id == recipient_id)
    total = query.with_entities(func.count(EmailEvent.id)).scalar() or 0
    events = (
        query.order_by(EmailEvent.event_time.desc(), EmailEvent.id.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )
    return events, total


def get_campaign_open_events(
    db: Session,
    campaign_id: int,
    skip: int = 0,
    limit: int = DEFAULT_LIMIT,
) -> tuple[list[CampaignOpenEventItem], int] | None:
    campaign = db.query(Campaign).filter(Campaign.id == campaign_id).first()
    if campaign is None:
        return None

    limit = _clamp_limit(limit)
    skip = max(skip, 0)

    filters = (
        Recipient.campaign_id == campaign_id,
        EmailEvent.event_type == "OPENED",
    )

    total = (
        db.query(func.count(EmailEvent.id))
        .join(Recipient, Recipient.id == EmailEvent.recipient_id)
        .filter(*filters)
        .scalar()
        or 0
    )

    rows = (
        db.query(
            EmailEvent.id.label("event_id"),
            Recipient.id.label("recipient_id"),
            Recipient.name.label("recipient_name"),
            Recipient.email.label("recipient_email"),
            EmailEvent.event_type.label("event_type"),
            EmailEvent.event_time.label("event_time"),
            EmailEvent.ip_address.label("ip_address"),
            EmailEvent.user_agent.label("user_agent"),
        )
        .join(Recipient, Recipient.id == EmailEvent.recipient_id)
        .filter(*filters)
        .order_by(EmailEvent.event_time.desc(), EmailEvent.id.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )

    items = [
        CampaignOpenEventItem(
            event_id=row.event_id,
            recipient_id=row.recipient_id,
            recipient_name=row.recipient_name,
            recipient_email=row.recipient_email,
            event_type=row.event_type,
            event_time=row.event_time,
            ip_address=row.ip_address,
            user_agent=row.user_agent,
        )
        for row in rows
    ]
    return items, total


def get_campaign_opens_timeline(
    db: Session,
    campaign_id: int,
) -> list[OpenTimelineItem] | None:
    campaign = db.query(Campaign).filter(Campaign.id == campaign_id).first()
    if campaign is None:
        return None

    rows = (
        db.query(
            cast(EmailEvent.event_time, Date).label("open_date"),
            func.count(EmailEvent.id).label("opens"),
        )
        .join(Recipient, Recipient.id == EmailEvent.recipient_id)
        .filter(
            Recipient.campaign_id == campaign_id,
            EmailEvent.event_type == "OPENED",
        )
        .group_by(cast(EmailEvent.event_time, Date))
        .order_by(cast(EmailEvent.event_time, Date).asc())
        .all()
    )

    return [
        OpenTimelineItem(
            date=row.open_date.isoformat(),
            opens=int(row.opens or 0),
        )
        for row in rows
    ]


def to_email_event_response(event: EmailEvent) -> EmailEventResponse:
    return EmailEventResponse.model_validate(event)
