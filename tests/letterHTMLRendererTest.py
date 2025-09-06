import sys
from pathlib import Path
from datetime import datetime
sys.path.append(str(Path(__file__).resolve().parent.parent))
from modules.letterHTMLRenderer import LetterHTMLRenderer
import json

# Paths
postal_info_path = Path("test_data/mock_postal_info.json")
letter_path = Path("../LettersToSend/01-09-2025.txt")
template_path = Path("../templates/letter_template.html")
output_dir = Path("generated_test_files")
output_dir.mkdir(parents=True, exist_ok=True)

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

# Save rendered HTML to file with ISO name and prefix
iso_now = datetime.now().isoformat(timespec="seconds").replace(":", "-")
filename = f"letterHTMLRendererTest-{iso_now}.html"
output_path = output_dir / filename
with open(output_path, "w", encoding="utf-8") as f:
    f.write(html)
print(f"Rendered HTML saved to {output_path}")