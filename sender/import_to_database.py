from pathlib import Path
import sys

import pandas as pd
from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError, SQLAlchemyError


# ============================================================
# PROJECT PATH
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parent.parent

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


# ============================================================
# DATABASE IMPORTS
# ============================================================

from backend.database import SessionLocal
from backend.models import Campaign, Recipient


# ============================================================
# CONFIGURATION
# ============================================================

EXCEL_FILE = (
    PROJECT_ROOT
    / "data"
    / "recipients_tracking.xlsx"
)

CAMPAIGN_NAME = "E STAR Independence Day 2026"

CAMPAIGN_SUBJECT = (
    "Happy Independence Day - E STAR Engineers"
)

BATCH_SIZE = 1000


# ============================================================
# STEP 1 — READ EXCEL
# ============================================================

def load_excel():

    print("=" * 70)
    print("STEP 1: READING EXCEL FILE")
    print("=" * 70)

    if not EXCEL_FILE.exists():
        raise FileNotFoundError(
            f"\nExcel file not found:\n{EXCEL_FILE}"
        )

    print(f"File: {EXCEL_FILE}")

    df = pd.read_excel(EXCEL_FILE)

    print(f"Rows found: {len(df):,}")

    required_columns = {
        "ID",
        "Name",
        "Email",
        "Tracking ID",
        "Send Status",
        "Open Status",
        "First Opened",
        "Last Opened",
        "Open Count",
    }

    missing_columns = (
        required_columns - set(df.columns)
    )

    if missing_columns:
        raise ValueError(
            "\nMissing columns in Excel:\n"
            + "\n".join(
                f"  - {column}"
                for column in sorted(missing_columns)
            )
        )

    print("All required columns found.")

    return df


# ============================================================
# STEP 2 — VALIDATE AND CLEAN DATA
# ============================================================

def clean_data(df):

    print()
    print("=" * 70)
    print("STEP 2: VALIDATING RECIPIENT DATA")
    print("=" * 70)

    df["Name"] = (
        df["Name"]
        .fillna("")
        .astype(str)
        .str.strip()
    )

    df["Email"] = (
        df["Email"]
        .fillna("")
        .astype(str)
        .str.strip()
        .str.lower()
    )

    df["Tracking ID"] = (
        df["Tracking ID"]
        .fillna("")
        .astype(str)
        .str.strip()
    )

    empty_names = (
        df["Name"] == ""
    ).sum()

    empty_emails = (
        df["Email"] == ""
    ).sum()

    empty_tracking_ids = (
        df["Tracking ID"] == ""
    ).sum()

    print(f"Empty names:          {empty_names:,}")
    print(f"Empty emails:         {empty_emails:,}")
    print(
        f"Empty Tracking IDs:   "
        f"{empty_tracking_ids:,}"
    )

    if empty_emails > 0:
        raise ValueError(
            f"\nFound {empty_emails:,} rows "
            "with empty email addresses."
        )

    if empty_tracking_ids > 0:
        raise ValueError(
            f"\nFound {empty_tracking_ids:,} rows "
            "with empty Tracking IDs."
        )

    # --------------------------------------------------------
    # Tracking ID uniqueness
    # --------------------------------------------------------

    duplicate_tracking_ids = (
        df["Tracking ID"]
        .duplicated()
        .sum()
    )

    print(
        f"Duplicate Tracking IDs: "
        f"{duplicate_tracking_ids:,}"
    )

    if duplicate_tracking_ids > 0:

        duplicates = df[
            df["Tracking ID"].duplicated(
                keep=False
            )
        ]

        print()
        print(
            "Duplicate Tracking ID examples:"
        )

        print(
            duplicates[
                [
                    "ID",
                    "Name",
                    "Email",
                    "Tracking ID",
                ]
            ]
            .head(10)
            .to_string(index=False)
        )

        raise ValueError(
            "\nDuplicate Tracking IDs detected. "
            "Fix the Excel file before importing."
        )

    # --------------------------------------------------------
    # Duplicate emails
    # --------------------------------------------------------

    duplicate_email_count = (
        df["Email"]
        .duplicated()
        .sum()
    )

    print(
        f"Duplicate email addresses: "
        f"{duplicate_email_count:,}"
    )

    if duplicate_email_count > 0:

        print()
        print("WARNING:")
        print(
            "Duplicate email addresses exist "
            "in the spreadsheet."
        )

        print(
            "Only one recipient record per email "
            "will be imported for this campaign."
        )

        df = df.drop_duplicates(
            subset=["Email"],
            keep="first"
        ).copy()

        print(
            f"Duplicate email rows removed: "
            f"{duplicate_email_count:,}"
        )

    print()
    print(
        f"Valid unique recipients: "
        f"{len(df):,}"
    )

    print(
        "Validation completed successfully."
    )

    return df


# ============================================================
# STEP 3 — GET OR CREATE CAMPAIGN
# ============================================================

def get_or_create_campaign(db):

    print()
    print("=" * 70)
    print("STEP 3: GETTING / CREATING CAMPAIGN")
    print("=" * 70)

    statement = select(Campaign).where(
        Campaign.name == CAMPAIGN_NAME
    )

    campaign = (
        db.execute(statement)
        .scalar_one_or_none()
    )

    if campaign:

        print("Existing campaign found.")

        print(
            f"  Name: {campaign.name}"
        )

        print(
            f"  ID:   {campaign.id}"
        )

        return campaign.id

    campaign = Campaign(
        name=CAMPAIGN_NAME,
        subject=CAMPAIGN_SUBJECT,
        total_recipients=0,
    )

    db.add(campaign)

    db.flush()

    campaign_id = campaign.id

    print("New campaign created.")

    print(
        f"  Name: {campaign.name}"
    )

    print(
        f"  ID:   {campaign_id}"
    )

    return campaign_id


# ============================================================
# STEP 4 — IMPORT RECIPIENTS
# ============================================================

def import_recipients(df, campaign_id):

    print()
    print("=" * 70)
    print("STEP 4: IMPORTING RECIPIENTS")
    print("=" * 70)

    db = SessionLocal()

    inserted = 0
    skipped = 0
    failed = 0

    try:

        # ----------------------------------------------------
        # Existing Tracking IDs
        # ----------------------------------------------------

        existing_tracking_ids = set(
            db.execute(
                select(
                    Recipient.tracking_token
                ).where(
                    Recipient.campaign_id
                    == campaign_id
                )
            )
            .scalars()
            .all()
        )

        print(
            f"Already imported Tracking IDs: "
            f"{len(existing_tracking_ids):,}"
        )

        # ----------------------------------------------------
        # Existing emails
        # ----------------------------------------------------

        existing_emails = set(
            email.lower()
            for email in
            db.execute(
                select(
                    Recipient.email
                ).where(
                    Recipient.campaign_id
                    == campaign_id
                )
            )
            .scalars()
            .all()
        )

        print(
            f"Already imported emails: "
            f"{len(existing_emails):,}"
        )

        print()

        total = len(df)

        # ----------------------------------------------------
        # Process batches
        # ----------------------------------------------------

        for start in range(
            0,
            total,
            BATCH_SIZE
        ):

            end = min(
                start + BATCH_SIZE,
                total
            )

            batch = df.iloc[start:end]

            recipients_to_add = []

            for _, row in batch.iterrows():

                tracking_id = (
                    str(row["Tracking ID"])
                    .strip()
                )

                email = (
                    str(row["Email"])
                    .strip()
                    .lower()
                )

                name = (
                    str(row["Name"])
                    .strip()
                )

                # --------------------------------------------
                # Already imported
                # --------------------------------------------

                if (
                    tracking_id
                    in existing_tracking_ids
                ):
                    skipped += 1
                    continue

                if email in existing_emails:
                    skipped += 1
                    continue

                # --------------------------------------------
                # Create recipient
                # --------------------------------------------

                recipient = Recipient(
                    campaign_id=campaign_id,
                    name=name,
                    email=email,
                    tracking_token=tracking_id,
                    send_status="PENDING",
                    sent_at=None,
                    delivered_at=None,
                    first_opened_at=None,
                    last_opened_at=None,
                    open_count=0,
                    retry_count=0,
                    last_error=None,
                )

                recipients_to_add.append(
                    recipient
                )

                existing_tracking_ids.add(
                    tracking_id
                )

                existing_emails.add(
                    email
                )

            # ------------------------------------------------
            # Insert batch
            # ------------------------------------------------

            if recipients_to_add:

                try:

                    db.add_all(
                        recipients_to_add
                    )

                    db.flush()

                    inserted += len(
                        recipients_to_add
                    )

                except IntegrityError as error:

                    db.rollback()

                    print()
                    print(
                        f"Integrity error in batch "
                        f"{start:,}-{end:,}"
                    )

                    print(error)

                    failed += len(
                        recipients_to_add
                    )

                    for recipient in (
                        recipients_to_add
                    ):

                        existing_tracking_ids.discard(
                            recipient.tracking_token
                        )

                        existing_emails.discard(
                            recipient.email
                        )

                except SQLAlchemyError as error:

                    db.rollback()

                    print()
                    print(
                        f"Database error in batch "
                        f"{start:,}-{end:,}"
                    )

                    print(error)

                    failed += len(
                        recipients_to_add
                    )

                    for recipient in (
                        recipients_to_add
                    ):

                        existing_tracking_ids.discard(
                            recipient.tracking_token
                        )

                        existing_emails.discard(
                            recipient.email
                        )

            # ------------------------------------------------
            # Progress
            # ------------------------------------------------

            processed = end

            percentage = (
                processed / total
            ) * 100

            print(
                f"Progress: "
                f"{processed:,}/{total:,} "
                f"({percentage:.2f}%) | "
                f"Inserted: {inserted:,} | "
                f"Skipped: {skipped:,} | "
                f"Failed: {failed:,}"
            )

        # ----------------------------------------------------
        # Update campaign count
        # ----------------------------------------------------

        campaign_total = db.execute(
            select(
                func.count(Recipient.id)
            ).where(
                Recipient.campaign_id
                == campaign_id
            )
        ).scalar_one()

        # ----------------------------------------------------
        # Update campaign
        # ----------------------------------------------------

        campaign = db.get(
            Campaign,
            campaign_id
        )

        if campaign:
            campaign.total_recipients = (
                campaign_total
            )

        # ----------------------------------------------------
        # Commit
        # ----------------------------------------------------

        db.commit()

        print()
        print("=" * 70)
        print("IMPORT COMPLETED")
        print("=" * 70)

        print(
            f"Inserted:         {inserted:,}"
        )

        print(
            f"Skipped:          {skipped:,}"
        )

        print(
            f"Failed:           {failed:,}"
        )

        print(
            f"Campaign total:   "
            f"{campaign_total:,}"
        )

    except Exception as error:

        db.rollback()

        print()
        print("=" * 70)
        print("IMPORT FAILED")
        print("=" * 70)

        print(
            f"Error: {error}"
        )

        raise

    finally:

        db.close()


# ============================================================
# MAIN
# ============================================================

def main():

    print()
    print("=" * 70)
    print("E STAR EMAIL TRACKING SYSTEM")
    print("POSTGRESQL RECIPIENT IMPORTER")
    print("=" * 70)
    print()

    # --------------------------------------------------------
    # Load Excel
    # --------------------------------------------------------

    df = load_excel()

    # --------------------------------------------------------
    # Validate
    # --------------------------------------------------------

    df = clean_data(df)

    # --------------------------------------------------------
    # Create/Get campaign
    # --------------------------------------------------------

    db = SessionLocal()

    try:

        campaign_id = get_or_create_campaign(
            db
        )

        db.commit()

    except Exception:

        db.rollback()

        raise

    finally:

        db.close()

    # --------------------------------------------------------
    # Import recipients
    # --------------------------------------------------------

    import_recipients(
        df,
        campaign_id
    )

    print()
    print("=" * 70)
    print("DONE")
    print("=" * 70)
    print()


# ============================================================
# ENTRY POINT
# ============================================================

if __name__ == "__main__":
    main()