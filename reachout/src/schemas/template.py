from pydantic import BaseModel, Field, ConfigDict


class TemplateCreate(BaseModel):
    title: str = Field(..., max_length=50, description="Заголовок шаблона")
    body: str = Field(..., description="Рассылочное письмо")


class TemplateResponse(BaseModel):
    id: int
    manager_id: int
    title: str
    body: str

    model_config = ConfigDict(from_attributes=True)