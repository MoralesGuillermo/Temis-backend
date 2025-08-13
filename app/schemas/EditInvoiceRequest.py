from pydantic import BaseModel, Field
from typing import List
from datetime import date

class InvoiceItemEdit(BaseModel):
    id: int
    description: str
    hours_worked: int = Field(..., gt=0)
    hourly_rate: float = Field(..., gt=0)

class EditInvoiceRequest(BaseModel):
    invoice_id: int
    emission_date: date
    due_date: date
    items: List[InvoiceItemEdit]

class EditInvoiceResponse(BaseModel):
    id: int
    emission_date: str
    due_date: str
    message: str
    updated_items: List[InvoiceItemEdit]