from pydantic import BaseModel, EmailStr, Field
from typing import Optional

class RegisterRequest(BaseModel):
    dni: str = Field(..., min_length=13, max_length=30, description="DNI del usuario")
    username: str = Field(..., min_length=3, max_length=24, description="Nombre de usuario único")
    password: str = Field(..., min_length=6, description="Contraseña del usuario")
    email: EmailStr
    first_name: str = Field(..., min_length=1, max_length=50)
    last_name: str = Field(..., min_length=1, max_length=50)
    association: int = Field(..., description="Número de colegiatura")
    phone: Optional[str] = Field(None, max_length=20)
    city: str = Field(..., description="Ciudad del usuario")

class RegisterResponse(BaseModel):
    id: int
    dni: str
    username: str
    email: str
    first_name: str
    last_name: str
    association: int
    phone: Optional[str]
    city: str
    message: str