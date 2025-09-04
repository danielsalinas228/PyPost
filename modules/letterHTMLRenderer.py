from pathlib import Path
from jinja2 import Template

class LetterHTMLRenderer:
    def __init__(self, template_path: str):
        self.template_path = template_path
        self.template = self._load_template()

    def _load_template(self) -> Template:
        with open(self.template_path, "r", encoding="utf-8") as f:
            return Template(f.read())

    def render(self, letter_contents: str, sender: dict, recipient: dict, letter_date: str) -> str:
        html = self.template.render(
            letter_date=letter_date,
            letter_contents=letter_contents,
            sender_name=sender.get("name", ""),
            sender_address_line1=sender.get("address_line1", ""),
            sender_address_line2=sender.get("address_line2", ""),
            sender_zip=sender.get("zip", ""),
            sender_city_state=sender.get("city_state", ""),
            sender_country=sender.get("country", ""),
            sender_phone=sender.get("phone", ""),
            recipient_name=recipient.get("name", ""),
            recipient_address_line1=recipient.get("address_line1", ""),
            recipient_address_line2=recipient.get("address_line2", ""),
            recipient_zip=recipient.get("zip", ""),
            recipient_city_state=recipient.get("city_state", ""),
            recipient_country=recipient.get("country", ""),
            recipient_phone=recipient.get("phone", "")
        )
        return html
