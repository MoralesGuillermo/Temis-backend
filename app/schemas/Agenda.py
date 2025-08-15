# app/schemas/AgendaCreate
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field, ConfigDict

class AgendaCreate(BaseModel):
    event_name: str = Field(..., min_length=1, max_length=40)
    description: str = Field(..., min_length=1)
    due_date: datetime  # ISO-8601 con TZ
    tags: List[str] = Field(default_factory=list)

# app/schemas/AgendaOut
class AgendaOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)  # pydantic v2

    id: int
    event_name: str
    description: str
    due_date: datetime
    tags: List[str]

# app/schemas/AgendaUpdate
class AgendaUpdate(BaseModel):
    event_name: Optional[str] = Field(None, min_length=1, max_length=40)
    description: Optional[str] = Field(None, min_length=1)
    due_date: Optional[datetime] = None            
    tags: Optional[List[str]] = None               