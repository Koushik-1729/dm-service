from datetime import datetime
from typing import Optional, Dict, Any, List
from uuid import UUID


class Strategy:
    """Domain model representing a monthly marketing strategy."""

    def __init__(
        self,
        id: Optional[UUID] = None,
        client_id: Optional[UUID] = None,
        version: int = 1,
        channels: Optional[List[Dict[str, Any]]] = None,
        content_calendar: Optional[List[Dict[str, Any]]] = None,
        kpis: Optional[Dict[str, Any]] = None,
        budget_allocation: Optional[Dict[str, Any]] = None,
        festival_campaigns: Optional[List[Dict[str, Any]]] = None,
        playbook_id: Optional[str] = None,
        ai_reasoning: Optional[str] = None,
        status: str = "draft",
        created_at: Optional[datetime] = None,
    ):
        self.id = id
        self.client_id = client_id
        self.version = version
        self.channels = channels or []
        self.content_calendar = content_calendar or []
        self.kpis = kpis or {}
        self.budget_allocation = budget_allocation or {}
        self.festival_campaigns = festival_campaigns or []
        self.playbook_id = playbook_id
        self.ai_reasoning = ai_reasoning
        self.status = status
        self.created_at = created_at

    def approve(self) -> None:
        self.status = "active"

    def archive(self) -> None:
        self.status = "archived"

    def get_active_channels(self) -> List[str]:
        return [ch["name"] for ch in self.channels if ch.get("active", True)]
