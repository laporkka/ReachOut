from pydantic import BaseModel, EmailStr, Field


class ManagerCreate(BaseModel):
    email: EmailStr = Field(..., description="Твой email")
    password: str = Field(...,min_length=8, max_length=50, description="Твой пароль")


class ManagerResponse(BaseModel):
    id: int
    email: EmailStr

    model_config = {"from_attributes": True}


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"