import csv
from pathlib import Path
from datetime import datetime
import uuid

COMPLAINTS_FILE = Path("complaints.csv")
UPDATES_FILE = Path("complaint_updates.csv")


def initialize_files():

    if not COMPLAINTS_FILE.exists():
        with open(COMPLAINTS_FILE, "w", newline="", encoding="utf-8-sig") as file:
            writer = csv.writer(file)
            writer.writerow([
                "complaint_id",
                "college",
                "complaint_type",
                "title",
                "details",
                "status",
                "ai_category",
                "priority",
                "reasoning",
                "created_at"
            ])

    if not UPDATES_FILE.exists():
        with open(UPDATES_FILE, "w", newline="", encoding="utf-8-sig") as file:
            writer = csv.writer(file)
            writer.writerow([
                "update_id",
                "complaint_id",
                "status",
                "admin_note",
                "updated_at"
            ])


def save_complaint(complaint):

    initialize_files()

    with open(COMPLAINTS_FILE, "r", newline="", encoding="utf-8-sig") as file:
        reader = csv.DictReader(file)
        fieldnames = list(reader.fieldnames or [])
        rows = list(reader)

    missing = [k for k in complaint.keys() if k not in fieldnames]
    if missing:
        fieldnames += missing
        rows.append(complaint)
        with open(COMPLAINTS_FILE, "w", newline="", encoding="utf-8-sig") as file:
            writer = csv.DictWriter(file, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(rows)
        return

    with open(COMPLAINTS_FILE, "a", newline="", encoding="utf-8-sig") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writerow(complaint)


def add_complaint_update(complaint_id, status, admin_note):

    initialize_files()

    update = {
        "update_id": str(uuid.uuid4()),
        "complaint_id": complaint_id,
        "status": status,
        "admin_note": admin_note,
        "updated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }

    with open(UPDATES_FILE, "a", newline="", encoding="utf-8-sig") as file:
        writer = csv.DictWriter(file, fieldnames=update.keys())
        writer.writerow(update)
