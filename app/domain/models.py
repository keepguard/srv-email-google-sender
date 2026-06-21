
from pydantic import BaseModel, EmailStr, Field
from typing import Optional

class EmailPayload(BaseModel):
    to: EmailStr
    subject: str = Field(..., min_length=1)
    message: Optional[str] = None
    html: Optional[str] = None
    cc: Optional[str] = None  # CSV para compatibilidade com seu payload
    replyTo: Optional[EmailStr] = None
