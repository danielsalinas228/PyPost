import os 
import base64
from pathlib import Path

from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request

from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders


class EmailSender:
    def __init__(self,
                client_secret_file_path: str,
                token_folder_path: str,
                api_name: str,
                api_version: str,
                *scopes: list[str],
                prefix: str=''):
        self.service = self.create_service(client_secret_file_path,
                                           token_folder_path,
                                           api_name,
                                           api_version,
                                           scopes,
                                           prefix)

    def create_service(self, client_secret_file_path: str,
                       token_folder_path: str,
                       api_name: str,
                       api_version: str,
                       *scopes: list[str],
                       prefix=''):
        CLIENT_SECRET_FILE = client_secret_file_path
        API_SERVICE_NAME = api_name
        API_VERSION = api_version
        SCOPES = [scope for scope in scopes[0]]

        creds = None
        token_dir = token_folder_path
        token_file = f'token{API_SERVICE_NAME}_{API_VERSION}{prefix}.json'
        token_full_path = os.path.join(token_dir, token_file)

        # Check if token dir exists first, if not, create the folder
        if not os.path.exists(token_dir):
            os.makedirs(token_dir, exist_ok=True)
        
        if os.path.exists(token_full_path):
            creds = Credentials.from_authorized_user_file(token_full_path, SCOPES)

        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    CLIENT_SECRET_FILE, SCOPES
                )
                creds = flow.run_local_server(port=0)
            
            with open(token_full_path, 'w') as token:
                token.write(creds.to_json())

        try:
            service = build(API_SERVICE_NAME,
                            API_VERSION,
                            credentials=creds,
                            static_discovery=False)
            print(API_SERVICE_NAME, API_VERSION, 'Service created successfully')
            return service
        except Exception as e:
            print(e)
            print(f'Failed to create service instance for {API_SERVICE_NAME}')
            if os.path.exists(token_full_path):
                os.remove(token_full_path)
            return None
        

    def send_email(self,
                   to: str,
                   subject: str,
                   body: str, 
                   body_type: str='plain',
                   attachment_paths: list[str]=None,
                   bcc: str=None):

        message = MIMEMultipart()
        message['to'] = to
        message['subject'] = subject
        if bcc is not None: message['bcc'] = bcc

        if body_type.lower() not in ['plain', 'html']:
            raise ValueError("body_type must be either 'plain' or 'html'")
        
        message.attach(MIMEText(body, body_type.lower()))

        if attachment_paths:
            for attachment_path in attachment_paths:
                if os.path.exists(attachment_path):
                    filename = os.path.basename(attachment_path)

                    with open(attachment_path, "rb") as attachment:
                        part = MIMEBase("application", "octet-stream")
                        part.set_payload(attachment.read())

                    encoders.encode_base64(part)

                    part.add_header(
                        "Content-Disposition",
                        f"attachment; filename= {filename}",
                    )

                    message.attach(part)
                else:
                    raise FileNotFoundError(f"{attachment_path} not found")
            
        raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode('utf-8')
        
        sent_message = self.service.users().messages().send(
            userId='me',
            body = {'raw': raw_message}
        ).execute()

        return sent_message