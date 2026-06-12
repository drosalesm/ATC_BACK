from pydantic import BaseModel, EmailStr
from typing import Optional

class UserCreate(BaseModel):
    username: str
    email: str  # Ensures a valid email format
    password: str
    role: str
    name: Optional[str] = None
    status: Optional[str] = "available"  # Default status is "active"

class UserUpdate(BaseModel):
    username: Optional[str] = None
    email: Optional[str] = None
    role: Optional[str] = None
    name: Optional[str] = None
    status: Optional[str] = None