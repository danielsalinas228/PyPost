import sys
from pathlib import Path
from datetime import datetime
import json
sys.path.append(str(Path(__file__).resolve().parent.parent))
from modules.HTMLRenderer import HTMLRenderer

# Output directory
output_dir = Path("generated_test_files")
output_dir.mkdir(parents=True, exist_ok=True)

# --- Test 1: Letter Template ---
postal_info_path = Path("test_data/mock_postal_info.json")
letter_path = Path("../LettersToSend/01-09-2025.txt")
letter_template_path = Path("../templates/letter_template.html")

with open(postal_info_path, "r", encoding="utf-8") as f:
    postal_info = json.load(f)
with open(letter_path, "r", encoding="utf-8") as f:
    letter_contents = f.read()

sender = postal_info["sender"]
recipient = postal_info["recipient"]
letter_name = "2025-09-01"

letter_context = {
    "letter_name": letter_name,
    "letter_contents": letter_contents,
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

letter_renderer = HTMLRenderer(str(letter_template_path))
letter_html = letter_renderer.render(letter_context)

print("=== HTMLRenderer Letter Template Test ===")
print(letter_html[:500])

assert sender["name"] in letter_html, "Sender name not found in HTML"
assert recipient["name"] in letter_html, "Recipient name not found in HTML"
assert letter_contents.strip() in letter_html, "Letter contents not found in HTML"
assert letter_name in letter_html, "Letter date not found in HTML"
print("Letter template checks passed.")

iso_now = datetime.now().isoformat(timespec="seconds").replace(":", "-")
letter_filename = f"HTMLRendererTest-letter-{iso_now}.html"
letter_output_path = output_dir / letter_filename
with open(letter_output_path, "w", encoding="utf-8") as f:
    f.write(letter_html)
print(f"Letter HTML saved to {letter_output_path}")

# --- Test 2: Email Body Template ---
email_body_template_path = Path("../templates/email_body_template.html")
email_body_context = {
    "recipient_name": recipient.get("name", ""),
    "created_date": "2025-09-01 10:00:00",
    "received_date": "2025-09-01 10:05:00",
    "scheduled_delivery": "2025-09-02 08:00:00",
    "sent_date": "2025-09-02 08:01:00"
}

email_body_renderer = HTMLRenderer(str(email_body_template_path))
email_body_html = email_body_renderer.render(email_body_context)

print("\n=== HTMLRenderer Email Body Template Test ===")
print(email_body_html[:500])

assert email_body_context["recipient_name"] in email_body_html, "Recipient name not found in email body HTML"
assert email_body_context["created_date"] in email_body_html, "Created date not found in email body HTML"
assert email_body_context["received_date"] in email_body_html, "Received date not found in email body HTML"
assert email_body_context["scheduled_delivery"] in email_body_html, "Scheduled delivery not found in email body HTML"
assert email_body_context["sent_date"] in email_body_html, "Sent date not found in email body HTML"
print("Email body template checks passed.")

email_body_filename = f"HTMLRendererTest-emailBody-{iso_now}.html"
email_body_output_path = output_dir / email_body_filename
with open(email_body_output_path, "w", encoding="utf-8") as f:
    f.write(email_body_html)
print(f"Email body HTML saved to {email_body_output_path}")