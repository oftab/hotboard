import json
from typing import Optional
from .base import BaseAdapter
from ..models import AdapterConfig


class V2exAdapter(BaseAdapter):
    name = "v2ex"
    platform = "V2EX"

    def __init__(self, config: Optional[AdapterConfig] = None):
        super().__init__(config)
        self.api_url = "https://www.v2ex.com/api/topics/hot.json"

    async def fetch(self) -> list[dict]:
        from ..core import Fetcher
        
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        }
        async with Fetcher(timeout=self.config.timeout if self.config else 30) as fetcher:
            response = await fetcher.get(self.api_url, headers=headers)
            if not response:
                return []
            return response.json()

    def parse(self, raw_data: list[dict]) -> list:
        items = []
        for item in raw_data:
            try:
                title = item.get("title", "")
                url = item.get("url", "")
                content = item.get("content", "")
                replies = item.get("replies", 0)
                node = item.get("node", {}).get("name", "")
                
                if title and url:
                    items.append(self._create_hot_item(
                        title=title,
                        url=url,
                        summary=content[:100] if content else title,
                        hot_score=float(replies * 10),
                        tags=["V2EX", node] if node else ["V2EX"],
                    ))
            except Exception as e:
                self.logger.warning(f"Error parsing v2ex item: {e}")
        return items
