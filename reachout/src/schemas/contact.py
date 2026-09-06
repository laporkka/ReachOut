from pydantic import BaseModel, Field, EmailStr, ConfigDict
from typing import Annotated, List
from datetime import datetime


class ContactCreate(BaseModel):
    first_name: str = Field(..., max_length=50, description="Имя юзера")
    email: EmailStr = Field(..., description="email юзера")
    birthday: Annotated[str, Field(pattern="^\d{4}-\d{2}-\d{2}$")]
    tags: List[str] = Field(default_factory=list)


class ContactBulkUpload(BaseModel):
    items: List[ContactCreate]


class ContactResponse(BaseModel):
    id: int 
    first_name: str
    email: str
    birthday: str
    tags: List[str]
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)