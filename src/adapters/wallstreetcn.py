import json
from typing import Optional
from .base import BaseAdapter
from ..models import AdapterConfig


class WallstreetcnAdapter(BaseAdapter):
    name = "wallstreetcn"
    platform = "华尔街见闻"

    def __init__(self, config: Optional[AdapterConfig] = None):
        super().__init__(config)
        self.api_url = "https://api-one.wallstcn.com/apiv1/content/articles/hot"

    async def fetch(self) -> list[dict]:
        from ..core import Fetcher
        
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Referer": "https://wallstreetcn.com/",
        }
        async with Fetcher(timeout=self.config.timeout if self.config else 30) as fetcher:
            response = await fetcher.get(self.api_url, headers=headers)
            if not response:
                return []
            data = response.json()
            return data.get("data", {}).get("items", [])

    def parse(self, raw_data: list[dict]) -> list:
        items = []
        for item in raw_data:
            try:
                title = item.get("title", "")
                item_id = item.get("id", "")
                url = f"https://wallstreetcn.com/articles/{item_id}" if item_id else ""
                summary = item.get("content_short", "")
                hot_score = item.get("like_count", 0) + item.get("comment_count", 0) * 5
                
                if title and url:
                    items.append(self._create_hot_item(
                        title=title,
                        url=url,
                        summary=summary[:100] if summary else title,
                        hot_score=float(hot_score),
                        tags=["华尔街见闻", "财经"],
                    ))
            except Exception as e:
                self.logger.warning(f"Error parsing wallstreetcn item: {e}")
        return items
