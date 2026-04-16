from abc import ABC, abstractmethod
from typing import Dict, Any, List


class PlaybookLoaderPort(ABC):
    """Abstract interface for loading sector-specific marketing playbooks."""

    @abstractmethod
    def load(self, sector: str) -> Dict[str, Any]:
        """Load the playbook configuration for a given business sector."""
        pass

    @abstractmethod
    def list_sectors(self) -> List[str]:
        """List all available sector playbook IDs."""
        pass
