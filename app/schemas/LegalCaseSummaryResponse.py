from typing import List
from pydantic import BaseModel

class LegalCaseSummaryItem(BaseModel):
    id: int
    title: str
    case_number: str
    case_type: str
    status: str
    client_name: str
    start_date: str
    
class LegalCaseSummaryResponse(BaseModel):
    cases: List[LegalCaseSummaryItem]
    total_count: int