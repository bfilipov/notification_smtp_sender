from pydantic import BaseModel


class CustomEmailSchema(BaseModel):
    body: str
