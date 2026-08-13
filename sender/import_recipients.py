# import pandas as pd
# import uuid
# from pathlib import Path

# INPUT_FILE = Path(r"C:\Hari_s Folder\email_tracking_system\data\email_tracking_system_testing.xlsx")
# OUTPUT_FILE = Path(r"C:\Hari_s Folder\email_tracking_system\data\recipients_tracking.xlsx")


# def generate_tracking_ids():

#     print("Reading spreadsheet...")

#     df = pd.read_excel(INPUT_FILE)

#     print(f"Found {len(df):,} recipients")

#     # Validate required columns
#     required_columns = {"Name", "Email"}

#     missing_columns = required_columns - set(df.columns)

#     if missing_columns:
#         raise ValueError(
#             f"Missing columns: {missing_columns}"
#         )

#     # Create sequential ID
#     df.insert(
#         0,
#         "ID",
#         range(1, len(df) + 1)
#     )

#     # Generate unique UUID for every recipient
#     df["Tracking ID"] = [
#         str(uuid.uuid4())
#         for _ in range(len(df))
#     ]

#     # Initial status
#     df["Send Status"] = "Pending"
#     df["Open Status"] = "Not Opened"
#     df["First Opened"] = ""
#     df["Last Opened"] = ""
#     df["Open Count"] = 0

#     # Save processed spreadsheet
#     df.to_excel(
#         OUTPUT_FILE,
#         index=False
#     )

#     print()
#     print("Processing completed.")
#     print(f"Recipients : {len(df):,}")
#     print(f"Output     : {OUTPUT_FILE}")


# if __name__ == "__main__":
#     generate_tracking_ids()

import pandas as pd

file = "../data/recipients_tracking.xlsx"

df = pd.read_excel(file)

print("Total recipients:", len(df))
print("Unique IDs:", df["ID"].nunique())
print("Unique Tracking IDs:", df["Tracking ID"].nunique())
print("Duplicate emails:", df["Email"].duplicated().sum())
print("Pending:", (df["Send Status"] == "Pending").sum())
print("Not opened:", (df["Open Status"] == "Not Opened").sum())