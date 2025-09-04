import os
from pypost_beta import load_postal_data, render_template, send_email

TEMPLATES_DIR = "templates"

# --- Load sender/recipient data ---
postal_data = load_postal_data()
sender = postal_data["sender"]
recipient = postal_data["recipient"]

# --- Test letter content ---
test_content = """Hola Lisania,

Este es un mensaje de prueba de PyPost. ✉️
Solo estamos comprobando que el envío funciona correctamente.
Disfruta tu carta de prueba!"""

subject = "Carta de prueba PyPost 📬"
letter_date = "prueba_carta"  # <-- the original txt filename (without .txt)

# --- Render letter HTML ---
letter_html = render_template(
    os.path.join(TEMPLATES_DIR, "letter_template.html"),
    letter_date=letter_date,  # <-- pass this to avoid KeyError
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
    letter_content=test_content
)

# --- Render email body ---
email_body = render_template(
    os.path.join(TEMPLATES_DIR, "email_body.html"),
    recipient_name=recipient["name"],
    letter_date=letter_date,  # <-- also pass here for consistency
    scheduled_delivery="03-09-2025"
)

# --- Send email ---
send_email(
    to_email="danielsalinas228@outlook.com",  # replace with actual recipient
    subject=subject,
    html_content=email_body,
    letter_html=letter_html,
    letter_filename=f"{letter_date}.html"
)

print("Test email sent!")
