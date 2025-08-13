from typing import List
from pydantic import BaseModel

# Exclusive client for Invoice Service

class ClientSummaryItem(BaseModel):
    id: int
    first_name: str
    last_name: str
    email: str
    phone_1: str
    dni: str

class ClientSummaryResponse(BaseModel):
    clients: List[ClientSummaryItem]
    total_count: int