import json
from typing import Optional
from .base import BaseAdapter
from ..models import AdapterConfig


class SspaiAdapter(BaseAdapter):
    name = "sspai"
    platform = "少数派"

    def __init__(self, config: Optional[AdapterConfig] = None):
        super().__init__(config)
        self.api_url = "https://sspai.com/api/v1/article?limit=30&offset=0&type=home"

    async def fetch(self) -> list[dict]:
        from ..core import Fetcher
        
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Referer": "https://sspai.com/",
        }
        async with Fetcher(timeout=self.config.timeout if self.config else 30) as fetcher:
            response = await fetcher.get(self.api_url, headers=headers)
            if not response:
                return []
            data = response.json()
            return data.get("data", [])

    def parse(self, raw_data: list[dict]) -> list:
        items = []
        for item in raw_data:
            try:
                title = item.get("title", "")
                article_id = item.get("id", "")
                url = f"https://sspai.com/post/{article_id}" if article_id else ""
                summary = item.get("summary", "")
                hot_score = item.get("like_count", 0) + item.get("view_count", 0)
                
                if title and url:
                    items.append(self._create_hot_item(
                        title=title,
                        url=url,
                        summary=summary[:100] if summary else title,
                        hot_score=float(hot_score),
                        tags=["少数派", "科技"],
                    ))
            except Exception as e:
                self.logger.warning(f"Error parsing sspai item: {e}")
        return items
