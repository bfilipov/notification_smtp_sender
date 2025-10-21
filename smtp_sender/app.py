from typing import Annotated

from dotenv import load_dotenv
from fastapi import FastAPI, BackgroundTasks, Header
from starlette.requests import Request

from smtp_sender.models import CustomEmailSchema
from smtp_sender.sender import send_custom_email

app = FastAPI(title="Email Service")

@app.post("/send-email", status_code=202)
async def send_email_endpoint(
        email: CustomEmailSchema,
        request: Request,
        background_tasks: BackgroundTasks,
        sec: Annotated[str | None, Header()] = None
):
    """
    Send an email asynchronously
    - Returns immediately (202 Accepted)
    - Simple security check to filter mass bots
    - Actual sending happens in background
    """
    print('here')
    background_tasks.add_task(send_custom_email, email, request, sec)
    return {"message": "Email sending started"}
