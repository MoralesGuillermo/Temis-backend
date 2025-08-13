"""Modelo para retornar un LegalCase al Front"""
from typing import Annotated, Optional
from pydantic import BaseModel, Field


class ClientOut(BaseModel):
    id: Annotated[int, Field(gt=0)]
    first_name: Annotated[str, Field(min_length=1, max_length=255)]
    last_name: Annotated[str, Field(min_length=1, max_length=255)]
    phone_1: Annotated[str, Field(min_length=1, max_length=50)]
    phone_2: Optional[str]
    email: Annotated[str, Field(min_length=1, max_length=255)]
    dni: Annotated[str, Field(min_length=1, max_length=50)]
    address: str

    
