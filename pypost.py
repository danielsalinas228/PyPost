from datetime import datetime, timedelta
import json
import sys
import random
from pathlib import Path

from modules.postalDatabase import PostalDatabase
from modules.letterHTMLRenderer import LetterHTMLRenderer
from modules.emailBodyHTMLRenderer import EmailBodyHTMLRenderer
from modules.emailSender import EmailSender

class PyPost:
    def __init__(self,
                 db_path: str = "data/postal.db",
                 letter_template_path: str = "templates/letter_template.html",
                 email_body_template_path: str = "templates/email_body_template.html",
                 client_secret_file: str = "Secrets/client_secret.json",
                 token_folder_path: str = "Secrets",
                 postal_info_path: str = "data/postal_info.json"):
        self.db_path = db_path
        self.db = PostalDatabase(db_path)
        self.letter_renderer = LetterHTMLRenderer(letter_template_path)
        self.email_body_renderer = EmailBodyHTMLRenderer(email_body_template_path)
        self.email_sender = EmailSender(
            client_secret_file,
            token_folder_path,
            "gmail",
            "v1",
            "https://mail.google.com/"
        )
        self.postal_info_path = postal_info_path

    def load_postal_data(self) -> dict:
        with open(self.postal_info_path, "r", encoding="utf-8") as f:
            return json.load(f)

    def calculate_delivery_datetime(self, previous_schedule_datetime_iso: str = None) -> str:
        now = datetime.now()
        base_dt = now
        if previous_schedule_datetime_iso:
            try:
                prev_dt = datetime.fromisoformat(previous_schedule_datetime_iso)
                if prev_dt > now:
                    base_dt = prev_dt
            except Exception:
                pass
        min_seconds = 86400      # 1 day
        max_seconds = 259200     # 3 days
        skew = random.betavariate(2, 5)
        offset_seconds = int(min_seconds + skew * (max_seconds - min_seconds))
        scheduled_dt = base_dt + timedelta(seconds=offset_seconds)
        return scheduled_dt.strftime("%Y-%m-%d %H:%M:%S")

    def render_template(self, letter_content: str, sender: dict, recipient: dict, letter_date: str) -> str:
        return self.letter_renderer.render(letter_content, sender, recipient, letter_date)

    def submit_letter(self, letter_file_path: str) -> str:
        postal_data = self.load_postal_data()
        sender = postal_data["sender"]
        recipient = postal_data["recipient"]

        with open(letter_file_path, "r", encoding="utf-8") as f:
            letter_content = f.read()

        now_iso = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        last_letter = self.db.get_last_submitted_letter()
        prev_scheduled = last_letter["scheduled_delivery_datetime"] if last_letter else None
        scheduled_delivery = self.calculate_delivery_datetime(prev_scheduled)

        html_contents = self.render_template(letter_content, sender, recipient, now_iso)

        letter_data = {
            "letter_id": str(int(datetime.now().timestamp() * 1000)),
            "letter_name": Path(letter_file_path).stem,
            "creation_datetime": now_iso,
            "contents": letter_content,
            "html_contents": html_contents,
            "postal_info": postal_data,
            "received_date": now_iso,
            "scheduled_delivery_datetime": scheduled_delivery,
            "delivery_datetime": None,
            "status": "in transit"
        }
        self.db.insert_letter(letter_data)
        return letter_data["letter_id"]

    def send_email(self, letter_id: str) -> bool:
        letter = self.db.get_letter_by_id(letter_id)
        if not letter:
            print(f"Letter ID {letter_id} not found.")
            return False

        recipient_email = letter["postal_info"]["recipient"]["email"]
        subject = f"Carta PyPost: {letter['letter_name']} ({letter['creation_datetime']})"
        body_html = self.email_body_renderer.render(
            recipient_name=letter["postal_info"]["recipient"]["name"],
            created_date=letter["creation_datetime"],
            received_date=letter["received_date"],
            scheduled_delivery=letter["scheduled_delivery_datetime"],
            sent_date=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        )

        # Save the HTML letter to a temp file for attachment
        temp_html_path = f"temp_{letter_id}.html"
        with open(temp_html_path, "w", encoding="utf-8") as f:
            f.write(letter["html_contents"])

        try:
            self.email_sender.send_email(
                to=recipient_email,
                subject=subject,
                body=body_html,
                body_type='html',
                attachment_paths=[temp_html_path]
            )
            # Update letter status and delivery_datetime
            self.db.update_letter_status(letter_id, "delivered", delivery_datetime=datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
            print(f"Letter {letter_id} sent to {recipient_email}.")
            return True
        except Exception as e:
            print(f"Failed to send letter {letter_id}: {e}")
            return False
        finally:
            # Clean up temp file
            Path(temp_html_path).unlink(missing_ok=True)

    def send_pending_letters(self) -> list:
        pending_letters = self.db.get_pending_letters()
        sent_ids = []
        for letter in pending_letters:
            if self.send_email(letter["letter_id"]):
                sent_ids.append(letter["letter_id"])
        return sent_ids

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python3 pypost.py path_to_letter.txt")
        sys.exit(1)
    letter_path = sys.argv[1]
    pypost = PyPost()
    letter_id = pypost.submit_letter(letter_path)
    sent = pypost.send_email(letter_id)
    if sent:
        print("Letter sent successfully!")
    else:
        print("Failed to send letter.")