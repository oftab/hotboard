import json
from typing import Optional
from .base import BaseAdapter
from ..models import AdapterConfig


class DoubanAdapter(BaseAdapter):
    name = "douban"
    platform = "豆瓣"

    def __init__(self, config: Optional[AdapterConfig] = None):
        super().__init__(config)
        self.api_url = "https://movie.douban.com/j/search_subjects?type=movie&tag=%E7%83%AD%E9%97%A8&page_limit=50&page_start=0"

    async def fetch(self) -> list[dict]:
        from ..core import Fetcher
        
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Referer": "https://movie.douban.com/",
        }
        async with Fetcher(timeout=self.config.timeout if self.config else 30) as fetcher:
            response = await fetcher.get(self.api_url, headers=headers)
            if not response:
                return []
            data = response.json()
            return data.get("subjects", [])

    def parse(self, raw_data: list[dict]) -> list:
        items = []
        for item in raw_data:
            try:
                title = item.get("title", "")
                url = item.get("url", "")
                rate = item.get("rate", "0")
                cover = item.get("cover", "")
                
                if title and url:
                    items.append(self._create_hot_item(
                        title=title,
                        url=url,
                        summary=f"豆瓣评分: {rate}",
                        hot_score=float(rate) * 10000 if rate else 0,
                        image_url=cover,
                        tags=["豆瓣", "电影"],
                    ))
            except Exception as e:
                self.logger.warning(f"Error parsing douban item: {e}")
        return items
