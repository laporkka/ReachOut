from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime
from src.models.campaign import StatusEnum

class CampaignCreate(BaseModel):
    template_id: int = Field(..., description="The unique database ID of the message template to send")
    target_tag: str = Field(..., description="The contact tag filter used to select recipients (e.g. 'VIP')")
    
    scheduled_at: datetime | None = Field(default=None, description="Optional execution timestamp. If empty, the campaign triggers instantly")


class CampaignResponse(BaseModel):
    id: int
    template_id: int  
    target_tag: str
    status: StatusEnum  
    total_recipients: int
    sent_successfully: int
    scheduled_at: datetime | None 
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)