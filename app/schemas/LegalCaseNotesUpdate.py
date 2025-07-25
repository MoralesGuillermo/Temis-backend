from typing import Annotated
from pydantic import BaseModel, Field


class LegalCaseNotesUpdate(BaseModel):
    id: Annotated[int, Field(gt=0)]
    notes: str
    
