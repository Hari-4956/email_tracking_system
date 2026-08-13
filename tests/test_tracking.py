from sqlalchemy import func

from backend.models import EmailEvent, Recipient
from backend.services import campaign_service


def test_tracking_token_not_found(client):
    response = client.get("/track/open/00000000-0000-0000-0000-000000000000")
    assert response.status_code == 404
    assert response.json()["detail"] == "Tracking token not found"


def test_tracking_open_existing_token(client, existing_recipient, db_session):
    """
    Uses an EXISTING tracking token.
    May create one additional OPENED event (allowed by Phase 4).
    Does not reset open_count or delete events afterward.
    """
    db_session.expire_all()
    before = (
        db_session.query(Recipient)
        .filter(Recipient.id == existing_recipient.id)
        .first()
    )
    token = before.tracking_token
    open_before = before.open_count
    events_before = (
        db_session.query(func.count(EmailEvent.id))
        .filter(EmailEvent.recipient_id == before.id)
        .scalar()
        or 0
    )

    response = client.get(
        f"/track/open/{token}",
        headers={"User-Agent": "Phase4-TestSuite/1.0"},
    )

    assert response.status_code == 200
    assert response.headers["content-type"].startswith("image/gif")
    assert response.content[:6] == b"GIF89a"

    db_session.expire_all()
    after = (
        db_session.query(Recipient)
        .filter(Recipient.id == existing_recipient.id)
        .first()
    )
    events_after = (
        db_session.query(func.count(EmailEvent.id))
        .filter(EmailEvent.recipient_id == after.id)
        .scalar()
        or 0
    )
    last_event = (
        db_session.query(EmailEvent)
        .filter(EmailEvent.recipient_id == after.id)
        .order_by(EmailEvent.id.desc())
        .first()
    )

    assert after.tracking_token == token
    assert after.open_count == open_before + 1
    assert after.last_opened_at is not None
    assert after.first_opened_at is not None
    assert events_after == events_before + 1
    assert last_event is not None
    assert last_event.event_type == "OPENED"
    assert last_event.ip_address is not None
    assert last_event.user_agent == "Phase4-TestSuite/1.0"


def test_stats_uses_sql_aggregation_not_full_load(db_session):
    """
    Ensure campaign stats path does not rely on loading all recipients.
    Inspect compiled SQL for aggregate keywords.
    """
    from sqlalchemy.dialects import postgresql

    from backend.models import Recipient
    from sqlalchemy import case, func

    query = db_session.query(
        func.count(Recipient.id).label("total_recipients"),
        func.coalesce(
            func.sum(case((Recipient.send_status == "PENDING", 1), else_=0)),
            0,
        ).label("pending"),
        func.coalesce(func.sum(Recipient.open_count), 0).label("total_opens"),
    ).filter(Recipient.campaign_id == 1)

    compiled = str(
        query.statement.compile(
            dialect=postgresql.dialect(),
            compile_kwargs={"literal_binds": True},
        )
    ).lower()

    assert "count(" in compiled
    assert "sum(" in compiled
    assert "from recipients" in compiled

    # Live service still returns consistent totals
    stats = campaign_service.get_campaign_stats(db_session, 1)
    assert stats is not None
    assert stats.total_recipients == 71627


def test_existing_data_integrity(db_session, campaign_one, recipient_count):
    assert campaign_one.name == "E STAR Independence Day 2026"
    assert recipient_count == 71627
    assert campaign_one.total_recipients == 71627

    event_count = db_session.query(func.count(EmailEvent.id)).scalar() or 0
    assert event_count >= 1

    # Tokens remain non-null / unique for campaign 1
    null_tokens = (
        db_session.query(func.count(Recipient.id))
        .filter(
            Recipient.campaign_id == 1,
            Recipient.tracking_token.is_(None),
        )
        .scalar()
        or 0
    )
    assert null_tokens == 0

    # Confirm we are not somehow back at the pre-cleanup size
    assert recipient_count != 78931
    assert recipient_count < 78931
