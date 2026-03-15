import json
from typing import Optional
from .base import BaseAdapter
from ..models import AdapterConfig


class HellogithubAdapter(BaseAdapter):
    name = "hellogithub"
    platform = "HelloGitHub"

    def __init__(self, config: Optional[AdapterConfig] = None):
        super().__init__(config)
        self.api_url = "https://hellogithub.com/v1/api/volume/"

    async def fetch(self) -> list[dict]:
        from ..core import Fetcher
        
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "application/json",
        }
        async with Fetcher(timeout=self.config.timeout if self.config else 30) as fetcher:
            response = await fetcher.get(self.api_url, headers=headers)
            if not response:
                return []
            try:
                data = response.json()
                return data.get("data", {}).get("items", [])
            except:
                return []

    def parse(self, raw_data: list[dict]) -> list:
        items = []
        for i, item in enumerate(raw_data):
            try:
                title = item.get("title", "")
                url = item.get("url", "")
                hot_score = float(item.get("star", 0) or 0)
                
                if title:
                    items.append(self._create_hot_item(
                        title=title,
                        url=url,
                        summary=item.get("summary", title)[:100],
                        hot_score=hot_score + 100 - i,
                        tags=["HelloGitHub", "开源"],
                    ))
            except Exception as e:
                self.logger.warning(f"Error parsing hellogithub item: {e}")
        return items
