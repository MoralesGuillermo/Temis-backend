from pydantic import BaseModel, EmailStr
from typing import Optional

class EditProfileRequest(BaseModel):
    email: EmailStr
    first_name: str
    last_name: str
    phone: Optional[str]
    city: str

class EditProfileResponse(BaseModel):
    id: int
    email: str
    first_name: str
    last_name: str
    phone: Optional[str]
    city: str
    message: str

class ChangePasswordRequest(BaseModel):
    current_password: str
    new_password: str

class ChangePasswordResponse(BaseModel):
    message: str