"""Modelo para retornar un LegalCase al Front"""
from typing import Annotated, Optional
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict



class FileOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: Annotated[int, Field(gt=0)]
    upload_date: datetime
    file_name: Annotated[str, Field(min_length=1, max_length=255)]
    size_mb: Annotated[float, Field(gt=0)]