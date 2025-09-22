import sqlite3
from datetime import datetime, timedelta
from typing import Optional
import json
import os

class PostalDatabase:
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.init_database()

    def init_database(self):
        """Create the letters table if it doesn't exist."""
        with sqlite3.connect(self.db_path) as conn:
            c = conn.cursor()
            c.execute("""
                CREATE TABLE IF NOT EXISTS letters (
                    letter_id TEXT PRIMARY KEY,
                    letter_name TEXT NOT NULL,
                    creation_datetime TEXT NOT NULL,
                    contents TEXT NOT NULL,
                    html_contents TEXT NOT NULL,
                    postal_info TEXT NOT NULL,
                    received_date TEXT NOT NULL,
                    scheduled_delivery_datetime TEXT NOT NULL,
                    delivery_datetime TEXT,
                    status TEXT NOT NULL
                )
            """)
            conn.commit()

    def insert_letter(self, letter_data: dict) -> str:
        """Insert new letter into database. Expects all fields in letter_data."""
        with sqlite3.connect(self.db_path) as conn:
            c = conn.cursor()
            c.execute("""
                INSERT INTO letters (
                    letter_id, letter_name, creation_datetime, contents, html_contents, postal_info,
                    received_date, scheduled_delivery_datetime, delivery_datetime, status
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                letter_data['letter_id'],
                letter_data['letter_name'],
                letter_data['creation_datetime'],
                letter_data['contents'],
                letter_data['html_contents'],
                json.dumps(letter_data['postal_info']),
                letter_data['received_date'],
                letter_data['scheduled_delivery_datetime'],
                letter_data.get('delivery_datetime'),  # Can be None at insert
                letter_data['status']
            ))
            conn.commit()
            return letter_data['letter_id']

    def get_letter_by_id(self, letter_id: str) -> Optional[dict]:
        """Retrieve letter data by ID."""
        with sqlite3.connect(self.db_path) as conn:
            c = conn.cursor()
            c.execute("SELECT * FROM letters WHERE letter_id = ?", (letter_id,))
            row = c.fetchone()
            if row:
                return {
                    "letter_id": row[0],
                    "letter_name": row[1],
                    "creation_datetime": row[2],
                    "contents": row[3],
                    "html_contents": row[4],
                    "postal_info": json.loads(row[5]),
                    "received_date": row[6],
                    "scheduled_delivery_datetime": row[7],
                    "delivery_datetime": row[8],
                    "status": row[9],
                }
            return None

    def get_pending_letters(self) -> list[dict]:
        """Get all letters ready for delivery (status = 'in transit' and scheduled_delivery_datetime <= now)."""
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with sqlite3.connect(self.db_path) as conn:
            c = conn.cursor()
            c.execute("""
                SELECT * FROM letters
                WHERE status = 'in transit' AND scheduled_delivery_datetime <= ?
            """, (now,))
            rows = c.fetchall()
            return [
                {
                    "letter_id": row[0],
                    "letter_name": row[1],
                    "creation_datetime": row[2],
                    "contents": row[3],
                    "html_contents": row[4],
                    "postal_info": json.loads(row[5]),
                    "received_date": row[6],
                    "scheduled_delivery_datetime": row[7],
                    "delivery_datetime": row[8],
                    "status": row[9],
                }
                for row in rows
            ]

    def update_letter_status(self, letter_id: str, status: str, delivery_datetime: Optional[str] = None) -> bool:
        """Update letter delivery status and (optionally) delivery_datetime."""
        with sqlite3.connect(self.db_path) as conn:
            c = conn.cursor()
            if delivery_datetime:
                c.execute("""
                    UPDATE letters
                    SET status = ?, delivery_datetime = ?
                    WHERE letter_id = ?
                """, (status, delivery_datetime, letter_id))
            else:
                c.execute("""
                    UPDATE letters
                    SET status = ?
                    WHERE letter_id = ?
                """, (status, letter_id))
            conn.commit()
            return c.rowcount > 0
        
    def get_last_submitted_letter(self) -> Optional[dict]:
        """Retrieve the most recently created letter with status 'in transit'."""
        with sqlite3.connect(self.db_path) as conn:
            c = conn.cursor()
            c.execute("""
                SELECT * FROM letters
                WHERE status = 'in transit'
                ORDER BY received_date DESC
                LIMIT 1
            """)
            row = c.fetchone()
            if row:
                return {
                    "letter_id": row[0],
                    "letter_name": row[1],
                    "creation_datetime": row[2],
                    "contents": row[3],
                    "html_contents": row[4],
                    "postal_info": json.loads(row[5]),
                    "received_date": row[6],
                    "scheduled_delivery_datetime": row[7],
                    "delivery_datetime": row[8],
                    "status": row[9],
                }
            return None
        
    def get_next_letter_to_deliver(self) -> Optional[dict]:
        """Retrieve the next letter to be delivered (earliest received_date with status 'in transit')."""
        with sqlite3.connect(self.db_path) as conn:
            c = conn.cursor()
            c.execute("""
                SELECT * FROM letters
                WHERE status = 'in transit'
                ORDER BY received_date ASC
                LIMIT 1
            """)
            row = c.fetchone()
            if row:
                return {
                    "letter_id": row[0],
                    "letter_name": row[1],
                    "creation_datetime": row[2],
                    "contents": row[3],
                    "html_contents": row[4],
                    "postal_info": json.loads(row[5]),
                    "received_date": row[6],
                    "scheduled_delivery_datetime": row[7],
                    "delivery_datetime": row[8],
                    "status": row[9],
                }
            return None
    
    def get_all_delivered_letters(self) -> list[dict]:
        """Retrieve all letters with status 'delivered', ordered by creation_datetime ascending."""
        with sqlite3.connect(self.db_path) as conn:
            c = conn.cursor()
            c.execute("""
                SELECT * FROM letters
                WHERE status = 'delivered'
                ORDER BY creation_datetime ASC
            """)
            rows = c.fetchall()
            return [
                {
                    "letter_id": row[0],
                    "letter_name": row[1],
                    "creation_datetime": row[2],
                    "contents": row[3],
                    "html_contents": row[4],
                    "postal_info": json.loads(row[5]),
                    "received_date": row[6],
                    "scheduled_delivery_datetime": row[7],
                    "delivery_datetime": row[8],
                    "status": row[9],
                }
                for row in rows
            ]
        
    def getAllLetters(self) -> list[dict]:
        """Retrieve all letters in the database."""
        with sqlite3.connect(self.db_path) as conn:
            c = conn.cursor()
            c.execute("SELECT * FROM letters")
            rows = c.fetchall()
            return [
                {
                    "letter_id": row[0],
                    "letter_name": row[1],
                    "creation_datetime": row[2],
                    "contents": row[3],
                    "html_contents": row[4],
                    "postal_info": json.loads(row[5]),
                    "received_date": row[6],
                    "scheduled_delivery_datetime": row[7],
                    "delivery_datetime": row[8],
                    "status": row[9],
                }
                for row in rows
            ]
    
    def get_all_letters_summary(self) -> list[dict]:
        """Return summary of all letters: letter_id, letter_name, status."""
        with sqlite3.connect(self.db_path) as conn:
            c = conn.cursor()
            c.execute("SELECT letter_id, letter_name, scheduled_delivery_datetime, status FROM letters")
            rows = c.fetchall()
            return [
                {
                    "letter_id": row[0],
                    "letter_name": row[1],
                    "scheduled_delivery_datetime": row[2],
                    "status": row[3]
                }
                for row in rows
            ]

    def get_pending_letters_summary(self) -> list[dict]:
        """Return summary of all pending letters: letter_id, letter_name, status, scheduled_delivery_datetime."""
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with sqlite3.connect(self.db_path) as conn:
            c = conn.cursor()
            c.execute("""
                SELECT letter_id, letter_name, status, scheduled_delivery_datetime
                FROM letters
                WHERE status = 'in transit'
            """)
            rows = c.fetchall()
            return [
                {
                    "letter_id": row[0],
                    "letter_name": row[1],
                    "status": row[2],
                    "scheduled_delivery_datetime": row[3]
                }
                for row in rows
            ]
        
    def get_next_letters_2deliver_summary(self) -> list[dict]:
        """Return summary of all pending letters: letter_id, letter_name, status, scheduled_delivery_datetime."""
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with sqlite3.connect(self.db_path) as conn:
            c = conn.cursor()
            c.execute("""
                SELECT letter_id, letter_name, status, scheduled_delivery_datetime
                FROM letters
                WHERE status = 'in transit' AND scheduled_delivery_datetime >= ?
            """, (now,))
            rows = c.fetchall()
            return [
                {
                    "letter_id": row[0],
                    "letter_name": row[1],
                    "status": row[2],
                    "scheduled_delivery_datetime": row[3]
                }
                for row in rows
            ]
        
    def delete_letter_by_id(self, letter_id: str) -> bool:
        """Delete a letter from the database by its ID."""
        with sqlite3.connect(self.db_path) as conn:
            c = conn.cursor()
            c.execute("DELETE FROM letters WHERE letter_id = ?", (letter_id,))
            conn.commit()
            return c.rowcount > 0

if __name__ == "__main__":
    import sys
    from pprint import pprint
    db_path = "../data/postal.db"
    if len(sys.argv) < 2:
        print("Usage: python3 postalDatabase.py --getAllLetters|--getAllLettersSummary|--getPendingLettersSummary|--delete letter_ID [db_path]")
        sys.exit(1)
    method = sys.argv[1]
    if len(sys.argv) > 2:
        db_path = sys.argv[2] if not method == "--delete" else (sys.argv[3] if len(sys.argv) > 3 else db_path)
    pdb = PostalDatabase(db_path)
    if method == "--getAllLetters":
        pprint(pdb.getAllLetters())
    elif method == "--getAllLettersSummary":
        pprint(pdb.get_all_letters_summary())
    elif method == "--getPendingLettersSummary":
        pprint(pdb.get_pending_letters_summary())
    elif method == "--delete":
        if len(sys.argv) < 3:
            print("Usage: python3 postalDatabase.py --delete letter_ID")
            sys.exit(1)
        letter_id = sys.argv[2]
        success = pdb.delete_letter_by_id(letter_id)
        if success:
            print(f"Letter {letter_id} deleted successfully.")
        else:
            print(f"Letter {letter_id} not found or could not be deleted.")
    else:
        print("Unknown method. Use --getAllLetters, --getAllLettersSummary, "
            "--getPendingLettersSummary, or --delete letter_ID [db_path].")