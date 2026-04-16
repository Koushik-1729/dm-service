from pydantic import BaseModel, ConfigDict
from typing import Optional, Dict, Any, List
from uuid import UUID
from datetime import datetime


class ClientResponse(BaseModel):
    id: UUID
    phone_number: str
    business_name: Optional[str] = None
    owner_name: Optional[str] = None
    sector: Optional[str] = None
    city: Optional[str] = None
    locality: Optional[str] = None
    language: str = "english"
    onboarding_status: str
    subscription_tier: str
    autonomy_level: str
    is_active: bool
    created_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class ClientListResponse(BaseModel):
    data: List[ClientResponse]
    total: int
