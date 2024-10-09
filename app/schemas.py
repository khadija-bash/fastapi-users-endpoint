from pydantic import BaseModel, Field, EmailStr
from typing import Optional
from uuid import UUID
from datetime import datetime

class UserBase(BaseModel):
    username: Optional[str] = None
    name: Optional[str] = None
    email: Optional[str] = None

class UserCreate(UserBase):
    email: Optional[EmailStr] = None
    sms: Optional[str] = None

class UserDisplay(UserBase):
    id: UUID
    created: datetime
    lastseen: Optional[datetime] = None

    class Config:
        orm_mode = True
        
