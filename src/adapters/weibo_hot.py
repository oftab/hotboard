import json
from typing import Optional
from .base import BaseAdapter
from ..models import AdapterConfig


class WeiboHotAdapter(BaseAdapter):
    name = "weibo_hot"
    platform = "微博热搜"

    def __init__(self, config: Optional[AdapterConfig] = None):
        super().__init__(config)
        self.api_url = "https://weibo.com/ajax/side/hotSearch"

    async def fetch(self) -> list[dict]:
        from ..core import Fetcher
        
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Referer": "https://weibo.com/",
            "Cookie": "SUB=_2AkMRN5mwf8NxqwJRmP8RzG_iZZ11wwvEieKlDxZlJRMxHRl-yT9kqhEbtRB6PfFQZ-sv5qXZPzPXxV5D8xTQVvKzNnXh",
        }
        async with Fetcher(timeout=self.config.timeout if self.config else 30) as fetcher:
            response = await fetcher.get(self.api_url, headers=headers)
            if not response:
                return []
            data = response.json()
            return data.get("data", {}).get("realtime", [])

    def parse(self, raw_data: list[dict]) -> list:
        items = []
        for item in raw_data:
            try:
                title = item.get("word", "")
                hot_value = item.get("raw_hot", 0)
                url = f"https://s.weibo.com/weibo?q={title}"
                
                if title:
                    items.append(self._create_hot_item(
                        title=title,
                        url=url,
                        summary=f"微博热搜 - {title}",
                        hot_score=float(hot_value),
                        tags=["微博", "热搜"],
                    ))
            except Exception as e:
                self.logger.warning(f"Error parsing weibo_hot item: {e}")
        return items
