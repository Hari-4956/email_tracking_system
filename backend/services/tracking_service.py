from datetime import datetime
import logging

from fastapi import HTTPException, Request
from fastapi.responses import Response
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from backend.models import EmailEvent, Recipient

logger = logging.getLogger(__name__)

# 1x1 transparent GIF
TRACKING_PIXEL = (
    b"GIF89a"
    b"\x01\x00\x01\x00"
    b"\x80\x00\x00"
    b"\x00\x00\x00"
    b"\xff\xff\xff"
    b"!\xf9\x04\x01"
    b"\x00\x00\x00\x00"
    b",\x00\x00\x00\x00"
    b"\x01\x00\x01\x00"
    b"\x00\x02\x02"
    b"\x44\x01\x00"
    b";"
)

PIXEL_HEADERS = {
    "Cache-Control": "no-cache, no-store, must-revalidate, max-age=0",
    "Pragma": "no-cache",
    "Expires": "0",
    "X-Robots-Tag": "noindex, nofollow",
}


def record_email_open(
    db: Session,
    tracking_token: str,
    request: Request,
) -> Response:
    """
    Record an OPENED event for the recipient identified by tracking_token
    and return a 1x1 transparent GIF.

    Recipient open fields and EmailEvent creation commit together.
    On failure, the session is rolled back so neither change is persisted alone.
    """
    token = (tracking_token or "").strip()
    if not token:
        raise HTTPException(
            status_code=404,
            detail="Tracking token not found",
        )

    recipient = (
        db.query(Recipient)
        .filter(Recipient.tracking_token == token)
        .first()
    )

    if recipient is None:
        raise HTTPException(
            status_code=404,
            detail="Tracking token not found",
        )

    now = datetime.utcnow()

    if recipient.first_opened_at is None:
        recipient.first_opened_at = now

    recipient.last_opened_at = now
    recipient.open_count = (recipient.open_count or 0) + 1

    ip_address = request.client.host if request.client else None
    user_agent = request.headers.get("user-agent")

    event = EmailEvent(
        recipient_id=recipient.id,
        event_type="OPENED",
        event_time=now,
        ip_address=ip_address,
        user_agent=user_agent,
    )
    db.add(event)

    try:
        db.commit()
    except SQLAlchemyError:
        db.rollback()
        logger.exception("Failed to record email open for recipient_id=%s", recipient.id)
        raise HTTPException(
            status_code=500,
            detail="Unable to record tracking event",
        ) from None

    return Response(
        content=TRACKING_PIXEL,
        media_type="image/gif",
        headers=PIXEL_HEADERS,
    )
