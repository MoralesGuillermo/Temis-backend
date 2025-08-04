from pydantic import BaseModel
from app.database.enums import InvoiceStatusEnum

class InvoiceUpdateRequest(BaseModel):
    id: int
    status: InvoiceStatusEnum

class InvoiceUpdateResponse(BaseModel):
    id: int
    status: InvoiceStatusEnum
    message: str