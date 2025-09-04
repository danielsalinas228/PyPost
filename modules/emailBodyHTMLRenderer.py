from pathlib import Path
from jinja2 import Template

class EmailBodyHTMLRenderer:
    def __init__(self, template_path: str):
        self.template_path = template_path
        self.template = self._load_template()

    def _load_template(self) -> Template:
        with open(self.template_path, "r", encoding="utf-8") as f:
            return Template(f.read())

    def render(self,
               recipient_name: str,
               created_date: str,
               received_date: str,
               scheduled_delivery: str,
               sent_date: str) -> str:
        html = self.template.render(
            recipient_name=recipient_name,
            created_date=created_date,
            received_date=received_date,
            scheduled_delivery=scheduled_delivery,
            sent_date=sent_date
        )
        return html