from datetime import datetime
from typing import Optional
from uuid import UUID


class UserIdentity:
    """Represents a resolvable identity tied to a funnel user."""

    def __init__(
        self,
        id: Optional[UUID] = None,
        client_id: Optional[UUID] = None,
        user_id: Optional[UUID] = None,
        identity_type: str = "",
        identity_value: str = "",
        is_primary: bool = False,
        created_at: Optional[datetime] = None,
    ):
        self.id = id
        self.client_id = client_id
        self.user_id = user_id
        self.identity_type = identity_type
        self.identity_value = identity_value
        self.is_primary = is_primary
        self.created_at = created_at
