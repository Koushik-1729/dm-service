from abc import ABC, abstractmethod
from typing import Dict, Any, Optional


class VideoGeneratorPort(ABC):
    """Abstract interface for video/reel generation (Creatomate, Shotstack). Phase 2."""

    @abstractmethod
    async def generate_from_template(
        self,
        template_id: str,
        modifications: Dict[str, Any],
    ) -> str:
        """Generate a video from a template with modifications. Returns video URL."""
        pass

    @abstractmethod
    async def get_render_status(self, render_id: str) -> Dict[str, Any]:
        """Check the status of a video render job."""
        pass
