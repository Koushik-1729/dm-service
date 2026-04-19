from datetime import datetime
from typing import Optional
from uuid import UUID


class User:
    """Represents an end-user in a business funnel."""

    def __init__(
        self,
        id: Optional[UUID] = None,
        client_id: Optional[UUID] = None,
        external_ref: Optional[str] = None,
        email: Optional[str] = None,
        phone_number: Optional[str] = None,
        first_name: Optional[str] = None,
        last_name: Optional[str] = None,
        status: str = "active",
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None,
    ):
        self.id = id
        self.client_id = client_id
        self.external_ref = external_ref
        self.email = email
        self.phone_number = phone_number
        self.first_name = first_name
        self.last_name = last_name
        self.status = status
        self.created_at = created_at
        self.updated_at = updated_at
