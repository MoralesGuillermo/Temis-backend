"""Modelo para retornar un LegalCase al Front"""
from typing import Annotated, Optional
from datetime import datetime
from pydantic import BaseModel, Field


class FileOut(BaseModel):
    id: Annotated[int, Field(gt=0)]
    upload_date: datetime
    file_name: Annotated[str, Field(min_length=1, max_length=255)]
    size_mb: Annotated[float, Field(gt=0)]