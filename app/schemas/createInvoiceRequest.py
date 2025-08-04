from pydantic import BaseModel, Field
from typing import List
from datetime import date

class InvoiceItemInput(BaseModel):
    description: str
    hours_worked: int = Field(..., gt=0)
    hourly_rate: float = Field(..., gt=0)

class CreateInvoiceRequest(BaseModel):
    client_id: int
    emission_date: date
    due_date: date
    items: List[InvoiceItemInput]