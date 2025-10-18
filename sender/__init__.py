import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from dotenv import load_dotenv


class EnvSMTPConfig:
    def __init__(self):
        load_dotenv()
        self.SMTP_SERVER = os.getenv('SMTP_SERVER')
        self.PORT = int(os.getenv('PORT'))
        self.SMTP_PASSWORD = os.getenv('SMTP_PASSWORD')
        self.SENDER_EMAIL = os.getenv('SENDER_EMAIL')
        self.SMTP_USERNAME = os.getenv('SMTP_USERNAME')


conf = EnvSMTPConfig()


def send_email(to_email, subject, body):
    smtp_server = conf.SMTP_SERVER
    port = conf.PORT
    sender_email = conf.SENDER_EMAIL
    smtp_username = conf.SMTP_USERNAME
    smtp_password = conf.SMTP_PASSWORD

    msg = MIMEMultipart()
    msg["From"] = sender_email
    msg["To"] = to_email
    msg["Subject"] = subject
    msg.attach(MIMEText(body, "plain"))

    try:
        server = smtplib.SMTP(smtp_server, port)
        server.starttls()
        server.login(smtp_username, smtp_password)
        server.sendmail(sender_email, to_email, msg.as_string())
        server.quit()
        print("Email sent!")
    except Exception as e:
        print(f"Error: {e}")


# test
if __name__ == '__main__':
    send_email('bogo.bace@gmail.com', 'test subject', 'test body')
