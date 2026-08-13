"""
DEVELOPMENT / SETUP UTILITY ONLY.

Creates tables via SQLAlchemy metadata if they do not already exist.

Do NOT use this as a production migration system.
Do NOT run against production as a routine deploy step.
Existing campaign/recipient/event data must not be dropped or truncated.
"""

from .database import Base, engine
from .models import Campaign, Recipient, EmailEvent  # noqa: F401


print("Creating database tables (IF NOT EXISTS via SQLAlchemy create_all)...")

Base.metadata.create_all(bind=engine)

print("Database tables created successfully.")
