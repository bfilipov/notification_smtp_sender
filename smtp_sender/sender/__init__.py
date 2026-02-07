import base64
import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from fastapi import HTTPException
from starlette.requests import Request

from smtp_sender.models import CustomEmailSchema


SUBSCRIBERS = [os.getenv('TEST_ADMIN_EMAIL'), ]
SUBJECT = 'Ново запитване през сайта!'


class EnvSMTPConfig:
    def __init__(self):
        self.SMTP_SERVER = os.getenv('SMTP_SERVER')
        self.PORT = int(os.getenv('SMTP_PORT'))
        self.SMTP_PASSWORD = os.getenv('SMTP_PASSWORD')
        self.SENDER_EMAIL = os.getenv('SENDER_EMAIL')
        self.SMTP_USERNAME = os.getenv('SMTP_USERNAME')


conf = EnvSMTPConfig()


def send_email(to_emails: list, subject, body):
    smtp_server = conf.SMTP_SERVER
    port = conf.PORT
    sender_email = conf.SENDER_EMAIL
    smtp_username = conf.SMTP_USERNAME
    smtp_password = conf.SMTP_PASSWORD

    msg = MIMEMultipart()
    msg["From"] = sender_email
    msg["To"] = ", ".join(to_emails)
    msg["Subject"] = subject
    msg.attach(MIMEText(body, "plain"))

    try:
        server = smtplib.SMTP(smtp_server, port)
        server.starttls()
        server.login(smtp_username, smtp_password)
        server.sendmail(sender_email, to_emails, msg.as_string())
        server.quit()
        print("Email sent!")
    except Exception as e:
        print(f"Error: {e}")


def check_security(request: Request, sec_token):
    """
    Very simple security check implemented on frontend and backend to filter mainstream bots.

    Expect {ua}|{lang}|{origin} encoded in base64.
    """

    ua = request.headers.get("user-agent", "")
    lang = request.headers.get("accept-language", "")
    origin = request.headers.get("origin", request.base_url.hostname)  # fallback for non-CORS

    expected_payload = f"{ua}|{lang}|{origin}"
    expected_token = base64.b64encode(expected_payload.encode()).decode().replace("=", "")

    print(f'Sec token received: {sec_token}')
    print(f'Sec token Calculated: {expected_token}')

    if sec_token != expected_token:
        raise HTTPException(status_code=403, detail="Invalid security token")


def send_custom_email(
        email: CustomEmailSchema,
        request: Request,
        sec_token: str,
):
    """Actual email sending logic (runs in background)"""
    try:
        print(SUBSCRIBERS)
        check_security(request, sec_token)
        send_email(SUBSCRIBERS, SUBJECT, email.body)
    except Exception as e:
        print(f"Email sending failed: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to send email")
