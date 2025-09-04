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
                    letter_id, letter_name, creation_datetime, contents, postal_info,
                    received_date, scheduled_delivery_datetime, delivery_datetime, status
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                letter_data['letter_id'],
                letter_data['letter_name'],
                letter_data['creation_datetime'],
                letter_data['contents'],
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
                    "postal_info": json.loads(row[4]),
                    "received_date": row[5],
                    "scheduled_delivery_datetime": row[6],
                    "delivery_datetime": row[7],
                    "status": row[8],
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
                    "postal_info": json.loads(row[4]),
                    "received_date": row[5],
                    "scheduled_delivery_datetime": row[6],
                    "delivery_datetime": row[7],
                    "status": row[8],
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
                ORDER BY creation_datetime DESC
                LIMIT 1
            """)
            row = c.fetchone()
            if row:
                return {
                    "letter_id": row[0],
                    "letter_name": row[1],
                    "creation_datetime": row[2],
                    "contents": row[3],
                    "postal_info": json.loads(row[4]),
                    "received_date": row[5],
                    "scheduled_delivery_datetime": row[6],
                    "delivery_datetime": row[7],
                    "status": row[8],
                }
            return None
        
    def get_next_letter_to_deliver(self) -> Optional[dict]:
        """Retrieve the next letter to be delivered (earliest creation_datetime with status 'in transit')."""
        with sqlite3.connect(self.db_path) as conn:
            c = conn.cursor()
            c.execute("""
                SELECT * FROM letters
                WHERE status = 'in transit'
                ORDER BY creation_datetime ASC
                LIMIT 1
            """)
            row = c.fetchone()
            if row:
                return {
                    "letter_id": row[0],
                    "letter_name": row[1],
                    "creation_datetime": row[2],
                    "contents": row[3],
                    "postal_info": json.loads(row[4]),
                    "received_date": row[5],
                    "scheduled_delivery_datetime": row[6],
                    "delivery_datetime": row[7],
                    "status": row[8],
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
                    "postal_info": json.loads(row[4]),
                    "received_date": row[5],
                    "scheduled_delivery_datetime": row[6],
                    "delivery_datetime": row[7],
                    "status": row[8],
                }
                for row in rows
            ]
        