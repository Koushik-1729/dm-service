from pydantic import BaseModel, ConfigDict
from typing import Optional, Dict, Any, List
from uuid import UUID
from datetime import datetime


class StrategyResponse(BaseModel):
    id: UUID
    client_id: UUID
    version: int
    channels: List[Dict[str, Any]]
    content_calendar: List[Dict[str, Any]]
    kpis: Dict[str, Any]
    budget_allocation: Dict[str, Any]
    playbook_id: Optional[str] = None
    ai_reasoning: Optional[str] = None
    status: str
    created_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class StrategyGenerateRequest(BaseModel):
    client_id: UUID
    feedback: Optional[str] = None
