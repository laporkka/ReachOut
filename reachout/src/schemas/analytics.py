from pydantic import BaseModel, ConfigDict


class AnalyticResponse(BaseModel):
    total_contacts: int
    total_campaigns: int 
    success_rate: float 

    model_config = ConfigDict(from_attributes=True)