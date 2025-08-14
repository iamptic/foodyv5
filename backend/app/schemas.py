from pydantic import BaseModel, field_validator, EmailStr
from typing import Optional

class RegisterPublicIn(BaseModel):
    phone: Optional[str] = None
    email: Optional[EmailStr] = None
    password: Optional[str] = None

    @field_validator('phone', mode='before')
    @classmethod
    def normalize_phone(cls, v):
        if v is None:
            return v
        return v.strip()

class RegisterPublicOut(BaseModel):
    merchant_id: str
    link_code: str

class TelegramLinkIn(BaseModel):
    code: str
    chat_id: int

class HealthOut(BaseModel):
    status: str = "ok"
