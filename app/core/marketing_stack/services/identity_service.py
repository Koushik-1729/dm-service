from typing import Dict, Optional
from uuid import uuid4

from app.core.marketing_stack.models.user import User
from app.core.marketing_stack.models.user_identity import UserIdentity
from app.core.marketing_stack.outbound.repositories.user_identity_repository import UserIdentityRepository
from app.core.marketing_stack.outbound.repositories.user_repository import UserRepository


class IdentityService:
    """Resolves and enriches end-user identities across journey events."""

    def __init__(
        self,
        user_repository: UserRepository,
        user_identity_repository: UserIdentityRepository,
    ):
        self._user_repo = user_repository
        self._identity_repo = user_identity_repository

    async def resolve_user(
        self,
        client_id,
        external_ref: Optional[str] = None,
        email: Optional[str] = None,
        phone_number: Optional[str] = None,
        first_name: Optional[str] = None,
        last_name: Optional[str] = None,
    ) -> User:
        candidates = [
            ("external_ref", external_ref),
            ("email", self._normalize_email(email)),
            ("phone_number", self._normalize_phone(phone_number)),
        ]

        user = None
        for identity_type, identity_value in candidates:
            if not identity_value:
                continue
            identity = await self._identity_repo.get_by_type_and_value(
                client_id=client_id,
                identity_type=identity_type,
                identity_value=identity_value,
            )
            if identity:
                user = await self._user_repo.get_by_id(identity.user_id)
                break

        if not user and external_ref:
            user = await self._user_repo.get_by_external_ref(client_id, external_ref)

        if not user:
            user = await self._user_repo.create(
                User(
                    id=uuid4(),
                    client_id=client_id,
                    external_ref=external_ref,
                    email=self._normalize_email(email),
                    phone_number=self._normalize_phone(phone_number),
                    first_name=first_name,
                    last_name=last_name,
                )
            )
        else:
            changed = False
            normalized_email = self._normalize_email(email)
            normalized_phone = self._normalize_phone(phone_number)
            if external_ref and not user.external_ref:
                user.external_ref = external_ref
                changed = True
            if normalized_email and not user.email:
                user.email = normalized_email
                changed = True
            if normalized_phone and not user.phone_number:
                user.phone_number = normalized_phone
                changed = True
            if first_name and not user.first_name:
                user.first_name = first_name
                changed = True
            if last_name and not user.last_name:
                user.last_name = last_name
                changed = True
            if changed:
                user = await self._user_repo.update(user)

        for identity_type, identity_value in candidates:
            if not identity_value:
                continue
            existing = await self._identity_repo.get_by_type_and_value(
                client_id=client_id,
                identity_type=identity_type,
                identity_value=identity_value,
            )
            if not existing:
                await self._identity_repo.create(
                    UserIdentity(
                        id=uuid4(),
                        client_id=client_id,
                        user_id=user.id,
                        identity_type=identity_type,
                        identity_value=identity_value,
                        is_primary=identity_type == "external_ref",
                    )
                )

        return user

    def _normalize_email(self, email: Optional[str]) -> Optional[str]:
        return email.strip().lower() if email else None

    def _normalize_phone(self, phone_number: Optional[str]) -> Optional[str]:
        if not phone_number:
            return None
        return "".join(char for char in phone_number if char.isdigit() or char == "+")
