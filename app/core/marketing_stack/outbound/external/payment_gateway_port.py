from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from decimal import Decimal


class PaymentGatewayPort(ABC):
    """Abstract interface for payment processing (Razorpay). Phase 2."""

    @abstractmethod
    async def create_subscription(
        self,
        plan_id: str,
        customer_phone: str,
        customer_name: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Create a recurring subscription. Returns subscription details."""
        pass

    @abstractmethod
    async def create_payment_link(
        self,
        amount: Decimal,
        description: str,
        customer_phone: str,
        reference_id: Optional[str] = None,
    ) -> str:
        """Create a payment link for one-time payment. Returns payment link URL."""
        pass

    @abstractmethod
    async def get_payment_status(self, payment_id: str) -> Dict[str, Any]:
        """Get the status of a payment."""
        pass

    @abstractmethod
    async def cancel_subscription(self, subscription_id: str) -> bool:
        """Cancel a subscription."""
        pass
