"""Modelo para retornar un LegalCase al Front"""
from typing import Annotated, Optional
from datetime import datetime
from pydantic import BaseModel, Field, EmailStr

from app.database.enums import CaseTypeEnum


class NewCaseData(BaseModel):
    class NewClient(BaseModel):
        first_name: str
        last_name: str
        phone_1: str
        email: EmailStr
        dni: str
        addresss: str

    title: Annotated[str, Field(min_length=1, max_length=100)]
    start_date: datetime
    case_type: Annotated[CaseTypeEnum, "Tipo de caso"]
    # plaintiff: str
    # defendant: str
    description: Optional[str]
    notes: Optional[str]
    client_id: Optional[int] = None
    client: Optional[NewClient] = None
