from sqlalchemy import case, func
from sqlalchemy.orm import Session

from backend.models import Campaign, Recipient
from backend.schemas import CampaignResponse, CampaignStatsResponse

DEFAULT_LIMIT = 50
MAX_LIMIT = 500


def _clamp_limit(limit: int) -> int:
    if limit < 1:
        return 1
    if limit > MAX_LIMIT:
        return MAX_LIMIT
    return limit


def sync_campaign_total_recipients(db: Session, campaign: Campaign) -> Campaign:
    """
    Align campaigns.total_recipients with the live COUNT(*) of recipients.
    Does not create or restore recipients.
    """
    actual_count = (
        db.query(func.count(Recipient.id))
        .filter(Recipient.campaign_id == campaign.id)
        .scalar()
        or 0
    )

    if campaign.total_recipients != actual_count:
        campaign.total_recipients = actual_count
        db.add(campaign)
        try:
            db.commit()
            db.refresh(campaign)
        except Exception:
            db.rollback()
            raise

    return campaign


def get_campaigns(
    db: Session,
    skip: int = 0,
    limit: int = DEFAULT_LIMIT,
) -> tuple[list[Campaign], int]:
    limit = _clamp_limit(limit)
    skip = max(skip, 0)

    total = db.query(func.count(Campaign.id)).scalar() or 0
    campaigns = (
        db.query(Campaign)
        .order_by(Campaign.id.asc())
        .offset(skip)
        .limit(limit)
        .all()
    )
    return campaigns, total


def get_campaign_by_id(
    db: Session,
    campaign_id: int,
    *,
    sync_total: bool = True,
) -> Campaign | None:
    campaign = db.query(Campaign).filter(Campaign.id == campaign_id).first()
    if campaign is None:
        return None

    if sync_total:
        campaign = sync_campaign_total_recipients(db, campaign)

    return campaign


def get_campaign_stats(db: Session, campaign_id: int) -> CampaignStatsResponse | None:
    campaign = get_campaign_by_id(db, campaign_id, sync_total=True)
    if campaign is None:
        return None

    row = (
        db.query(
            func.count(Recipient.id).label("total_recipients"),
            func.coalesce(
                func.sum(case((Recipient.send_status == "PENDING", 1), else_=0)),
                0,
            ).label("pending"),
            func.coalesce(
                func.sum(case((Recipient.send_status == "SENT", 1), else_=0)),
                0,
            ).label("sent"),
            func.coalesce(
                func.sum(case((Recipient.send_status == "FAILED", 1), else_=0)),
                0,
            ).label("failed"),
            func.coalesce(
                func.sum(case((Recipient.delivered_at.isnot(None), 1), else_=0)),
                0,
            ).label("delivered"),
            func.coalesce(
                func.sum(case((Recipient.first_opened_at.isnot(None), 1), else_=0)),
                0,
            ).label("opened"),
            func.coalesce(func.sum(Recipient.open_count), 0).label("total_opens"),
        )
        .filter(Recipient.campaign_id == campaign_id)
        .one()
    )

    total_recipients = int(row.total_recipients or 0)
    pending = int(row.pending or 0)
    sent = int(row.sent or 0)
    failed = int(row.failed or 0)
    delivered = int(row.delivered or 0)
    opened = int(row.opened or 0)
    unique_opened = opened
    total_opens = int(row.total_opens or 0)

    open_rate = (
        round((unique_opened / total_recipients) * 100, 4)
        if total_recipients > 0
        else 0.0
    )

    return CampaignStatsResponse(
        campaign_id=campaign.id,
        name=campaign.name,
        subject=campaign.subject,
        total_recipients=total_recipients,
        pending=pending,
        sent=sent,
        failed=failed,
        delivered=delivered,
        opened=opened,
        unique_opened=unique_opened,
        total_opens=total_opens,
        open_rate=open_rate,
    )


def to_campaign_response(campaign: Campaign) -> CampaignResponse:
    return CampaignResponse.model_validate(campaign)
