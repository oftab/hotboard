import json
from typing import Optional
from .base import BaseAdapter
from ..models import AdapterConfig


class DiggAdapter(BaseAdapter):
    name = "digg"
    platform = "Digg"

    def __init__(self, config: Optional[AdapterConfig] = None):
        super().__init__(config)
        self.api_url = "https://digg.com/api/v2/digg/story/list"

    async def fetch(self) -> list[dict]:
        from ..core import Fetcher
        
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        }
        async with Fetcher(timeout=self.config.timeout if self.config else 30) as fetcher:
            response = await fetcher.get(self.api_url, headers=headers)
            if not response:
                return []
            data = response.json()
            return data.get("data", {}).get("feed", [])

    def parse(self, raw_data: list[dict]) -> list:
        items = []
        for item in raw_data:
            try:
                title = item.get("title", "")
                url = item.get("url", "")
                description = item.get("description", "")
                diggs = item.get("digg_score", 0)
                
                if title and url:
                    items.append(self._create_hot_item(
                        title=title,
                        url=url,
                        summary=description or title,
                        hot_score=float(diggs),
                        tags=["Digg", "新闻"],
                    ))
            except Exception as e:
                self.logger.warning(f"Error parsing digg item: {e}")
        return items
