from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from email.mime.text import MIMEText
import base64


def get_gmail_service():
    creds = Credentials.from_authorized_user_file(
        "token.json", ["https://www.googleapis.com/auth/gmail.send"]
    )
    return build("gmail", "v1", credentials=creds)


def send_email_tool(to: str, subject: str, body: str):
    service = get_gmail_service()

    message = MIMEText(body)
    message["to"] = to
    message["subject"] = subject
    raw = base64.urlsafe_b64encode(message.as_bytes()).decode()

    sent = service.users().messages().send(userId="me", body={"raw": raw}).execute()

    return {"status": "sent", "id": sent["id"]}
