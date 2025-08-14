from typing import List, Union
from pydantic import BaseModel
from datetime import date

class InvoiceItemResponse(BaseModel):
    name: str
    hours: int
    rate: float

class InvoiceResponse(BaseModel):
    id: int
    client: str
    client_email: str
    case_number: str
    issue_date: str
    due_date: str
    status: str
    amount: Union[int, float]
    items: List[InvoiceItemResponse]