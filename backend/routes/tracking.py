from fastapi import APIRouter, Depends, Path, Request
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.services.tracking_service import record_email_open

router = APIRouter(
    prefix="/track",
    tags=["Email Tracking"],
)


@router.get(
    "/open/{tracking_token}",
    summary="Record email open via tracking pixel",
    description=(
        "Records an OPENED event for the recipient identified by tracking_token "
        "and returns a 1x1 transparent GIF. URL format must remain "
        "/track/open/{tracking_token}."
    ),
)
def track_email_open(
    request: Request,
    tracking_token: str = Path(..., min_length=1, max_length=64),
    db: Session = Depends(get_db),
):
    return record_email_open(
        db=db,
        tracking_token=tracking_token,
        request=request,
    )
