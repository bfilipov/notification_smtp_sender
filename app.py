import os

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, BackgroundTasks
from pydantic import BaseModel

from sender import send_email

app = FastAPI(title="Email Service")

load_dotenv()
TEST_ADMIN_EMAIL = os.getenv('TEST_ADMIN_EMAIL')


class CustomEmailSchema(BaseModel):
    body: str


SUBSCRIBERS_LIST = TEST_ADMIN_EMAIL
SUBJECT = 'Ново запитване през сайта!'


def send_custom_email(email: CustomEmailSchema):
    """Actual email sending logic (runs in background)"""
    try:
        send_email(SUBSCRIBERS_LIST, SUBJECT, email.body)
    except Exception as e:
        print(f"Email sending failed: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to send email")


@app.post("/send-email", status_code=202)
async def send_email_endpoint(
        email: CustomEmailSchema,
        background_tasks: BackgroundTasks
):
    """
    Send an email asynchronously
    - Returns immediately (202 Accepted)
    - Actual sending happens in background
    """
    background_tasks.add_task(send_custom_email, email)
    return {"message": "Email sending started"}
