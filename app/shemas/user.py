from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime

# User base schema
class UserBase(BaseModel):
    email: EmailStr
    username: str
    full_name: Optional[str] = None

# Schema for creating a user
class UserCreate(UserBase):
    password: str = Field(..., min_length=8)
    role: str

# Schema for updating a user
class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    username: Optional[str] = None
    full_name: Optional[str] = None
    password: Optional[str] = None
    role: Optional[str] = None
    is_active: Optional[bool] = None

# Schema for returning user information
class UserInDB(UserBase):
    id: str
    role: str
    is_active: bool
    created_at: datetime
    updated_at: datetime

# Schema for public user information
class User(UserInDB):
    pass

    class Config:
        from_attributes = True