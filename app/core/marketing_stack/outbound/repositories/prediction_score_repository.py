from abc import ABC, abstractmethod
from typing import List, Optional
from uuid import UUID

from app.core.marketing_stack.models.prediction_score import PredictionScore


class PredictionScoreRepository(ABC):
    @abstractmethod
    async def create(self, prediction: PredictionScore) -> PredictionScore:
        pass

    @abstractmethod
    async def get_latest_by_user(self, user_id: UUID) -> Optional[PredictionScore]:
        pass

    @abstractmethod
    async def list_latest_by_client(self, client_id: UUID, limit: int = 100) -> List[PredictionScore]:
        pass
