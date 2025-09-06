import sys
from pathlib import Path
from datetime import datetime
import json
sys.path.append(str(Path(__file__).resolve().parent.parent))
from modules.emailBodyHTMLRenderer import EmailBodyHTMLRenderer

# Paths
template_path = Path("../templates/email_body_template.html")
output_dir = Path("generated_test_files")
output_dir.mkdir(parents=True, exist_ok=True)
postal_info_path = Path("test_data/mock_postal_info.json")

# Load mock postal info
with open(postal_info_path, "r", encoding="utf-8") as f:
    postal_info = json.load(f)

recipient = postal_info["recipient"]
recipient_name = recipient["name"]

# Sample data
created_date = "2025-09-01 10:00:00"
received_date = "2025-09-01 10:05:00"
scheduled_delivery = "2025-09-02 08:00:00"
sent_date = "2025-09-02 08:01:00"

# Render HTML
renderer = EmailBodyHTMLRenderer(str(template_path))
html = renderer.render(
    recipient_name=recipient_name,
    created_date=created_date,
    received_date=received_date,
    scheduled_delivery=scheduled_delivery,
    sent_date=sent_date
)

# Output for inspection
print("=== Email Body HTML Render Test ===")
print(html[:500])  # Print first 500 chars for inspection

# Assertions
assert recipient_name in html, "Recipient name not found in HTML"
assert created_date in html, "Created date not found in HTML"
assert received_date in html, "Received date not found in HTML"
assert scheduled_delivery in html, "Scheduled delivery not found in HTML"
assert sent_date in html, "Sent date not found in HTML"
print("All checks passed.")

# Save rendered HTML to file with ISO name and prefix
iso_now = datetime.now().isoformat(timespec="seconds").replace(":", "-")
filename = f"emailBodyHTMLRendererTest-{iso_now}.html"
output_path = output_dir / filename
with open(output_path, "w", encoding="utf-8") as f:
    f.write(html)
print(f"Rendered HTML saved to {output_path}")