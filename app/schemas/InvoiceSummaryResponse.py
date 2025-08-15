from typing import List
from pydantic import BaseModel


class InvoiceItemDetail(BaseModel):
    id: int
    description: str
    hours_worked: int
    hourly_rate: float
    item_total: float

class InvoiceSummaryItem(BaseModel):
    id: int
    invoice_number: int
    client_name: str
    client_email: str
    case_number: str
    emission_date: str
    due_date: str
    status: str
    total_amount: float
    items: List[InvoiceItemDetail]

class InvoiceSummaryResponse(BaseModel):
    invoices: List[InvoiceSummaryItem]
    total_count: int