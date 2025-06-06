from pydantic import BaseModel, EmailStr
from typing import Optional


class UserCreate(BaseModel):
    first_name: str
    last_name: str
    email: Optional[EmailStr] = None
    phone_number: Optional[str] = None
    username: Optional[str] = None
    password: str

    class Config:
        anystr_strip_whitespace = True


class UserOut(BaseModel):
    id: int
    first_name: str
    last_name: str
    email: Optional[EmailStr]
    phone_number: Optional[str]
    username: Optional[str]
    email_verified: bool

    class Config:
        orm_mode = True

class UserUpdate(BaseModel):
    first_name: Optional[str]
    last_name: Optional[str]
    phone_number: Optional[str]
    username: Optional[str]

    class Config:
        anystr_strip_whitespace = True

class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = 'bearer'


class TokenRefresh(BaseModel):
    refresh_token: str


class EmailSchema(BaseModel):
    email: EmailStr


class PasswordResetConfirm(BaseModel):
    token: str
    new_password: str