from typing import List
from pydantic import BaseModel

class InvoiceSummaryItem(BaseModel):
    id: int
    invoice_number: int
    client_name: str
    emission_date: str
    due_date: str
    status: str
    total_amount: float

class InvoiceSummaryResponse(BaseModel):
    invoices: List[InvoiceSummaryItem]
    total_count: int