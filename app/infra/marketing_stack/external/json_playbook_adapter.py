import json
import os
from typing import Dict, Any, List
from loguru import logger

from app.core.marketing_stack.outbound.external.playbook_loader_port import PlaybookLoaderPort


class JsonPlaybookAdapter(PlaybookLoaderPort):
    """Loads sector playbooks from JSON files in the playbooks/ directory."""

    def __init__(self, playbooks_dir: str = "playbooks"):
        self._playbooks_dir = playbooks_dir
        self._cache: Dict[str, Dict[str, Any]] = {}

    def load(self, sector: str) -> Dict[str, Any]:
        if sector in self._cache:
            return self._cache[sector]

        file_path = os.path.join(self._playbooks_dir, f"{sector}.json")

        if not os.path.exists(file_path):
            logger.warning(f"Playbook not found for sector '{sector}', falling back to 'general'")
            file_path = os.path.join(self._playbooks_dir, "general.json")

        if not os.path.exists(file_path):
            logger.error(f"General playbook not found at {file_path}")
            return self._minimal_playbook(sector)

        try:
            with open(file_path, "r") as f:
                playbook = json.load(f)
            self._cache[sector] = playbook
            logger.debug(f"Loaded playbook for sector '{sector}'")
            return playbook
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in playbook {file_path}: {e}")
            return self._minimal_playbook(sector)

    def list_sectors(self) -> List[str]:
        sectors = []
        if not os.path.isdir(self._playbooks_dir):
            return sectors
        for filename in os.listdir(self._playbooks_dir):
            if filename.endswith(".json"):
                sectors.append(filename.replace(".json", ""))
        return sorted(sectors)

    def _minimal_playbook(self, sector: str) -> Dict[str, Any]:
        return {
            "sector": sector,
            "channels": [
                {"name": "instagram", "priority": 1, "posts_per_week": 4},
                {"name": "whatsapp", "priority": 2, "messages_per_week": 2},
            ],
            "content_types": ["post", "reel_script", "campaign_message"],
            "posting_schedule": {
                "monday": {"channel": "instagram", "type": "post"},
                "wednesday": {"channel": "instagram", "type": "reel_script"},
                "friday": {"channel": "instagram", "type": "post"},
                "saturday": {"channel": "whatsapp", "type": "campaign_message"},
            },
            "cold_start_defaults": {
                "avg_cpc": 15,
                "avg_ctr": 2.5,
                "avg_conversion_rate": 0.15,
                "avg_order_value": 500,
            },
            "festivals": [],
        }
