from abc import ABC, abstractmethod
from typing import Dict, Any, Optional


class AIProviderPort(ABC):
    """Abstract interface for AI generation (Claude, Gemini, etc.)."""

    @abstractmethod
    async def generate(
        self,
        system_prompt: str,
        user_prompt: str,
        max_tokens: int = 4096,
    ) -> str:
        """Generate text completion from the AI model."""
        pass

    @abstractmethod
    async def generate_structured(
        self,
        system_prompt: str,
        user_prompt: str,
        response_schema: Optional[Dict[str, Any]] = None,
        max_tokens: int = 4096,
    ) -> Dict[str, Any]:
        """Generate structured JSON output from the AI model."""
        pass
