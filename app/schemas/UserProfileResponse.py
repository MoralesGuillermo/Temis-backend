from pydantic import BaseModel
from typing import Optional

class UserProfileResponse(BaseModel):
    id: int
    dni: str
    username: str
    email: str
    first_name: str
    last_name: str
    association: int
    phone: Optional[str]
    city: str
    status: str
    role_name: str
    account_email: str
    subscription_plan: str