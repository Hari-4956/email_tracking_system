from fastapi import APIRouter, Depends, HTTPException, Path, Query
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.schemas import (
    RecipientListResponse,
    RecipientResponse,
    TestRecipientResponse,
)
from backend.services import recipient_service

router = APIRouter(
    prefix="/api/recipients",
    tags=["Recipients"],
)


@router.get(
    "/test",
    response_model=TestRecipientResponse,
    summary="Return one sample recipient",
)
def get_test_recipient(db: Session = Depends(get_db)):
    """Return one real recipient from PostgreSQL for safe testing."""
    recipient = recipient_service.get_test_recipient(db)

    if recipient is None:
        return TestRecipientResponse(
            status="not_found",
            message="No recipients found in database",
        )

    return TestRecipientResponse(
        status="success",
        recipient=recipient_service.build_recipient_response(recipient),
    )


@router.get(
    "/pending",
    response_model=RecipientListResponse,
    summary="List PENDING recipients",
)
def get_pending_recipients(
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=50, ge=1, le=500),
    campaign_id: int | None = Query(default=None, ge=1),
    db: Session = Depends(get_db),
):
    recipients, total = recipient_service.get_pending_recipients(
        db=db,
        skip=skip,
        limit=limit,
        campaign_id=campaign_id,
    )
    return RecipientListResponse(
        total=total,
        skip=skip,
        limit=limit,
        recipients=[
            recipient_service.build_recipient_response(r) for r in recipients
        ],
    )


@router.get(
    "/email/{email}",
    response_model=RecipientResponse,
    summary="Get recipient by email",
)
def get_recipient_by_email(email: str, db: Session = Depends(get_db)):
    recipient = recipient_service.get_recipient_by_email(db, email)
    if recipient is None:
        raise HTTPException(status_code=404, detail="Recipient not found")
    return recipient_service.build_recipient_response(recipient)


@router.get(
    "/token/{tracking_token}",
    response_model=RecipientResponse,
    summary="Get recipient by tracking token",
)
def get_recipient_by_token(
    tracking_token: str = Path(..., min_length=1, max_length=64),
    db: Session = Depends(get_db),
):
    recipient = recipient_service.get_recipient_by_token(db, tracking_token)
    if recipient is None:
        raise HTTPException(status_code=404, detail="Recipient not found")
    return recipient_service.build_recipient_response(recipient)


@router.get(
    "/{recipient_id}",
    response_model=RecipientResponse,
    summary="Get recipient by ID",
)
def get_recipient_by_id(
    recipient_id: int = Path(..., ge=1),
    db: Session = Depends(get_db),
):
    recipient = recipient_service.get_recipient_by_id(db, recipient_id)
    if recipient is None:
        raise HTTPException(status_code=404, detail="Recipient not found")
    return recipient_service.build_recipient_response(recipient)


@router.get(
    "",
    response_model=RecipientListResponse,
    summary="List recipients (paginated, searchable)",
    description=(
        "Server-side search/filter/pagination over recipients. "
        "search matches name, email, and tracking_token (case-insensitive). "
        "status supports PENDING, SENT, FAILED. "
        "opened=true/false filters on first_opened_at."
    ),
)
def list_recipients(
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=50, ge=1, le=500),
    campaign_id: int | None = Query(default=None, ge=1),
    search: str | None = Query(
        default=None,
        max_length=255,
        description="Case-insensitive match on name, email, or tracking_token",
    ),
    status: str | None = Query(
        default=None,
        description="Filter by send_status: PENDING, SENT, or FAILED",
    ),
    opened: bool | None = Query(
        default=None,
        description="true = first_opened_at IS NOT NULL; false = IS NULL",
    ),
    db: Session = Depends(get_db),
):
    normalized_status: str | None = None
    if status is not None:
        normalized_status = status.strip().upper()
        if normalized_status not in recipient_service.ALLOWED_SEND_STATUSES:
            raise HTTPException(
                status_code=422,
                detail="status must be one of: PENDING, SENT, FAILED",
            )

    recipients, total = recipient_service.get_recipients(
        db=db,
        skip=skip,
        limit=limit,
        campaign_id=campaign_id,
        search=search,
        status=normalized_status,
        opened=opened,
    )
    return RecipientListResponse(
        total=total,
        skip=skip,
        limit=limit,
        recipients=[
            recipient_service.build_recipient_response(r) for r in recipients
        ],
    )
