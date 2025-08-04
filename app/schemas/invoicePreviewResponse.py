from typing import List
from pydantic import BaseModel
from app.schemas.enums import InvoiceStatus

class InvoiceItemPreview(BaseModel):
    name: str
    hours: int
    rate: float

class InvoicePreviewResponse(BaseModel):
    id: int
    client: str
    caseNumber: str
    amount: float
    issueDate: str
    dueDate: str
    status: InvoiceStatus
    items: List[InvoiceItemPreview]