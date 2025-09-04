import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parent.parent))
from modules.emailSender import EmailSender

CLIENT_SECRET_FILE = '../Secrets/client_secret.json'
TOKEN_FOLDER_PATH = '../Secrets'
API_SERVICE_NAME = 'gmail'
API_VERSION = 'v1'
SCOPES = ['https://mail.google.com/']

emailSender = EmailSender(
    CLIENT_SECRET_FILE,
    TOKEN_FOLDER_PATH,
    API_SERVICE_NAME,
    API_VERSION,
    *SCOPES
)

to_address = 'dannydaniiel10@gmail.com'
email_subject = 'This is a test'

# Read HTML content from file
html_file_path = '../templates/29-08-2025.html'
with open('../templates/email_body_template.html', 'r', encoding='utf-8') as f:
    email_body = f.read()

attch_dir = [html_file_path]

print(dir(emailSender.service))
print(emailSender.send_email(
    to_address,
    email_subject,
    email_body,
    body_type='html',
    attachment_paths=attch_dir
))