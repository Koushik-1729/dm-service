from pydantic import BaseModel, ConfigDict
from typing import Optional, List
from uuid import UUID
from datetime import datetime


class ContentResponse(BaseModel):
    id: UUID
    client_id: UUID
    channel: str
    content_type: str
    variant_group: Optional[str] = None
    variant_label: str
    caption: str
    media_url: Optional[str] = None
    hashtags: List[str] = []
    cta_text: Optional[str] = None
    risk_level: str
    status: str
    scheduled_for: Optional[datetime] = None
    published_at: Optional[datetime] = None
    created_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class ContentListResponse(BaseModel):
    data: List[ContentResponse]
    total: int


class ContentApproveRequest(BaseModel):
    content_ids: List[UUID]
