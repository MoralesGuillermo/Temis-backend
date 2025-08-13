"""Modelo para retornar un LegalCase al Front"""
from typing import Annotated, Optional
from datetime import datetime
from pydantic import BaseModel, Field


class LegalCaseOut(BaseModel):
    id: Annotated[int, Field(gt=0)]
    start_date: datetime
    case_type: str
    client_id: Annotated[int, Field(gt=0)]
    description: Annotated[str, Field(min_length=1, max_length=255)]
    notes: str
    title: Annotated[str, Field(min_length=1, max_length=100)]
    case_number: Optional[str]
    end_date: Optional[datetime]
    priority_level: str
    status: str

    class Config:
        from_attributes = True

    
