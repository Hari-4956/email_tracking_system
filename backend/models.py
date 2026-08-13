from datetime import datetime

from sqlalchemy import (
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .database import Base


class Campaign(Base):
    __tablename__ = "campaigns"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )

    name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    subject: Mapped[str] = mapped_column(
        String(500),
        nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
    )

    total_recipients: Mapped[int] = mapped_column(
        Integer,
        default=0,
    )

    recipients = relationship(
        "Recipient",
        back_populates="campaign",
    )


class Recipient(Base):
    __tablename__ = "recipients"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )

    campaign_id: Mapped[int] = mapped_column(
        ForeignKey("campaigns.id"),
        nullable=False,
        index=True,
    )

    name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    email: Mapped[str] = mapped_column(
        String(320),
        nullable=False,
        index=True,
    )

    tracking_token: Mapped[str] = mapped_column(
        String(36),
        nullable=False,
        unique=True,
        index=True,
    )

    send_status: Mapped[str] = mapped_column(
        String(50),
        default="PENDING",
        nullable=False,
    )

    sent_at: Mapped[datetime | None] = mapped_column(
        DateTime,
        nullable=True,
    )

    delivered_at: Mapped[datetime | None] = mapped_column(
        DateTime,
        nullable=True,
    )

    first_opened_at: Mapped[datetime | None] = mapped_column(
        DateTime,
        nullable=True,
    )

    last_opened_at: Mapped[datetime | None] = mapped_column(
        DateTime,
        nullable=True,
    )

    open_count: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
    )

    retry_count: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
    )

    last_error: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
    )

    campaign = relationship(
        "Campaign",
        back_populates="recipients",
    )

    events = relationship(
        "EmailEvent",
        back_populates="recipient",
        cascade="all, delete-orphan",
    )

    __table_args__ = (
        UniqueConstraint(
            "campaign_id",
            "email",
            name="uq_campaign_recipient_email",
        ),
    )


class EmailEvent(Base):
    __tablename__ = "email_events"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )

    recipient_id: Mapped[int] = mapped_column(
        ForeignKey("recipients.id"),
        nullable=False,
        index=True,
    )

    event_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )

    event_time: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
    )

    ip_address: Mapped[str | None] = mapped_column(
        String(45),
        nullable=True,
    )

    user_agent: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    recipient = relationship(
        "Recipient",
        back_populates="events",
    )