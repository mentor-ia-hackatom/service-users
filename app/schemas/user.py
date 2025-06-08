from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime

class UserBase(BaseModel):
    email: EmailStr
    full_name: Optional[str] = None

class UserCreate(UserBase):
    password: str

class UserUpdate(UserBase):
    password: Optional[str] = None

class UserInDBBase(UserBase):
    uuid: str
    is_active: bool
    created_at: int
    updated_at: Optional[int] = None

    class Config:
        from_attributes = True

class User(UserInDBBase):
    full_name: str
    email: str
    

class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str

class TokenPayload(BaseModel):
    sub: Optional[str] = None 

class UserGetOrCreate(UserBase):
    uuid: str