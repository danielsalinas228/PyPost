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

if __name__ == "__main__":
    import json

    # Paths
    postal_info_path = Path("../data/postal_info.json")
    letter_path = Path("../LettersToSend/01-09-2025.txt")
    template_path = Path("../templates/letter_template.html")

    # Load postal info
    with open(postal_info_path, "r", encoding="utf-8") as f:
        postal_info = json.load(f)

    # Load letter contents
    with open(letter_path, "r", encoding="utf-8") as f:
        letter_contents = f.read()

    # Prepare data
    sender = postal_info["sender"]
    recipient = postal_info["recipient"]
    letter_date = "2025-09-01"

    # Render HTML
    renderer = LetterHTMLRenderer(str(template_path))
    html = renderer.render(letter_contents, sender, recipient, letter_date)

    # Test output
    print("=== HTML Render Test ===")
    print(html[:500])  # Print first 500 chars for inspection

    # Optionally, check for expected substrings
    assert sender["name"] in html, "Sender name not found in HTML"
    assert recipient["name"] in html, "Recipient name not found in HTML"
    assert letter_contents.strip() in html, "Letter contents not found in HTML"
    assert letter_date in html, "Letter date not found in HTML"
    print("All checks passed.")

    # Save rendered HTML to file
    output_path = Path("../LettersToSend/01-09-2025.html")
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"Rendered HTML saved to {output_path}")