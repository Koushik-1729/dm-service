from abc import ABC, abstractmethod
from datetime import date
from typing import List, Optional, Dict, Any
from uuid import UUID

from app.core.marketing_stack.models.daily_metrics import DailyMetrics


class MetricsRepository(ABC):
    """Abstract repository interface for DailyMetrics operations."""

    @abstractmethod
    async def upsert_daily(self, metrics: DailyMetrics) -> DailyMetrics:
        pass

    @abstractmethod
    async def get_range(
        self,
        client_id: UUID,
        start_date: date,
        end_date: date,
        channel: Optional[str] = None,
    ) -> List[DailyMetrics]:
        pass

    @abstractmethod
    async def get_latest(self, client_id: UUID) -> Optional[DailyMetrics]:
        pass

    @abstractmethod
    async def get_summary(self, client_id: UUID, days: int = 7) -> Dict[str, Any]:
        pass
