from pydantic import BaseModel, EmailStr
from typing import Optional, List

class User(BaseModel):
    email: EmailStr
    password: str

class UpdateUser(BaseModel):
    new_email: Optional[EmailStr] = None
    new_password: Optional[str] = None
    wishlist: Optional[List[str]] = None
