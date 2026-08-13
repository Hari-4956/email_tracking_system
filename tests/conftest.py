import pytest
from fastapi.testclient import TestClient
from sqlalchemy import func, text

from backend.database import SessionLocal
from backend.main import app
from backend.models import Campaign, Recipient


@pytest.fixture(scope="session")
def client():
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture(scope="session")
def db_session():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture(scope="session")
def campaign_one(db_session):
    campaign = db_session.query(Campaign).filter(Campaign.id == 1).first()
    assert campaign is not None, "Campaign id=1 must exist"
    return campaign


@pytest.fixture(scope="session")
def existing_recipient(db_session):
    recipient = (
        db_session.query(Recipient)
        .filter(Recipient.campaign_id == 1)
        .order_by(Recipient.id.asc())
        .first()
    )
    assert recipient is not None, "At least one recipient must exist"
    return recipient


@pytest.fixture(scope="session")
def recipient_count(db_session):
    return (
        db_session.query(func.count(Recipient.id))
        .filter(Recipient.campaign_id == 1)
        .scalar()
        or 0
    )
