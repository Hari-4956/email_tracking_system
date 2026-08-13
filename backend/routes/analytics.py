from fastapi import APIRouter, Depends, HTTPException, Path, Query
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.schemas import (
    CampaignOpenEventListResponse,
    CampaignStatsResponse,
    EmailEventListResponse,
    OpenTimelineResponse,
    RecipientResponse,
)
from backend.services import analytics_service

router = APIRouter(
    prefix="/api/analytics",
    tags=["Analytics"],
)


@router.get(
    "/campaign/{campaign_id}",
    response_model=CampaignStatsResponse,
    summary="Campaign analytics overview",
)
def get_campaign_analytics(
    campaign_id: int = Path(..., ge=1),
    db: Session = Depends(get_db),
):
    stats = analytics_service.get_campaign_analytics(db, campaign_id)
    if stats is None:
        raise HTTPException(status_code=404, detail="Campaign not found")
    return stats


@router.get(
    "/campaign/{campaign_id}/opens/timeline",
    response_model=OpenTimelineResponse,
    summary="Campaign opens timeline (GROUP BY date)",
)
def get_campaign_opens_timeline(
    campaign_id: int = Path(..., ge=1),
    db: Session = Depends(get_db),
):
    timeline = analytics_service.get_campaign_opens_timeline(db, campaign_id)
    if timeline is None:
        raise HTTPException(status_code=404, detail="Campaign not found")
    return OpenTimelineResponse(
        campaign_id=campaign_id,
        timeline=timeline,
    )


@router.get(
    "/campaign/{campaign_id}/opens",
    response_model=CampaignOpenEventListResponse,
    summary="Campaign open events (paginated JOIN)",
)
def get_campaign_opens(
    campaign_id: int = Path(..., ge=1),
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=50, ge=1, le=500),
    db: Session = Depends(get_db),
):
    result = analytics_service.get_campaign_open_events(
        db=db,
        campaign_id=campaign_id,
        skip=skip,
        limit=limit,
    )
    if result is None:
        raise HTTPException(status_code=404, detail="Campaign not found")

    items, total = result
    return CampaignOpenEventListResponse(
        campaign_id=campaign_id,
        total=total,
        skip=skip,
        limit=limit,
        opens=items,
    )


@router.get(
    "/recipient/{recipient_id}/events",
    response_model=EmailEventListResponse,
    summary="Recipient email event history",
)
def get_recipient_events(
    recipient_id: int = Path(..., ge=1),
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=50, ge=1, le=500),
    db: Session = Depends(get_db),
):
    result = analytics_service.get_recipient_events(
        db=db,
        recipient_id=recipient_id,
        skip=skip,
        limit=limit,
    )
    if result is None:
        raise HTTPException(status_code=404, detail="Recipient not found")

    events, total = result
    return EmailEventListResponse(
        recipient_id=recipient_id,
        total=total,
        skip=skip,
        limit=limit,
        events=[
            analytics_service.to_email_event_response(event) for event in events
        ],
    )


@router.get(
    "/recipient/{recipient_id}",
    response_model=RecipientResponse,
    summary="Recipient analytics detail",
)
def get_recipient_analytics(
    recipient_id: int = Path(..., ge=1),
    db: Session = Depends(get_db),
):
    recipient = analytics_service.get_recipient_analytics(db, recipient_id)
    if recipient is None:
        raise HTTPException(status_code=404, detail="Recipient not found")
    return recipient
