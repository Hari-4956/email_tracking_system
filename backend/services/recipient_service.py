from sqlalchemy import func, or_
from sqlalchemy.orm import Session, Query

from backend.config import get_settings
from backend.models import Recipient
from backend.schemas import RecipientResponse


DEFAULT_LIMIT = 50
MAX_LIMIT = 500
ALLOWED_SEND_STATUSES = frozenset({"PENDING", "SENT", "FAILED"})


def _clamp_limit(limit: int) -> int:
    if limit < 1:
        return 1
    if limit > MAX_LIMIT:
        return MAX_LIMIT
    return limit


def _escape_like(value: str) -> str:
    """Escape LIKE wildcards so user input is treated literally."""
    return (
        value.replace("\\", "\\\\")
        .replace("%", "\\%")
        .replace("_", "\\_")
    )


def build_recipient_response(recipient: Recipient) -> RecipientResponse:
    settings = get_settings()
    return RecipientResponse(
        id=recipient.id,
        campaign_id=recipient.campaign_id,
        name=recipient.name,
        email=recipient.email,
        tracking_token=recipient.tracking_token,
        send_status=recipient.send_status,
        sent_at=recipient.sent_at,
        delivered_at=recipient.delivered_at,
        first_opened_at=recipient.first_opened_at,
        last_opened_at=recipient.last_opened_at,
        open_count=recipient.open_count,
        retry_count=recipient.retry_count,
        last_error=recipient.last_error,
        created_at=recipient.created_at,
        tracking_url=settings.build_tracking_url(recipient.tracking_token),
    )


def _apply_recipient_filters(
    query: Query,
    *,
    campaign_id: int | None = None,
    search: str | None = None,
    status: str | None = None,
    opened: bool | None = None,
) -> Query:
    if campaign_id is not None:
        query = query.filter(Recipient.campaign_id == campaign_id)

    if status is not None:
        query = query.filter(Recipient.send_status == status)

    if opened is True:
        query = query.filter(Recipient.first_opened_at.isnot(None))
    elif opened is False:
        query = query.filter(Recipient.first_opened_at.is_(None))

    if search:
        term = search.strip()
        if term:
            pattern = f"%{_escape_like(term)}%"
            query = query.filter(
                or_(
                    Recipient.name.ilike(pattern, escape="\\"),
                    Recipient.email.ilike(pattern, escape="\\"),
                    Recipient.tracking_token.ilike(pattern, escape="\\"),
                )
            )

    return query


def get_recipients(
    db: Session,
    skip: int = 0,
    limit: int = DEFAULT_LIMIT,
    campaign_id: int | None = None,
    search: str | None = None,
    status: str | None = None,
    opened: bool | None = None,
) -> tuple[list[Recipient], int]:
    limit = _clamp_limit(limit)
    skip = max(skip, 0)

    filtered = _apply_recipient_filters(
        db.query(Recipient),
        campaign_id=campaign_id,
        search=search,
        status=status,
        opened=opened,
    )

    total = (
        _apply_recipient_filters(
            db.query(func.count(Recipient.id)),
            campaign_id=campaign_id,
            search=search,
            status=status,
            opened=opened,
        ).scalar()
        or 0
    )

    recipients = (
        filtered.order_by(Recipient.id.asc())
        .offset(skip)
        .limit(limit)
        .all()
    )
    return recipients, int(total)


def get_recipient_by_id(db: Session, recipient_id: int) -> Recipient | None:
    return (
        db.query(Recipient)
        .filter(Recipient.id == recipient_id)
        .first()
    )


def get_recipient_by_email(db: Session, email: str) -> Recipient | None:
    return (
        db.query(Recipient)
        .filter(func.lower(Recipient.email) == email.lower())
        .order_by(Recipient.id.asc())
        .first()
    )


def get_recipient_by_token(db: Session, tracking_token: str) -> Recipient | None:
    return (
        db.query(Recipient)
        .filter(Recipient.tracking_token == tracking_token)
        .first()
    )


def get_pending_recipients(
    db: Session,
    skip: int = 0,
    limit: int = DEFAULT_LIMIT,
    campaign_id: int | None = None,
) -> tuple[list[Recipient], int]:
    return get_recipients(
        db=db,
        skip=skip,
        limit=limit,
        campaign_id=campaign_id,
        status="PENDING",
    )


def get_test_recipient(db: Session) -> Recipient | None:
    """Return the first available recipient from PostgreSQL."""
    return db.query(Recipient).order_by(Recipient.id.asc()).first()
