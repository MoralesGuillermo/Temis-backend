from typing import Annotated
from pydantic import BaseModel, Field


class UserResponse(BaseModel):
    id: Annotated[int, Field(gt=0)]
    first_name: Annotated[str, Field(min_length=1, max_length=50)]
    last_name: Annotated[str, Field(min_length=1, max_length=50)]
    phone: Annotated[str, Field(min_length=1, max_length=20)]
    email: Annotated[str, Field(min_length=1, max_length=120)]
    
