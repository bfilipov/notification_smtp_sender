from typing import Annotated

from fastapi import FastAPI, BackgroundTasks, Header
from fastapi.middleware.cors import CORSMiddleware
from starlette.requests import Request

from smtp_sender.models import CustomEmailSchema
from smtp_sender.sender import send_custom_email

app = FastAPI(title="Email Service")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://advokatvidin.com"],
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["user-agent", "accept-language", "origin", "sec", "content-type"],
    expose_headers=["*"],
)


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
    background_tasks.add_task(send_custom_email, email, request, sec)
    return {"message": "Email sending started"}


@app.get("/health")
async def health_check():
    """Health check endpoint for Docker"""
    return {"status": "healthy", "service": "email-sender"}
