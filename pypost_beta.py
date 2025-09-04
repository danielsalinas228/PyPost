import os
import sys
import json
import random
import shutil
import sqlite3
import smtplib
import datetime
from string import Template
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication

DB_FILE = "letters.db"
POSTAL_DATA = os.path.join("data", "postal_data.json")

LETTERS_TO_SEND = "Letters to Send"
SENT_LETTERS = "Sent Letters"
TEMPLATES_DIR = "templates"

# SMTP config (replace with env vars in production!)
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 465
SMTP_USER = "danielsalinas0228@gmail.com"
SMTP_PASS = "Goo228g&TC"

# Delivery timing
MIN_SECONDS = 1 * 24 * 3600   # 1 day
MAX_SECONDS = 7 * 24 * 3600   # 7 days


# ---------- Utils ----------
def load_postal_data():
    with open(POSTAL_DATA, "r", encoding="utf-8") as f:
        return json.load(f)


def calculate_delivery(min_seconds=MIN_SECONDS, max_seconds=MAX_SECONDS):
    mean = (max_seconds + min_seconds) / 1.8
    stddev = (max_seconds - min_seconds) / 4
    delay = int(random.gauss(mean, stddev))
    delay = max(min_seconds, min(max_seconds, delay))
    scheduled_time = datetime.datetime.now() + datetime.timedelta(seconds=delay)
    return scheduled_time


def render_template(path, **kwargs):
    """Render template using string.Template to avoid CSS {} issues"""
    with open(path, "r", encoding="utf-8") as f:
        template = Template(f.read())
    return template.safe_substitute(**kwargs)


# ---------- DB Setup ----------
def init_db():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS letters (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            recipient_email TEXT NOT NULL,
            subject TEXT NOT NULL,
            content TEXT NOT NULL,
            scheduled_delivery TEXT NOT NULL,
            sent INTEGER DEFAULT 0,
            original_filename TEXT
        )
    """)
    conn.commit()
    conn.close()


# ---------- Email ----------
def send_email(to_email, subject, html_content, letter_html, letter_filename="letter.html"):
    msg = MIMEMultipart()
    msg["From"] = SMTP_USER
    msg["To"] = to_email
    msg["Subject"] = subject

    msg.attach(MIMEText(html_content, "html"))

    attachment = MIMEApplication(letter_html.encode("utf-8"), _subtype="html")
    attachment.add_header("Content-Disposition", "attachment", filename=letter_filename)
    msg.attach(attachment)

    with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
        server.starttls()
        server.login(SMTP_USER, SMTP_PASS)
        server.sendmail(SMTP_USER, to_email, msg.as_string())


# ---------- Letter Logic ----------
def submit_letter(letter_path):
    if not os.path.exists(letter_path):
        print(f"File not found: {letter_path}")
        return

    with open(letter_path, "r", encoding="utf-8") as f:
        content = f.read().strip()

    scheduled_time = calculate_delivery()
    scheduled_str = scheduled_time.strftime("%Y-%m-%d %H:%M")
    subject = f"¡Ha llegado una nueva carta! 📬"
    original_filename = os.path.basename(letter_path)

    # Insert into DB
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("""
        INSERT INTO letters (recipient_email, subject, content, scheduled_delivery, sent, original_filename)
        VALUES (?, ?, ?, ?, 0, ?)
    """, ("lisania@example.com", subject, content, scheduled_str, original_filename))
    conn.commit()
    conn.close()

    # Move processed letter
    os.makedirs(SENT_LETTERS, exist_ok=True)
    shutil.move(letter_path, os.path.join(SENT_LETTERS, original_filename))

    print(f"Letter submitted: {letter_path} (scheduled for {scheduled_str})")

    # Try sending pending letters
    send_pending_letters()


def send_pending_letters():
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("""
        SELECT id, recipient_email, subject, content, scheduled_delivery, original_filename
        FROM letters
        WHERE sent = 0 AND scheduled_delivery <= ?
    """, (now,))
    letters = c.fetchall()

    postal_data = load_postal_data()
    sender = postal_data["sender"]
    recipient = postal_data["recipient"]

    for letter in letters:
        id, recipient_email, subject, content, scheduled_delivery, original_filename = letter
        letter_date = os.path.splitext(original_filename)[0]

        # Render letter HTML
        letter_html = render_template(
            os.path.join(TEMPLATES_DIR, "letter_template.html"),
            letter_date=letter_date,
            subject=subject,
            sender_name=sender["name"],
            sender_address=sender["address_line1"] + ", " + sender["address_line2"],
            sender_city=sender["city_state_zip"],
            sender_country=sender["country"],
            sender_phone=sender["phone"],
            recipient_name=recipient["name"],
            recipient_address=recipient["address_line1"] + ", " + recipient["address_line2"],
            recipient_city=recipient["city_state_zip"],
            recipient_country=recipient["country"],
            recipient_phone=recipient["phone"],
            letter_content=content.strip()
        )

        # Render email body
        email_body = render_template(
            os.path.join(TEMPLATES_DIR, "email_body.html"),
            recipient_name=recipient["name"],
            letter_date=letter_date,
            scheduled_delivery=scheduled_delivery
        )

        # Send email
        attachment_name = f"{letter_date}.html"
        send_email(
            recipient_email,
            subject,
            email_body,
            letter_html,
            letter_filename=attachment_name
        )

        c.execute("UPDATE letters SET sent = 1 WHERE id = ?", (id,))
        print(f"Letter {id} sent to {recipient_email}")

    conn.commit()
    conn.close()


# ---------- Main ----------
if __name__ == "__main__":
    init_db()

    if len(sys.argv) < 2:
        print("Usage: python3 pypost.py <letter.txt>")
        sys.exit(1)

    letter_file = sys.argv[1]
    submit_letter(letter_file)
