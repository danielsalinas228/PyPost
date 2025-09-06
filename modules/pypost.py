PROJECT_ROOT = Path(__file__).resolve().parent.parent

import json
import sys
import random
import uuid
from pathlib import Path
from datetime import datetime, timedelta

from modules.postalDatabase import PostalDatabase
from modules.HTMLRenderer import HTMLRenderer
from modules.emailSender import EmailSender
from modules.aiTextGenerator import AiTextGenerator

class PyPost:
    def __init__(self,
                 db_path: str = PROJECT_ROOT / "data/postal.db",
                 letter_template_path: str = PROJECT_ROOT / "templates/letter_template.html",
                 email_body_template_path: str = PROJECT_ROOT / "templates/email_body_template.html",
                 client_secret_file: str = PROJECT_ROOT / "Secrets/client_secret.json",
                 token_folder_path: str = PROJECT_ROOT / "Secrets",
                 postal_info_path: str = PROJECT_ROOT / "data/postal_info.json",
                 api_key_path: str = PROJECT_ROOT / "Secrets/openApi_key.json",
                 email_subject_prompt_template: str = PROJECT_ROOT / "templates/email_subject_prompt_template.txt"):
        self.db_path = db_path
        self.db = PostalDatabase(db_path)
        self.letter_renderer = HTMLRenderer(letter_template_path)
        self.email_body_renderer = HTMLRenderer(email_body_template_path)
        self.email_sender = EmailSender(
            client_secret_file,
            token_folder_path,
            "gmail",
            "v1",
            "https://mail.google.com/"
        )
        api_key_path = Path(api_key_path)
        with open(api_key_path, "r", encoding="utf-8") as f:
            api_data = json.load(f)
            api_key = api_data["api_key"]
        self.postal_info_path = postal_info_path
        self.ai_text_generator = AiTextGenerator(openApi_key=api_key)
        with open(email_subject_prompt_template, "r", encoding="utf-8") as f:
            self.email_subject_prompt = f.read()
        self.deault_email_subject = "💌 Una carta te espera"

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

    def render_letter_template(self, letter_content: str, sender: dict, recipient: dict, letter_name: str) -> str:
        context = {
            "letter_name": letter_name,
            "letter_contents": letter_content,
            "sender_name": sender.get("name", ""),
            "sender_address_line1": sender.get("address_line1", ""),
            "sender_address_line2": sender.get("address_line2", ""),
            "sender_zip": sender.get("zip", ""),
            "sender_city_state": sender.get("city_state", ""),
            "sender_country": sender.get("country", ""),
            "sender_phone": sender.get("phone", ""),
            "recipient_name": recipient.get("name", ""),
            "recipient_address_line1": recipient.get("address_line1", ""),
            "recipient_address_line2": recipient.get("address_line2", ""),
            "recipient_zip": recipient.get("zip", ""),
            "recipient_city_state": recipient.get("city_state", ""),
            "recipient_country": recipient.get("country", ""),
            "recipient_phone": recipient.get("phone", "")
        }
        return self.letter_renderer.render(context)

    def render_email_body(self, letter: dict) -> str:
        context = {
            "recipient_name": letter["postal_info"]["recipient"]["name"],
            "created_date": letter["creation_datetime"],
            "received_date": letter["received_date"],
            "scheduled_delivery": letter["scheduled_delivery_datetime"],
            "sent_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        return self.email_body_renderer.render(context)

    def submit_letter(self, letter_file_path: str) -> str:
        postal_data = self.load_postal_data()
        sender = postal_data["sender"]
        recipient = postal_data["recipient"]

        with open(letter_file_path, "r", encoding="utf-8") as f:
            letter_content = f.read()

        now_iso = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        last_letter = self.db.get_last_submitted_letter()
        prev_scheduled_datetime = last_letter["scheduled_delivery_datetime"] if last_letter else None
        scheduled_delivery = self.calculate_delivery_datetime(prev_scheduled_datetime)

        letter_name = Path(letter_file_path).stem
        html_contents = self.render_letter_template(letter_content, sender, recipient, letter_name)

        letter_data = {
            "letter_id": str(uuid.uuid4()),
            "letter_name": letter_name,
            "creation_datetime": letter_name, # Using letter_name as creation date
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
        
        # Generate email subject with AI, fallback to default if fails
        try:
            subject = self.ai_text_generator.generate(self.email_subject_prompt)
        except Exception as e:
            print(f"AI subject generation failed: {e}")
            subject = self.deault_email_subject
        
        body_html = self.render_email_body(letter)

        # Save the HTML letter to a temp file for attachment
        temp_html_path = PROJECT_ROOT / f"temp_{letter_id}.html"
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
    #TODO: delete lines, pypost should be used as a module
    if len(sys.argv) != 2:
        print("Usage: python3 pypost.py path_to_letter.txt")
        sys.exit(1)
    letter_path = sys.argv[1]
    pypost = PyPost()
    pypost.submit_letter(letter_path)
    sent_letters_ids = pypost.send_pending_letters()
    if sent_letters_ids:
        print(f"Letters sent successfully!: \n{', '.join(sent_letters_ids)}")
    else:
        print("Failed to send letter.")