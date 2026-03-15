import json
from typing import Optional
from .base import BaseAdapter
from ..models import AdapterConfig


class QqnewsAdapter(BaseAdapter):
    name = "qqnews"
    platform = "腾讯新闻"

    def __init__(self, config: Optional[AdapterConfig] = None):
        super().__init__(config)
        self.api_url = "https://i.news.qq.com/gw/pc_hot_list"

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
                return data.get("data", {}).get("list", [])
            except:
                return []

    def parse(self, raw_data: list[dict]) -> list:
        items = []
        for i, item in enumerate(raw_data):
            try:
                title = item.get("title", "")
                url = item.get("url", "")
                hot_score = float(item.get("hot_value", 0) or 0)
                
                if title:
                    items.append(self._create_hot_item(
                        title=title,
                        url=url,
                        summary=item.get("desc", title)[:100],
                        hot_score=hot_score + 100 - i,
                        tags=["腾讯新闻", "新闻"],
                    ))
            except Exception as e:
                self.logger.warning(f"Error parsing qqnews item: {e}")
        return items
