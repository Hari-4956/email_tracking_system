from fastapi import APIRouter, Depends, HTTPException, Path, Query
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.schemas import (
    CampaignListResponse,
    CampaignResponse,
    CampaignStatsResponse,
)
from backend.services import campaign_service

router = APIRouter(
    prefix="/api/campaigns",
    tags=["Campaigns"],
)


@router.get(
    "",
    response_model=CampaignListResponse,
    summary="List campaigns",
)
def list_campaigns(
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=50, ge=1, le=500),
    db: Session = Depends(get_db),
):
    campaigns, total = campaign_service.get_campaigns(
        db=db,
        skip=skip,
        limit=limit,
    )
    return CampaignListResponse(
        total=total,
        skip=skip,
        limit=limit,
        campaigns=[
            campaign_service.to_campaign_response(c) for c in campaigns
        ],
    )


@router.get(
    "/{campaign_id}/stats",
    response_model=CampaignStatsResponse,
    summary="Campaign statistics (SQL aggregation)",
)
def get_campaign_stats(
    campaign_id: int = Path(..., ge=1),
    db: Session = Depends(get_db),
):
    stats = campaign_service.get_campaign_stats(db, campaign_id)
    if stats is None:
        raise HTTPException(status_code=404, detail="Campaign not found")
    return stats


@router.get(
    "/{campaign_id}",
    response_model=CampaignResponse,
    summary="Get campaign by ID",
)
def get_campaign(
    campaign_id: int = Path(..., ge=1),
    db: Session = Depends(get_db),
):
    campaign = campaign_service.get_campaign_by_id(db, campaign_id)
    if campaign is None:
        raise HTTPException(status_code=404, detail="Campaign not found")
    return campaign_service.to_campaign_response(campaign)
