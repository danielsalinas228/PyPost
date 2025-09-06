import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parent.parent))
from modules.postalDatabase import PostalDatabase
from datetime import datetime, timedelta
import sqlite3
import uuid
import json
import os

db = PostalDatabase("test_data/postalDatabase.db")

# Load postal_info from JSON file
postal_info_path = Path("test_data/mock_postal_info.json")
with open(postal_info_path, "r", encoding="utf-8") as f:
    postal_info = json.load(f)

# Helper for datetime strings
def dtstr(days_offset=0, hour=10, minute=0, second=0):
    dt = datetime(2025, 9, 1, hour, minute, second) + timedelta(days=days_offset)
    return dt.strftime("%Y-%m-%d %H:%M:%S")

# Insert multiple mock letters
mock_letters = [
    {
        "letter_id": str(uuid.uuid4()),
        "letter_name": "2025-09-01",
        "creation_datetime": dtstr(0, 10),
        "contents": "First letter.",
        "postal_info": postal_info,
        "received_date": dtstr(0, 10),
        "scheduled_delivery_datetime": dtstr(1, 8),
        "delivery_datetime": None,
        "status": "in transit"
    },
    {
        "letter_id": str(uuid.uuid4()),
        "letter_name": "2025-09-02",
        "creation_datetime": dtstr(1, 11),
        "contents": "Second letter.",
        "postal_info": postal_info,
        "received_date": dtstr(1, 11),
        "scheduled_delivery_datetime": dtstr(2, 8),
        "delivery_datetime": None,
        "status": "in transit"
    },
    {
        "letter_id": str(uuid.uuid4()),
        "letter_name": "2025-09-03",
        "creation_datetime": dtstr(2, 12),
        "contents": "Third letter.",
        "postal_info": postal_info,
        "received_date": dtstr(2, 12),
        "scheduled_delivery_datetime": dtstr(3, 8),
        "delivery_datetime": dtstr(3, 9),
        "status": "delivered"
    }
]

for letter in mock_letters:
    db.insert_letter(letter)

# Test get_letter_by_id
print("\nTest get_letter_by_id (first letter):")
first_id = mock_letters[0]["letter_id"]
result = db.get_letter_by_id(first_id)
if result and result["letter_id"] == first_id:
    print("PASS")
else:
    print("FAIL")

# Test get_pending_letters
print("\nTest get_pending_letters:")
pending = db.get_pending_letters()
if isinstance(pending, list) and len(pending) == 2:
    print("PASS")
else:
    print("FAIL")

# Test get_last_submitted_letter
print("\nTest get_last_submitted_letter:")
last = db.get_last_submitted_letter()
if last and last["letter_name"] == "2025-09-02":
    print("PASS")
else:
    print("FAIL")

# Test get_next_letter_to_deliver
print("\nTest get_next_letter_to_deliver:")
next_letter = db.get_next_letter_to_deliver()
if next_letter and next_letter["letter_name"] == "2025-09-01":
    print("PASS")
else:
    print("FAIL")

# Test get_all_delivered_letters
print("\nTest get_all_delivered_letters:")
delivered = db.get_all_delivered_letters()
if isinstance(delivered, list) and len(delivered) == 1 and delivered[0]["status"] == "delivered":
    print("PASS")
else:
    print("FAIL")

# Test update_letter_status
print("\nTest update_letter_status (set first letter to delivered):")
delivery_dt = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
db.update_letter_status(first_id, "delivered", delivery_datetime=delivery_dt)
updated = db.get_letter_by_id(first_id)
if updated and updated["status"] == "delivered" and updated["delivery_datetime"] == delivery_dt:
    print("PASS")
else:
    print("FAIL")

# Clean up: Delete all letters from the database
with sqlite3.connect(db.db_path) as conn:
    c = conn.cursor()
    c.execute("DELETE FROM letters")
    conn.commit()
    print("\nCleanup: All letters deleted.")

# Delete the database file itself
if os.path.exists(db.db_path):
    os.remove(db.db_path)
    print("Database file deleted.")
else:
    print("Database file not found for deletion.")