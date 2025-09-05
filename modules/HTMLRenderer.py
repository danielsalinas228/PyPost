from pathlib import Path
from jinja2 import Template
from typing import Any, Dict


class HTMLRenderer:
    def __init__(self, template_path: str):
        self.template_path = Path(template_path)
        self.template = self._load_template()

    def _load_template(self) -> Template:
        with open(self.template_path, "r", encoding="utf-8") as f:
            return Template(f.read())

    def render(self, context: Dict[str, Any]) -> str:
        """
        Renders the template with the given context variables.

        Args:
            context (dict): A dictionary of variables to pass to the template.

        Returns:
            str: The rendered HTML as a string.
        """
        return self.template.render(**context)
