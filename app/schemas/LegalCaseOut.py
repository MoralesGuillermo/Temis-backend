"""Modelo para retornar un LegalCase al Front"""
from typing import Annotated, Optional
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict
from app.schemas.ClientOut import ClientOut


class LegalCaseOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: Annotated[int, Field(gt=0)]
    start_date: datetime
    case_type: str
    client: ClientOut
    description: Annotated[str, Field(min_length=1, max_length=255)]
    notes: str
    title: Annotated[str, Field(min_length=1, max_length=100)]
    case_number: Optional[str]
    end_date: Optional[datetime]
    priority_level: str
    status: str

    
