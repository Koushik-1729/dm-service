from abc import ABC, abstractmethod
from typing import List, Optional
from uuid import UUID

from app.core.marketing_stack.models.user_identity import UserIdentity


class UserIdentityRepository(ABC):
    @abstractmethod
    async def create(self, identity: UserIdentity) -> UserIdentity:
        pass

    @abstractmethod
    async def get_by_type_and_value(
        self,
        client_id: UUID,
        identity_type: str,
        identity_value: str,
    ) -> Optional[UserIdentity]:
        pass

    @abstractmethod
    async def list_by_user(self, user_id: UUID) -> List[UserIdentity]:
        pass
